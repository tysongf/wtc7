/* Explicit shell kernel for wtc7.xfe, the Phase 1 detailed (shell) model.
 *
 * Element: Belytschko-Lin-Tsay four-node shell (Belytschko, Lin and Tsay 1984, as
 * given in the LS-DYNA Theory Manual): co-rotational local frame, one-point in-plane
 * quadrature, NIP Gauss points through the thickness, transverse shear with factor
 * kappa, Flanagan-Belytschko stiffness hourglass control (membrane, bending and
 * transverse modes).
 * Material: plane-stress J2 plasticity with isotropic hardening on tabulated,
 * temperature-dependent flow curves (return map of Simo and Taylor 1986); E(T) and
 * the thermal strain are tabulated. Stresses are kept in the element frame.
 * Also here: nodal force gather, central-difference update with mass-proportional
 * damping, penalty contact with Coulomb friction (rigid bounded planes; nodes or
 * fixed points against shell surfaces), and breakable bolt and stud springs.
 *
 * Units: kip, in., s, C. Node arrays are (nn, 3) or (nn, 6) row-major doubles.
 * "fint" holds internal minus external (contact, spring) forces: the update uses
 * a = (lambda * fpat - fint) / m.
 */
#include <math.h>
#include <string.h>

typedef struct {
    int nmat, nT, nep;
    double T0, dT;
    const double *E;     /* nmat*nT, ksi */
    const double *eth;   /* nmat*nT, thermal strain from 20 C */
    const double *ep;    /* nmat*nep, plastic-strain grid, increasing, ep[0] = 0 */
    const double *sy;    /* nmat*nT*nep, flow stress, ksi (compression curve for kind 2) */
    const double *nu;    /* nmat */
    const int *kind;     /* nmat: 0 = J2 tabulated, 1 = elastic, 2 = J2 with separate tension and
                            compression curves chosen by the sign of the trial mean stress
                            (LS-DYNA MAT_124 idea, used by NIST for the composite slab) */
    const double *syt;   /* nmat*nT*nep, tension flow curve (kind 2) */
} Mat;

static const double XI_I[4] = {-1.0, 1.0, 1.0, -1.0};
static const double ETA_I[4] = {-1.0, -1.0, 1.0, 1.0};
static const double HG_H[4] = {1.0, -1.0, 1.0, -1.0};

static inline void cross(const double *a, const double *b, double *c)
{
    c[0] = a[1] * b[2] - a[2] * b[1];
    c[1] = a[2] * b[0] - a[0] * b[2];
    c[2] = a[0] * b[1] - a[1] * b[0];
}

static inline double dot(const double *a, const double *b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

static inline void normalize(double *a)
{
    double n = sqrt(dot(a, a));
    if (n > 0) { a[0] /= n; a[1] /= n; a[2] /= n; }
}

static inline void tindex(const Mat *m, double T, int *i, double *w)
{
    double s = (T - m->T0) / m->dT;
    if (s <= 0.0) { *i = 0; *w = 0.0; return; }
    if (s >= m->nT - 1) { *i = m->nT - 2; *w = 1.0; return; }
    *i = (int)s;
    *w = s - *i;
}

static inline double tab_T(const Mat *m, const double *a, int k, double T)
{
    int i; double w;
    tindex(m, T, &i, &w);
    const double *r = a + (size_t)k * m->nT;
    return r[i] * (1.0 - w) + r[i + 1] * w;
}

/* flow stress and hardening slope at plastic strain ep, temperature T, material k */
static void flow(const Mat *m, int k, double T, double ep, double *sy, double *H, int tens)
{
    int it; double wt;
    tindex(m, T, &it, &wt);
    const int n = m->nep;
    const double *g = m->ep + (size_t)k * n;
    const double *tab = tens ? m->syt : m->sy;
    int j; double we; int flat = 0;
    if (ep <= g[0]) { j = 0; we = 0.0; }
    else if (ep >= g[n - 1]) { j = n - 2; we = 1.0; flat = 1; }
    else {
        int lo = 0, hi = n - 1;
        while (hi - lo > 1) { int mid = (lo + hi) >> 1; if (g[mid] <= ep) lo = mid; else hi = mid; }
        j = lo; we = (ep - g[j]) / (g[j + 1] - g[j]);
    }
    const double *s0 = tab + ((size_t)k * m->nT + it) * n;
    const double *s1 = s0 + n;
    double a = s0[j] + we * (s0[j + 1] - s0[j]);
    double b = s1[j] + we * (s1[j + 1] - s1[j]);
    *sy = a * (1.0 - wt) + b * wt;
    if (flat) { *H = 0.0; return; }
    double dg = g[j + 1] - g[j];
    *H = ((s0[j + 1] - s0[j]) * (1.0 - wt) + (s1[j + 1] - s1[j]) * wt) / dg;
}

/* Plane-stress J2 return map. s = trial (sxx, syy, sxy) in, corrected out.
 * Returns the equivalent plastic strain increment. */
static double return_map(const Mat *m, int k, double T, double E, double nu, double ep0, double *s, int tens)
{
    const double r2 = 0.70710678118654752440;
    double a1 = (s[0] + s[1]) * r2, a2 = (s[1] - s[0]) * r2, a3 = s[2];
    double c1 = E / (3.0 * (1.0 - nu)), c2 = E / (1.0 + nu);
    double p2 = a1 * a1 / 3.0 + a2 * a2 + 2.0 * a3 * a3;
    double se = sqrt(1.5 * p2);
    double sy, H;
    flow(m, k, T, ep0, &sy, &H, tens);
    if (se <= sy) return 0.0;
    double lo = 0.0, hi = -1.0;
    double g = (se - sy) / (se * (c2 + 2.0 * H / 3.0 > 0.1 * c2 ? c2 + 2.0 * H / 3.0 : 0.1 * c2));
    double dep = 0.0;
    for (int it = 0; it < 60; ++it) {
        double d1 = 1.0 + c1 * g, d2 = 1.0 + c2 * g;
        double A1 = a1 / d1, A2 = a2 / d2, A3 = a3 / d2;
        double q2 = A1 * A1 / 3.0 + A2 * A2 + 2.0 * A3 * A3;
        double sq = sqrt(1.5 * q2);
        dep = 2.0 / 3.0 * g * sq;
        flow(m, k, T, ep0 + dep, &sy, &H, tens);
        double F = sq - sy;
        if (fabs(F) <= 1e-10 * (sy + 1.0)) break;
        if (F > 0.0) lo = g; else hi = g;
        double dq2 = -2.0 / 3.0 * a1 * a1 * c1 / (d1 * d1 * d1) - 2.0 * (a2 * a2 + 2.0 * a3 * a3) * c2 / (d2 * d2 * d2);
        double dsq = 0.75 * dq2 / (sq > 1e-30 ? sq : 1e-30);
        double dF = dsq - H * 2.0 / 3.0 * (sq + g * dsq);
        double gn = (dF < 0.0) ? g - F / dF : -1.0;
        if (!(gn > lo) || (hi >= 0.0 && !(gn < hi))) gn = (hi >= 0.0) ? 0.5 * (lo + hi) : 2.0 * (g > 0.0 ? g : 1e-12);
        g = gn;
    }
    double d1 = 1.0 + c1 * g, d2 = 1.0 + c2 * g;
    double A1 = a1 / d1, A2 = a2 / d2;
    s[0] = (A1 - A2) * r2;
    s[1] = (A1 + A2) * r2;
    s[2] = a3 / d2;
    return dep;
}

/* stress update at one integration point with precomputed E0 = E(T_prev), E1 = E(T_now),
 * Poisson ratio and thermal strain increment; returns the plastic strain increment */
static inline double stress_point(const Mat *m, int k, double T1, double E0, double E1, double nu, double dth,
                                  double symin2, double symin2_t, const double *de, double *s, double ep0)
{
    double r = E1 / E0, c = E1 / (1.0 - nu * nu);
    double d0 = de[0] - dth, d1 = de[1] - dth, d2 = de[2];
    s[0] = r * s[0] + c * (d0 + nu * d1);
    s[1] = r * s[1] + c * (nu * d0 + d1);
    s[2] = r * s[2] + c * 0.5 * (1.0 - nu) * d2;
    if (m->kind[k] == 1) return 0.0;
    /* von Mises squared below the lowest flow stress at this temperature: elastic, no table search */
    double se2 = s[0] * s[0] + s[1] * s[1] - s[0] * s[1] + 3.0 * s[2] * s[2];
    int tens = (m->kind[k] == 2) && (s[0] + s[1] > 0.0);
    if (se2 <= (tens ? symin2_t : symin2)) return 0.0;
    return return_map(m, k, T1, E1, nu, ep0, s, tens);
}

/* lowest flow stress over the plastic-strain grid at temperature T (elastic-check bound) */
static double flow_min(const Mat *m, int k, double T, int tens)
{
    int it; double wt;
    tindex(m, T, &it, &wt);
    const int n = m->nep;
    double lo = 1e300;
    for (int tab = tens; tab <= tens; ++tab) {
        const double *s0 = (tab ? m->syt : m->sy) + ((size_t)k * m->nT + it) * n, *s1 = s0 + n;
        for (int j = 0; j < n; ++j) {
            double v = s0[j] * (1.0 - wt) + s1[j] * wt;
            if (v < lo) lo = v;
        }
    }
    return lo;
}

/* single integration-point update for the tests (same code path as shell_forces) */
double stress_update(const Mat *m, int k, double T0, double T1, const double *de, double *s, double ep0)
{
    double E0 = tab_T(m, m->E, k, T0), E1 = tab_T(m, m->E, k, T1);
    double dth = tab_T(m, m->eth, k, T1) - tab_T(m, m->eth, k, T0);
    double fm = flow_min(m, k, T1, 0), ft = (m->kind[k] == 2) ? flow_min(m, k, T1, 1) : fm;
    return stress_point(m, k, T1, E0, E1, m->nu[k], dth, fm * fm * (1.0 - 1e-12), ft * ft * (1.0 - 1e-12), de, s, ep0);
}

static void frame(const double X[4][3], double *e1, double *e2, double *e3, double *xc)
{
    double r31[3], r42[3], r21[3];
    for (int k = 0; k < 3; ++k) {
        r31[k] = X[2][k] - X[0][k];
        r42[k] = X[3][k] - X[1][k];
        r21[k] = X[1][k] - X[0][k];
        xc[k] = 0.25 * (X[0][k] + X[1][k] + X[2][k] + X[3][k]);
    }
    cross(r31, r42, e3);
    normalize(e3);
    double p = dot(r21, e3);
    for (int k = 0; k < 3; ++k) e1[k] = r21[k] - p * e3[k];
    normalize(e1);
    cross(e3, e1, e2);
}

/* Internal forces of all shell elements. fe: nel*24 (per node fx fy fz mx my mz, global).
 * energy[0] += internal (elastic + plastic) work on mechanical strain, energy[1] += hourglass
 * work, energy[2] += plastic dissipation estimate, energy[3] += work of thermal strain
 * against stress (energy input from restrained expansion, -sigma : d eps_th). */
void shell_forces(int nel, const int *conn, const double *h, const int *mat, const int *tg,
                  const double *x, const double *v, const double *w, double dt,
                  const double *Tnow, const double *Tprev, const Mat *M,
                  int nip, const double *zeta, const double *wz, double qhg, double kappa,
                  double *sig, double *epsp, double *qs, double *hgs, double *fe, double *energy)
{
    double eIE = 0.0, eHG = 0.0, ePL = 0.0, eTH = 0.0;
    /* elastic-check bound per (material, temperature group), squared */
    enum { MAXM = 16, MAXG = 16 };
    double bound2[MAXM][MAXG], bound2t[MAXM][MAXG];
    double Ecur[MAXM][MAXG], Eold[MAXM][MAXG], dthm[MAXM][MAXG];
    int ng = 0;
    for (int e = 0; e < nel; ++e) if (tg[e] + 1 > ng) ng = tg[e] + 1;
    for (int k = 0; k < M->nmat && k < MAXM; ++k)
        for (int g = 0; g < ng && g < MAXG; ++g) {
            double fm = flow_min(M, k, Tnow[g], 0);
            double ftm = (M->kind[k] == 2) ? flow_min(M, k, Tnow[g], 1) : fm;
            bound2[k][g] = fm * fm * (1.0 - 1e-12);
            bound2t[k][g] = ftm * ftm * (1.0 - 1e-12);
            Ecur[k][g] = tab_T(M, M->E, k, Tnow[g]);
            Eold[k][g] = tab_T(M, M->E, k, Tprev[g]);
            dthm[k][g] = tab_T(M, M->eth, k, Tnow[g]) - tab_T(M, M->eth, k, Tprev[g]);
        }
#pragma omp parallel for schedule(static) reduction(+ : eIE, eHG, ePL, eTH)
    for (int e = 0; e < nel; ++e) {
        const int *nd = conn + 4 * e;
        double X[4][3], V[4][3], W[4][3];
        for (int I = 0; I < 4; ++I)
            for (int k = 0; k < 3; ++k) {
                X[I][k] = x[3 * nd[I] + k];
                V[I][k] = v[3 * nd[I] + k];
                W[I][k] = w[3 * nd[I] + k];
            }
        double e1[3], e2[3], e3[3], xc[3];
        frame(X, e1, e2, e3, xc);
        double xl[4], yl[4], vl[4][3], wl[4][2];
        for (int I = 0; I < 4; ++I) {
            double d[3] = {X[I][0] - xc[0], X[I][1] - xc[1], X[I][2] - xc[2]};
            xl[I] = dot(d, e1);
            yl[I] = dot(d, e2);
            vl[I][0] = dot(V[I], e1);
            vl[I][1] = dot(V[I], e2);
            vl[I][2] = dot(V[I], e3);
            wl[I][0] = dot(W[I], e1);
            wl[I][1] = dot(W[I], e2);
        }
        double a2 = (xl[2] - xl[0]) * (yl[3] - yl[1]) + (xl[1] - xl[3]) * (yl[2] - yl[0]);
        double A = 0.5 * a2;
        double B1[4] = {(yl[1] - yl[3]) / a2, (yl[2] - yl[0]) / a2, (yl[3] - yl[1]) / a2, (yl[0] - yl[2]) / a2};
        double B2[4] = {(xl[3] - xl[1]) / a2, (xl[0] - xl[2]) / a2, (xl[1] - xl[3]) / a2, (xl[2] - xl[0]) / a2};
        double dmx = 0, dmy = 0, dmxy = 0, kx = 0, ky = 0, kxy = 0, vz1 = 0, vz2 = 0, wxa = 0, wya = 0;
        for (int I = 0; I < 4; ++I) {
            dmx += B1[I] * vl[I][0];
            dmy += B2[I] * vl[I][1];
            dmxy += B2[I] * vl[I][0] + B1[I] * vl[I][1];
            kx += B1[I] * wl[I][1];
            ky -= B2[I] * wl[I][0];
            kxy += B2[I] * wl[I][1] - B1[I] * wl[I][0];
            vz1 += B1[I] * vl[I][2];
            vz2 += B2[I] * vl[I][2];
            wxa += 0.25 * wl[I][0];
            wya += 0.25 * wl[I][1];
        }
        double gxz = vz1 + wya, gyz = vz2 - wxa;
        const int km = mat[e], gk = tg[e];
        const double T1 = Tnow[gk];
        const double E0 = Eold[km][gk], E1 = Ecur[km][gk], nu = M->nu[km];
        const double ratio = E1 / E0;
        const double dth = dthm[km][gk];
        const double sb2 = bound2[km][gk], sb2t = bound2t[km][gk];
        const double hh = h[e];
        double Nxx = 0, Nyy = 0, Nxy = 0, Mxx = 0, Myy = 0, Mxy = 0;
        for (int ip = 0; ip < nip; ++ip) {
            double z = 0.5 * hh * zeta[ip], wt = 0.5 * hh * wz[ip];
            double de[3] = {(dmx + z * kx) * dt, (dmy + z * ky) * dt, (dmxy + z * kxy) * dt};
            double *s = sig + ((size_t)e * nip + ip) * 3;
            double so[3] = {s[0], s[1], s[2]};
            double *ep = epsp + (size_t)e * nip + ip;
            double dep = stress_point(M, km, T1, E0, E1, nu, dth, sb2, sb2t, de, s, *ep);
            *ep += dep;
            eIE += 0.5 * ((so[0] + s[0]) * (de[0] - dth) + (so[1] + s[1]) * (de[1] - dth) + (so[2] + s[2]) * de[2]) * wt * A;
            eTH -= 0.5 * (so[0] + s[0] + so[1] + s[1]) * dth * wt * A;
            ePL += dep * sqrt(s[0] * s[0] + s[1] * s[1] - s[0] * s[1] + 3.0 * s[2] * s[2]) * wt * A;
            Nxx += wt * s[0];
            Nyy += wt * s[1];
            Nxy += wt * s[2];
            Mxx -= wt * z * s[0];
            Myy -= wt * z * s[1];
            Mxy -= wt * z * s[2];
        }
        const double G1 = E1 / (2.0 * (1.0 + nu));
        double *q = qs + 2 * (size_t)e;
        double qo0 = q[0], qo1 = q[1];
        q[0] = ratio * q[0] + kappa * G1 * hh * gxz * dt;
        q[1] = ratio * q[1] + kappa * G1 * hh * gyz * dt;
        eIE += 0.5 * ((qo0 + q[0]) * gxz + (qo1 + q[1]) * gyz) * dt * A;
        double fl[4][3], ml[4][2];
        for (int I = 0; I < 4; ++I) {
            fl[I][0] = A * (B1[I] * Nxx + B2[I] * Nxy);
            fl[I][1] = A * (B2[I] * Nyy + B1[I] * Nxy);
            fl[I][2] = A * (B1[I] * q[0] + B2[I] * q[1]);
            ml[I][0] = A * (B2[I] * Myy + B1[I] * Mxy - 0.25 * q[1]);
            ml[I][1] = -A * (B1[I] * Mxx + B2[I] * Mxy - 0.25 * q[0]);
        }
        /* hourglass control */
        double hx = 0, hy = 0, BB = 0;
        for (int I = 0; I < 4; ++I) {
            hx += HG_H[I] * xl[I];
            hy += HG_H[I] * yl[I];
            BB += B1[I] * B1[I] + B2[I] * B2[I];
        }
        double gam[4], qd[5] = {0, 0, 0, 0, 0};
        for (int I = 0; I < 4; ++I) {
            gam[I] = HG_H[I] - hx * B1[I] - hy * B2[I];
            qd[0] += gam[I] * wl[I][0];
            qd[1] += gam[I] * wl[I][1];
            qd[2] += gam[I] * vl[I][2];
            qd[3] += gam[I] * vl[I][0];
            qd[4] += gam[I] * vl[I][1];
        }
        double rth = qhg * E1 * hh * hh * hh * A * BB / 192.0;
        double rw = qhg * kappa * G1 * hh * hh * hh * BB / 12.0;
        double rm = qhg * E1 * hh * A * BB / 8.0;
        double rr[5] = {rth, rth, rw, rm, rm};
        double *hq = hgs + 5 * (size_t)e;
        for (int j = 0; j < 5; ++j) {
            double old = ratio * hq[j];
            hq[j] = old + rr[j] * qd[j] * dt;
            eHG += 0.5 * (old + hq[j]) * qd[j] * dt;
        }
        for (int I = 0; I < 4; ++I) {
            ml[I][0] += gam[I] * hq[0];
            ml[I][1] += gam[I] * hq[1];
            fl[I][2] += gam[I] * hq[2];
            fl[I][0] += gam[I] * hq[3];
            fl[I][1] += gam[I] * hq[4];
        }
        double *o = fe + 24 * (size_t)e;
        for (int I = 0; I < 4; ++I)
            for (int k = 0; k < 3; ++k) {
                o[6 * I + k] = fl[I][0] * e1[k] + fl[I][1] * e2[k] + fl[I][2] * e3[k];
                o[6 * I + 3 + k] = ml[I][0] * e1[k] + ml[I][1] * e2[k];
            }
    }
    energy[0] += eIE;
    energy[1] += eHG;
    energy[2] += ePL;
    energy[3] += eTH;
}

/* f (nn*6) = sum of element contributions; ptr/idx: CSR of node -> (4*e + I) */
void gather(int nn, const int *ptr, const int *idx, const double *fe, double *f)
{
#pragma omp parallel for schedule(static)
    for (int n = 0; n < nn; ++n) {
        double s[6] = {0, 0, 0, 0, 0, 0};
        for (int k = ptr[n]; k < ptr[n + 1]; ++k) {
            const double *p = fe + 6 * (size_t)idx[k];
            for (int j = 0; j < 6; ++j) s[j] += p[j];
        }
        for (int j = 0; j < 6; ++j) f[6 * (size_t)n + j] = s[j];
    }
}

/* Central-difference update with mass-proportional damping c (1/s).
 * fix: nn*6 flags (1 fixed, 2 prescribed velocity vpres). cons: ncons constraints (node, type 0 = translation, 1 = rotation,
 * unit direction): the velocity component along the direction is removed.
 * out[0] = kinetic energy at the half step, out[1] += damping work. */
void integrate(int nn, double *x, double *v, double *w, const double *fint, const double *fpat, double lam,
               const double *mass, const double *rinert, const unsigned char *fix, const double *vpres,
               int ncons, const int *cnode, const int *ctype, const double *cdir,
               double c, double dt, double *out)
{
    double ke = 0.0, ed = 0.0;
    const double a = 1.0 - 0.5 * c * dt, b = 1.0 / (1.0 + 0.5 * c * dt);
#pragma omp parallel for schedule(static) reduction(+ : ke, ed)
    for (int n = 0; n < nn; ++n) {
        const double m = mass[n], I = rinert[n];
        for (int k = 0; k < 3; ++k) {
            size_t j = 6 * (size_t)n + k;
            double *vv = v + 3 * (size_t)n + k;
            if (fix[j]) { *vv = (fix[j] == 2) ? vpres[j] : 0.0; continue; }
            double f = lam * fpat[j] - fint[j];
            double vo = *vv;
            *vv = (a * vo + dt * f / m) * b;
            ed += c * m * 0.25 * (vo + *vv) * (vo + *vv) * dt;
        }
        for (int k = 0; k < 3; ++k) {
            size_t j = 6 * (size_t)n + 3 + k;
            double *ww = w + 3 * (size_t)n + k;
            if (fix[j]) { *ww = (fix[j] == 2) ? vpres[j] : 0.0; continue; }
            double wo = *ww;
            *ww = (a * wo + dt * (lam * fpat[j] - fint[j]) / I) * b;
            ed += c * I * 0.25 * (wo + *ww) * (wo + *ww) * dt;
        }
    }
    for (int i = 0; i < ncons; ++i) {
        double *p = (ctype[i] == 0 ? v : w) + 3 * (size_t)cnode[i];
        const double *d = cdir + 3 * i;
        double s = dot(p, d);
        p[0] -= s * d[0];
        p[1] -= s * d[1];
        p[2] -= s * d[2];
    }
#pragma omp parallel for schedule(static) reduction(+ : ke)
    for (int n = 0; n < nn; ++n) {
        double *vv = v + 3 * (size_t)n, *ww = w + 3 * (size_t)n;
        for (int k = 0; k < 3; ++k) x[3 * (size_t)n + k] += dt * vv[k];
        ke += 0.5 * mass[n] * dot(vv, vv) + 0.5 * rinert[n] * dot(ww, ww);
    }
    out[0] = ke;
    out[1] += ed;
}

/* Coulomb friction on a penalty tangential spring. ft: stored tangential force (3).
 * n: unit normal; fn >= 0; vt: relative tangential velocity of the slave. Returns
 * the dissipated energy over the step. */
static double friction(double *ft, const double *n, double fn, const double *vt, double kt, double mu, double dt)
{
    double s = dot(ft, n);
    for (int k = 0; k < 3; ++k) ft[k] = ft[k] - s * n[k] - kt * vt[k] * dt;
    double mag = sqrt(dot(ft, ft)), cap = mu * fn;
    if (mag > cap) {
        double slip = (mag - cap) / kt;
        double sc = mag > 0 ? cap / mag : 0.0;
        for (int k = 0; k < 3; ++k) ft[k] *= sc;
        return cap * slip;
    }
    return 0.0;
}

/* Rigid bounded plane. P: p0[3], n[3] (outward, toward the slaves), t1[3], t2[3],
 * lim[4] = (s1min, s1max, s2min, s2max). Slave surface = node + off along -n.
 * out[0..2] = force on the plane (reaction) this cycle, out[3] += friction dissipation,
 * out[4] = number of active slaves this cycle. */
void contact_plane(int ns, const int *snode, const double *soff, const double *P,
                   const double *x, const double *v, const double *kn, double ktf, double mu, const double *cn,
                   double dt, double gmax, double *ft, double *fint, double *out)
{
    const double *p0 = P, *n = P + 3, *t1 = P + 6, *t2 = P + 9, *lim = P + 12;
    out[0] = out[1] = out[2] = out[4] = 0.0;
    double o0 = 0, o1 = 0, o2 = 0, o3 = 0, o4 = 0;
#pragma omp parallel for schedule(static) reduction(+ : o0, o1, o2, o3, o4) if (ns > 256)
    for (int i = 0; i < ns; ++i) {
        const int nd = snode[i];
        const double *xi = x + 3 * (size_t)nd;
        double d[3] = {xi[0] - p0[0], xi[1] - p0[1], xi[2] - p0[2]};
        double g = dot(d, n) - soff[i];
        double s1 = dot(d, t1), s2 = dot(d, t2);
        double *f = ft + 3 * i;
        if (!(g < 0.0 && g > -gmax && s1 >= lim[0] && s1 <= lim[1] && s2 >= lim[2] && s2 <= lim[3])) {
            f[0] = f[1] = f[2] = 0.0;
            continue;
        }
        const double *vi = v + 3 * (size_t)nd;
        double vn = dot(vi, n);
        double fn = -kn[i] * g - cn[i] * vn;
        if (fn < 0.0) fn = 0.0;
        double vt[3] = {vi[0] - vn * n[0], vi[1] - vn * n[1], vi[2] - vn * n[2]};
        o3 += friction(f, n, fn, vt, ktf * kn[i], mu, dt);
        double F0 = fn * n[0] + f[0], F1 = fn * n[1] + f[1], F2 = fn * n[2] + f[2];
        fint[6 * (size_t)nd + 0] -= F0;
        fint[6 * (size_t)nd + 1] -= F1;
        fint[6 * (size_t)nd + 2] -= F2;
        o0 -= F0; o1 -= F1; o2 -= F2;
        o4 += 1.0;
    }
    out[0] = o0; out[1] = o1; out[2] = o2; out[3] += o3; out[4] = o4;
}

/* Project point p onto quad (nodes nd): natural coordinates, surface point, normal, shape functions. */
static void project_quad(const double *x, const int *nd, const double *p, double *xi, double *eta,
                         double *xs, double *nrm, double *N)
{
    double X[4][3];
    for (int I = 0; I < 4; ++I)
        for (int k = 0; k < 3; ++k) X[I][k] = x[3 * nd[I] + k];
    double e1[3], e2[3], xc[3];
    frame(X, e1, e2, nrm, xc);
    double xl[4], yl[4];
    for (int I = 0; I < 4; ++I) {
        double d[3] = {X[I][0] - xc[0], X[I][1] - xc[1], X[I][2] - xc[2]};
        xl[I] = dot(d, e1);
        yl[I] = dot(d, e2);
    }
    double dp[3] = {p[0] - xc[0], p[1] - xc[1], p[2] - xc[2]};
    double px = dot(dp, e1), py = dot(dp, e2);
    double a = 0.0, b = 0.0;
    for (int it = 0; it < 8; ++it) {
        double fx = -px, fy = -py, J11 = 0, J12 = 0, J21 = 0, J22 = 0;
        for (int I = 0; I < 4; ++I) {
            double Ni = 0.25 * (1 + a * XI_I[I]) * (1 + b * ETA_I[I]);
            double dxi = 0.25 * XI_I[I] * (1 + b * ETA_I[I]), deta = 0.25 * ETA_I[I] * (1 + a * XI_I[I]);
            fx += Ni * xl[I];
            fy += Ni * yl[I];
            J11 += dxi * xl[I];
            J12 += deta * xl[I];
            J21 += dxi * yl[I];
            J22 += deta * yl[I];
        }
        double det = J11 * J22 - J12 * J21;
        double da = (J22 * fx - J12 * fy) / det, db = (-J21 * fx + J11 * fy) / det;
        a -= da;
        b -= db;
        if (fabs(da) + fabs(db) < 1e-12) break;
    }
    *xi = a;
    *eta = b;
    for (int k = 0; k < 3; ++k) xs[k] = 0.0;
    for (int I = 0; I < 4; ++I) {
        N[I] = 0.25 * (1 + a * XI_I[I]) * (1 + b * ETA_I[I]);
        for (int k = 0; k < 3; ++k) xs[k] += N[I] * X[I][k];
    }
}

/* Nodes (snode >= 0) or fixed points (snode < 0, position spos) against a shell
 * surface. cur: current master element per slave (-1: none), moved across edges with
 * nbr (nel*4; edge 0 = nodes 0-1, 1 = 1-2, 2 = 2-3, 3 = 3-0). The contact side of the
 * surface is the one whose normal has a positive component along dref; its surface
 * lies at mfac * thickness from the mid-surface. */
void contact_surface(int ns, const int *snode, const double *spos, const double *soff, int *cur,
                     const int *conn, const int *nbr, const double *hel, double mfac, const double *dref,
                     const double *x, const double *v, const double *kn, double ktf, double mu, const double *cn,
                     double dt, double gmax, double *ft, double *fint, double *out)
{
    out[0] = out[1] = out[2] = out[4] = 0.0;
    double o0 = 0, o1 = 0, o2 = 0, o3 = 0, o4 = 0;
#pragma omp parallel for schedule(dynamic, 64) reduction(+ : o0, o1, o2, o3, o4) if (ns > 256)
    for (int i = 0; i < ns; ++i) {
        double *f = ft + 3 * i;
        int e = cur[i];
        if (e < 0) { f[0] = f[1] = f[2] = 0.0; continue; }
        const double *p = snode[i] >= 0 ? x + 3 * (size_t)snode[i] : spos + 3 * i;
        double xi, eta, xs[3], nrm[3], N[4];
        int found = 0;
        for (int hop = 0; hop < 12; ++hop) {
            project_quad(x, conn + 4 * e, p, &xi, &eta, xs, nrm, N);
            double vx = fabs(xi) - 1.0, ve = fabs(eta) - 1.0;
            if (vx <= 1e-9 && ve <= 1e-9) { found = 1; break; }
            int edge = (vx > ve) ? (xi > 0 ? 1 : 3) : (eta > 0 ? 2 : 0);
            int e2 = nbr[4 * e + edge];
            if (e2 < 0) break;
            e = e2;
        }
        cur[i] = e;
        if (!found) { f[0] = f[1] = f[2] = 0.0; continue; }
        if (dot(nrm, dref) < 0.0) { nrm[0] = -nrm[0]; nrm[1] = -nrm[1]; nrm[2] = -nrm[2]; }
        double d[3] = {p[0] - xs[0], p[1] - xs[1], p[2] - xs[2]};
        double g = dot(d, nrm) - soff[i] - mfac * hel[e];
        if (!(g < 0.0 && g > -gmax)) { f[0] = f[1] = f[2] = 0.0; continue; }
        const int *nd = conn + 4 * e;
        double vrel[3] = {0, 0, 0};
        if (snode[i] >= 0)
            for (int k = 0; k < 3; ++k) vrel[k] = v[3 * (size_t)snode[i] + k];
        for (int I = 0; I < 4; ++I)
            for (int k = 0; k < 3; ++k) vrel[k] -= N[I] * v[3 * (size_t)nd[I] + k];
        double vn = dot(vrel, nrm);
        double fn = -kn[i] * g - cn[i] * vn;
        if (fn < 0.0) fn = 0.0;
        double vt[3] = {vrel[0] - vn * nrm[0], vrel[1] - vn * nrm[1], vrel[2] - vn * nrm[2]};
        o3 += friction(f, nrm, fn, vt, ktf * kn[i], mu, dt);
        double F[3];
        for (int k = 0; k < 3; ++k) F[k] = fn * nrm[k] + f[k];      /* on the slave */
        if (snode[i] >= 0)
            for (int k = 0; k < 3; ++k) fint[6 * (size_t)snode[i] + k] -= F[k];
        for (int I = 0; I < 4; ++I)
            for (int k = 0; k < 3; ++k) {
#pragma omp atomic
                fint[6 * (size_t)nd[I] + k] += N[I] * F[k];
            }
        o0 += F[0]; o1 += F[1]; o2 += F[2];         /* force on the slave side */
        o4 += 1.0;
    }
    out[0] = o0; out[1] = o1; out[2] = o2; out[3] += o3; out[4] = o4;
}

/* Breakable two-point springs (bolts, studs). End A: up to 4 nodes with weights; end
 * B: up to 4 nodes with weights, or fixed (nb[4i] < 0) at pB. d = (xB - xA) - d0.
 * Axis n (unit; from B toward A): fixed (nfix), or the current normal of element
 * eax >= 0 (sign kept close to nfix). Shear part ds = d - (d.n) n acts after a
 * radial clearance clr; axial part acts without clearance. F on A = ks (|ds| - clr)
 * ds/|ds| + ka (d.n) n. Failure: |Fs| > vcap, or tension -(d.n) ka > tcap.
 * fsv: nsp*7 output (|Fs|, tension, slip |ds|, stored energy, force on A (3)). */
void springs(int nsp, const int *na, const double *wa, const int *nb, const double *wb, const double *pB,
             const double *d0, const double *nfix, const int *eax, const int *conn,
             const double *ks, const double *ka, const double *clr, const double *vcap, const double *tcap,
             unsigned char *broken, const double *x, double *fint, double *fsv)
{
    for (int i = 0; i < nsp; ++i) {
        double *o = fsv + 7 * i;
        if (broken[i]) { o[0] = o[1] = o[2] = o[3] = o[4] = o[5] = o[6] = 0.0; continue; }
        double xa[3] = {0, 0, 0}, xb[3] = {0, 0, 0};
        for (int I = 0; I < 4; ++I) {
            int n1 = na[4 * i + I];
            if (n1 >= 0) for (int k = 0; k < 3; ++k) xa[k] += wa[4 * i + I] * x[3 * (size_t)n1 + k];
        }
        if (nb[4 * i] >= 0) {
            for (int I = 0; I < 4; ++I) {
                int n1 = nb[4 * i + I];
                if (n1 >= 0) for (int k = 0; k < 3; ++k) xb[k] += wb[4 * i + I] * x[3 * (size_t)n1 + k];
            }
        } else
            for (int k = 0; k < 3; ++k) xb[k] = pB[3 * i + k];
        double d[3];
        for (int k = 0; k < 3; ++k) d[k] = xb[k] - xa[k] - d0[3 * i + k];
        double n[3] = {nfix[3 * i], nfix[3 * i + 1], nfix[3 * i + 2]};
        if (eax[i] >= 0) {
            double X[4][3], e1[3], e2[3], e3[3], xc[3];
            const int *nd = conn + 4 * eax[i];
            for (int I = 0; I < 4; ++I)
                for (int k = 0; k < 3; ++k) X[I][k] = x[3 * (size_t)nd[I] + k];
            frame(X, e1, e2, e3, xc);
            if (dot(e3, n) < 0.0) { e3[0] = -e3[0]; e3[1] = -e3[1]; e3[2] = -e3[2]; }
            n[0] = e3[0]; n[1] = e3[1]; n[2] = e3[2];
        }
        double dn = dot(d, n);
        double ds[3] = {d[0] - dn * n[0], d[1] - dn * n[1], d[2] - dn * n[2]};
        double sl = sqrt(dot(ds, ds));
        double fs = (sl > clr[i]) ? ks[i] * (sl - clr[i]) : 0.0;
        double ten = -dn * ka[i];
        if (fs > vcap[i] || ten > tcap[i]) {
            broken[i] = 1;
            o[0] = fs; o[1] = ten; o[2] = sl;
            o[3] = 0.5 * fs * fs / ks[i] + 0.5 * ka[i] * dn * dn;   /* energy lost at failure */
            o[4] = o[5] = o[6] = 0.0;
            continue;
        }
        double F[3];
        for (int k = 0; k < 3; ++k) F[k] = (sl > 0 ? fs * ds[k] / sl : 0.0) + ka[i] * dn * n[k];
        for (int I = 0; I < 4; ++I) {
            int n1 = na[4 * i + I];
            if (n1 >= 0) for (int k = 0; k < 3; ++k) fint[6 * (size_t)n1 + k] -= wa[4 * i + I] * F[k];
        }
        if (nb[4 * i] >= 0)
            for (int I = 0; I < 4; ++I) {
                int n1 = nb[4 * i + I];
                if (n1 >= 0) for (int k = 0; k < 3; ++k) fint[6 * (size_t)n1 + k] += wb[4 * i + I] * F[k];
            }
        o[0] = fs;
        o[1] = ten;
        o[2] = sl;
        o[3] = 0.5 * fs * fs / ks[i] + 0.5 * ka[i] * dn * dn;
        o[4] = F[0];
        o[5] = F[1];
        o[6] = F[2];
    }
}

#ifdef _OPENMP
#include <omp.h>
void set_threads(int n) { omp_set_num_threads(n); }
int get_threads(void) { return omp_get_max_threads(); }
#else
void set_threads(int n) { (void)n; }
int get_threads(void) { return 1; }
#endif
