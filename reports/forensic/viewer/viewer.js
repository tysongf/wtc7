// Detailed-model viewer: deformed shapes from scripts/export_viewer.py output (data/*.js).
// Vue holds the controls and the trace; Three draws one canvas split into one or two viewports that
// share a camera. Mesh arrays live outside Vue so they are not made reactive.
(function () {
  "use strict";
  const W7 = window.WTC7;
  const H = 260, M = { l: 52, r: 14, t: 12, b: 40 };
  // sequential blue, steps 100 to 700 (dataviz reference palette)
  const BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
                "#1c5cab", "#184f95", "#104281", "#0d366b"];
  const EVENTS = [
    ["E1_g79_all_bolts", "E1 column 79 bolts gone"], ["E3_g44_all_bolts", "E3 column 44 bolts gone"],
    ["E4_beam_buckled", "E4 beam buckles"], ["E5_girder_buckled", "E5 girder buckles"],
    ["first_fin_bolt", "First fin bolt"], ["Q12_west_plate_bearing", "Bears on west plate"],
    ["E2r_rocking_79", "E2r twist limit"], ["E2_walkoff_79", "E2 walk-off"], ["E2_support_lost_79", "E2s support lost"],
  ];
  const QUANTITIES = [
    { key: "lat79", label: "Girder end at column 79: movement west (in.)", unit: "in.", walk: true },
    { key: "ax79", label: "Girder end at column 79: movement along the girder, + away from the column (in.)", unit: "in." },
    { key: "dz79", label: "Girder end at column 79: vertical movement (in.)", unit: "in." },
    { key: "twist79", label: "Girder end at column 79: twist, + top toward west (deg)", unit: "deg" },
  ];
  const VIEWS = [
    { key: "col79", label: "Column 79" }, { key: "end", label: "Along the girder" }, { key: "below", label: "From below" },
    { key: "floor", label: "Whole floor" }, { key: "plan", label: "Plan" },
  ];
  const PART_LABEL = { girder: "Girder", stiffener: "Girder", beam: "Floor beams", fin: "Fin plates", slab: "Slab" };
  const PART_VAR = { girder: "--s1", stiffener: "--s1", beam: "--s2", fin: "--s3", slab: "--neutral" };

  // ---------------------------------------------------------------- loading and decoding
  function script(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error("could not load " + src));
      document.head.appendChild(s);
    });
  }

  async function gunzip(b64) {
    const bin = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
    const stream = new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"));
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }

  const geoms = {}, runs = {};

  function geometry(key) {
    if (!geoms[key]) geoms[key] = (async () => {
      await script("data/geom_" + key + ".js");
      const g = W7.geom[key];
      const x0 = new Float32Array((await gunzip(g.x0)).buffer);
      const cb = (await gunzip(g.conn)).buffer;
      const conn = g.conn_type === "uint16" ? new Uint16Array(cb) : new Uint32Array(cb);
      const pid = await gunzip(g.pid);
      const slabId = g.parts.indexOf("slab");
      const steel = [], slab = [];
      const nodePart = new Uint8Array(g.nn);
      for (let e = 0; e < g.ne; e++) {
        const a = conn[4 * e], b = conn[4 * e + 1], c = conn[4 * e + 2], d = conn[4 * e + 3];
        (pid[e] === slabId ? slab : steel).push(a, b, c, a, c, d);
        if (pid[e] !== slabId) nodePart[a] = nodePart[b] = nodePart[c] = nodePart[d] = pid[e];
        else nodePart[a] = nodePart[b] = nodePart[c] = nodePart[d] = slabId;
      }
      return { key, nn: g.nn, parts: g.parts, x0, nodePart, idxSteel: new Uint32Array(steel), idxSlab: new Uint32Array(slab) };
    })();
    return geoms[key];
  }

  function loadRun(name) {
    if (!runs[name]) runs[name] = (async () => {
      await script("data/" + encodeURIComponent(name) + ".js");
      const r = W7.runs[name];
      const g = await geometry(r.geom);
      const bytes = await gunzip(r.u);
      const F = r.frames.t.length, N = g.nn, L = F * 3 * N;
      const acc = new Int32Array(3 * N), u = [];
      for (let k = 0; k < F; k++) {
        const f = new Float32Array(3 * N);
        for (let c = 0; c < 3; c++) {
          const base = (k * 3 + c) * N;
          for (let n = 0; n < N; n++) {
            const i = base + n;
            acc[c * N + n] += ((bytes[L + i] << 8) | bytes[i]) << 16 >> 16;
            f[3 * n + c] = acc[c * N + n] * r.res;
          }
        }
        u.push(f);
      }
      return { meta: r, geom: g, u };
    })();
    return runs[name];
  }

  // ---------------------------------------------------------------- helpers
  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  function frameIndex(ft, t) {
    let k = 0;
    for (let i = 0; i < ft.length; i++) if (ft[i] <= t + 1e-6) k = i;
    return k;
  }

  function niceTicks(lo, hi, n) {
    const span = hi - lo || 1, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0))), err = step0 / mag;
    const step = (err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1) * mag;
    const out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }

  function nearestRow(tt, t) {
    let lo = 0, hi = tt.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (tt[mid] <= t) lo = mid; else hi = mid; }
    return Math.abs(tt[hi] - t) < Math.abs(tt[lo] - t) ? hi : lo;
  }

  function rampLUT() {
    const cols = BLUE.map((h) => new THREE.Color(h)), lut = new Float32Array(256 * 3);
    for (let i = 0; i < 256; i++) {
      const x = (i / 255) * (cols.length - 1), j = Math.min(Math.floor(x), cols.length - 2), f = x - j;
      const c = cols[j].clone().lerp(cols[j + 1], f);
      lut[3 * i] = c.r; lut[3 * i + 1] = c.g; lut[3 * i + 2] = c.b;
    }
    return lut;
  }

  // ---------------------------------------------------------------- 3D
  const R = { need: true, panes: [], lut: null };

  function initThree(canvas, onChange) {
    R.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    R.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    R.renderer.setScissorTest(true);
    R.camera = new THREE.PerspectiveCamera(35, 1, 1, 20000);
    R.camera.up.set(0, 0, 1);
    R.camera.position.set(-110, -90, 25);
    R.controls = new THREE.OrbitControls(R.camera, canvas);
    R.controls.target.set(0, 30, -18);
    R.controls.update();
    R.controls.addEventListener("change", () => { R.need = true; onChange(); });
    R.lut = rampLUT();
    for (let i = 0; i < 2; i++) {
      const scene = new THREE.Scene();
      scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8984, 0.8));
      const sun = new THREE.DirectionalLight(0xffffff, 0.45);
      sun.position.set(-1, -1.5, 2);
      scene.add(sun);
      const fill = new THREE.DirectionalLight(0xffffff, 0.2);
      fill.position.set(1, 1, -1);
      scene.add(fill);
      R.panes.push({ scene, name: null });
    }
    const loop = () => {
      requestAnimationFrame(loop);
      if (R.need) { R.need = false; render(); }
    };
    loop();
  }

  function render() {
    const r = R.renderer, el = r.domElement, w = el.clientWidth, h = el.clientHeight;
    if (!w || !h) return;
    const n = R.count || 1;
    r.setClearColor(new THREE.Color(cssVar("--stage")));
    for (let i = 0; i < n; i++) {
      const p = R.panes[i];
      let x = 0, y = 0, vw = w, vh = h;
      if (R.rows) { vh = Math.round(h / n); y = h - (i + 1) * vh; }
      else { x = Math.round((i * w) / n); vw = Math.round(((i + 1) * w) / n) - x; }
      r.setViewport(x, y, vw, vh);
      r.setScissor(x, y, vw, vh);
      R.camera.aspect = vw / vh;
      // keep the horizontal field of view of a 1.4:1 viewport when the viewport is taller than that
      R.camera.fov = R.camera.aspect >= 1.4 ? 35
        : (2 * Math.atan((Math.tan((17.5 * Math.PI) / 180) * 1.4) / R.camera.aspect) * 180) / Math.PI;
      R.camera.updateProjectionMatrix();
      r.render(p.scene, R.camera);
    }
  }

  function clear(group) {
    if (!group) return;
    group.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
    group.parent && group.parent.remove(group);
  }

  function setPaneRun(p, d) {
    clear(p.root);
    const g = d.geom, root = new THREE.Group();
    const pos = new THREE.BufferAttribute(new Float32Array(g.x0), 3);
    const col = new THREE.BufferAttribute(new Float32Array(3 * g.nn), 3);
    const steelG = new THREE.BufferGeometry();
    steelG.setAttribute("position", pos);
    steelG.setAttribute("color", col);
    steelG.setIndex(new THREE.BufferAttribute(g.idxSteel, 1));
    const steel = new THREE.Mesh(steelG, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide }));
    const slabG = new THREE.BufferGeometry();
    slabG.setAttribute("position", pos);
    slabG.setIndex(new THREE.BufferAttribute(g.idxSlab, 1));
    const slab = new THREE.Mesh(slabG, new THREE.MeshLambertMaterial({
      color: cssVar("--neutral"), transparent: true, opacity: 0.22, depthWrite: false, side: THREE.DoubleSide }));
    slab.renderOrder = 2;

    const supports = new THREE.Group();
    for (const pl of d.meta.planes) {
      const q = pl.quad.flat(), at79 = pl.name.includes("79");
      const pg = new THREE.BufferGeometry();
      pg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(q), 3));
      pg.setIndex([0, 1, 2, 0, 2, 3]);
      const c = cssVar("--support");
      supports.add(new THREE.Mesh(pg, new THREE.MeshBasicMaterial({
        color: c, transparent: true, opacity: at79 ? 0.5 : 0.28, depthWrite: false, side: THREE.DoubleSide })));
      const eg = new THREE.BufferGeometry();
      eg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(q), 3));
      supports.add(new THREE.LineLoop(eg, new THREE.LineBasicMaterial({ color: c })));
    }

    const ns = d.meta.springs.names.length;
    const mkPoints = (size) => {
      const bg = new THREE.BufferGeometry();
      bg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(3 * ns), 3));
      bg.setDrawRange(0, 0);
      return new THREE.Points(bg, new THREE.PointsMaterial({ size, sizeAttenuation: false, color: 0xffffff }));
    };
    const intact = mkPoints(5), broken = mkPoints(9);
    root.add(steel, slab, supports, intact, broken);
    p.scene.add(root);
    Object.assign(p, { root, steel, slab, supports, intact, broken, pos, col, d, name: d.meta.name });
  }

  function updatePane(p, opt) {
    const d = p.d, g = d.geom, k = frameIndex(d.meta.frames.t, opt.t), u = d.u[k];
    const P = p.pos.array, C = p.col.array, x0 = g.x0, s = opt.scale;
    for (let i = 0; i < P.length; i++) P[i] = x0[i] + s * u[i];
    p.pos.needsUpdate = true;
    p.steel.geometry.computeVertexNormals();
    if (opt.showSlab) p.slab.geometry.computeVertexNormals();
    if (opt.colorBy === "disp") {
      const lut = R.lut, inv = opt.umax > 0 ? 255 / opt.umax : 0;
      for (let n = 0; n < g.nn; n++) {
        const a = u[3 * n], b = u[3 * n + 1], c = u[3 * n + 2];
        const j = 3 * Math.min(255, Math.round(Math.sqrt(a * a + b * b + c * c) * inv));
        C[3 * n] = lut[j]; C[3 * n + 1] = lut[j + 1]; C[3 * n + 2] = lut[j + 2];
      }
    } else {
      const pc = g.parts.map((name) => new THREE.Color(cssVar(PART_VAR[name] || "--neutral")));
      for (let n = 0; n < g.nn; n++) {
        const c = pc[g.nodePart[n]];
        C[3 * n] = c.r; C[3 * n + 1] = c.g; C[3 * n + 2] = c.b;
      }
    }
    p.col.needsUpdate = true;
    p.slab.visible = opt.showSlab;
    p.supports.visible = opt.showSupports;
    p.slab.material.color.set(cssVar("--neutral"));
    p.supports.traverse((o) => { if (o.material) o.material.color.set(cssVar("--support")); });

    const sp = d.meta.springs, tk = d.meta.frames.t[k], A = p.intact.geometry, B = p.broken.geometry;
    const pa = A.attributes.position.array, pb = B.attributes.position.array;
    let na = 0, nb = 0;
    for (let i = 0; i < sp.names.length; i++) {
      if (!(sp.group[i].startsWith("stud") ? opt.showStuds : opt.showBolts)) continue;
      let x = 0, y = 0, z = 0;
      for (let j = 0; j < 4; j++) {
        const n = sp.na[i][j], w = sp.wa[i][j];
        if (n < 0 || !w) continue;
        x += w * P[3 * n]; y += w * P[3 * n + 1]; z += w * P[3 * n + 2];
      }
      const isBroken = sp.t_break[i] != null && sp.t_break[i] <= tk + 1e-6;
      const arr = isBroken ? pb : pa, m = isBroken ? nb++ : na++;
      arr[3 * m] = x; arr[3 * m + 1] = y; arr[3 * m + 2] = z;
    }
    A.setDrawRange(0, na); B.setDrawRange(0, nb);
    A.attributes.position.needsUpdate = B.attributes.position.needsUpdate = true;
    A.computeBoundingSphere(); B.computeBoundingSphere();
    p.intact.material.color.set(cssVar("--bolt"));
    p.broken.material.color.set(cssVar("--critical"));
    p.intact.visible = p.broken.visible = opt.showBolts || opt.showStuds;
  }

  function setView(key, g) {
    const x0 = g ? g.x0 : null;
    const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
    if (x0) for (let i = 0; i < x0.length; i++) { const c = i % 3; lo[c] = Math.min(lo[c], x0[i]); hi[c] = Math.max(hi[c], x0[i]); }
    const cx = (lo[0] + hi[0]) / 2, cy = (lo[1] + hi[1]) / 2, cz = (lo[2] + hi[2]) / 2;
    const diag = Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) || 1000;
    const V = {
      col79: [[0, 40, -18], [-150, -90, 40]],
      end: [[0, 0, -16], [0, -170, -6]],
      below: [[0, 60, -20], [-130, -50, -150]],
      floor: [[cx, cy, cz], [cx - 0.55 * diag, cy - 0.7 * diag, cz + 0.45 * diag]],
      plan: [[cx, cy, cz], [cx, cy - 1, cz + 1.25 * diag]],
    }[key];
    R.controls.target.set(...V[0]);
    R.camera.position.set(...V[1]);
    R.controls.update();
    R.need = true;
  }

  // ---------------------------------------------------------------- app
  const hash = new URLSearchParams(location.hash.slice(1));
  const names = W7.index.runs.map((r) => r.name);
  const pick = (v, dflt) => (names.includes(v) ? v : dflt);

  Vue.createApp({
    data() {
      return {
        index: W7.index,
        runA: pick(hash.get("a"), W7.index.base),
        runB: pick(hash.get("b"), names.includes("nist_replica") ? "nist_replica" : names[0]),
        compare: hash.has("b"),
        colorBy: hash.get("c") === "disp" ? "disp" : "part",
        scale: [1, 2, 5, 10, 20].includes(+hash.get("s")) ? +hash.get("s") : 1, scales: [1, 2, 5, 10, 20], showSlab: false, showBolts: true, showStuds: false, showSupports: true,
        ti: 0, narrow: false, quantity: "lat79", playing: false, hoverT: null, hoverPx: 0, infos: {}, northDeg: 0, theme: 0,
        W: 800, H, M, views: VIEWS, quantities: QUANTITIES, error: null,
      };
    },
    computed: {
      shown() { return this.compare ? [this.runA, this.runB] : [this.runA]; },
      times() {
        const s = new Set();
        for (const n of this.shown) if (this.infos[n]) this.infos[n].ft.forEach((t) => s.add(t));
        return [...s].sort((a, b) => a - b);
      },
      tNow() { return this.times[this.ti] || 0; },
      panes() {
        return this.shown.map((n) => {
          const r = this.infos[n];
          if (!r) return { run: null };
          const k = frameIndex(r.ft, this.tNow), last = k === r.ft.length - 1;
          return {
            run: r, events: r.events, diffText: r.diffText,
            frameText: `Snapshot ${k + 1} of ${r.ft.length}: t = ${r.ft[k].toFixed(2)} s, beam ${r.fT[k].toFixed(0)} °C`,
            afterLast: last && r.tEnd > r.ft[k] + 0.05,
            lastT: `t = ${r.ft[k].toFixed(2)} s`,
            endText: `t = ${r.tEnd.toFixed(2)} s (${r.status})`,
          };
        });
      },
      umaxShown() {
        let m = 0;
        for (const n of this.shown) if (this.infos[n]) m = Math.max(m, ...this.infos[n].unorm);
        return m;
      },
      resText() {
        const v = Object.values(this.infos).map((r) => r.res);
        return v.length ? Math.max(...v).toFixed(3) : "0.005";
      },
      rampCss() { return "linear-gradient(to right," + BLUE.join(",") + ")"; },
      partLegend() {
        this.theme;
        const l = [{ name: "Girder", color: cssVar("--s1") }, { name: "Floor beams", color: cssVar("--s2") },
                   { name: "Fin plates", color: cssVar("--s3") }];
        if (this.showSlab) l.push({ name: "Slab", color: cssVar("--neutral") });
        if (this.showSupports) l.push({ name: "Column faces, seats and plates (rigid)", color: cssVar("--support") });
        return l;
      },
      boltWord() { return this.showBolts && this.showStuds ? "Bolt or stud" : this.showStuds ? "Stud" : "Bolt"; },
      boltColors() { this.theme; return { intact: cssVar("--bolt"), broken: cssVar("--critical") }; },
      seriesColors() { this.theme; return [cssVar("--s1"), cssVar("--s2")]; },
      qInfo() {
        const q = QUANTITIES.find((x) => x.key === this.quantity);
        const r = this.infos[this.runA];
        return { ...q, threshold: q.walk && r ? r.walkLat : null };
      },
      series() { return this.shown.map((n) => this.infos[n]).filter(Boolean); },
      xMax() { return Math.max(1, ...this.series.map((r) => r.tEnd)); },
      yDom() {
        let lo = 0, hi = 0;
        for (const r of this.series) for (const v of r.trace[this.quantity]) { if (v < lo) lo = v; if (v > hi) hi = v; }
        if (this.qInfo.threshold != null) hi = Math.max(hi, this.qInfo.threshold * 1.1);
        const pad = (hi - lo) * 0.05 || 1;
        return [lo - pad, hi + pad];
      },
      yTicks() { return niceTicks(this.yDom[0], this.yDom[1], 5); },
      xTicks() { return niceTicks(0, this.xMax, 8); },
      paths() {
        return this.series.map((r) => {
          const tt = r.trace.t, vv = r.trace[this.quantity];
          let d = "";
          for (let i = 0; i < tt.length; i++) d += (i ? "L" : "M") + this.sx(tt[i]).toFixed(1) + "," + this.sy(vv[i]).toFixed(1);
          return d;
        });
      },
      noSnap() {
        return this.series.filter((r) => r.tEnd > r.ft[r.ft.length - 1] + 0.05).map((r) => {
          const a = this.sx(r.ft[r.ft.length - 1]);
          return { x: a, w: this.sx(r.tEnd) - a };
        });
      },
      hoverInfo() {
        if (this.hoverT == null || !this.series.length) return null;
        const t = Math.max(0, Math.min(this.xMax, this.hoverT));
        const vals = this.series.map((r) => {
          const i = nearestRow(r.trace.t, t);
          return { name: r.label, v: r.trace[this.quantity][i], T: r.trace.T[i] };
        });
        return { t, x: this.sx(t), px: this.hoverPx, vals };
      },
    },
    watch: {
      shown: { handler: "loadShown", immediate: true },
      compare() { this.writeHash(); },
      ti() { this.refresh(); },
      colorBy() { this.refresh(); this.writeHash(); },
      scale() { this.refresh(); this.writeHash(); },
      showSlab() { this.refresh(); },
      showBolts() { this.refresh(); },
      showStuds() { this.refresh(); },
      W() { this.$refs.svg.setAttribute("viewBox", `0 0 ${this.W} ${H}`); },
      showSupports() { this.refresh(); },
      theme() { this.refresh(); },
    },
    mounted() {
      try {
        initThree(this.$refs.canvas, () => this.updateNorth());
      } catch (e) {
        this.$refs.wrap.textContent = "This browser could not start WebGL, so the 3D view is unavailable.";
        return;
      }
      const ro = new ResizeObserver(() => {
        const el = this.$refs.canvas;
        requestAnimationFrame(() => { this.narrow = R.rows = this.$refs.wrap.clientWidth < 700; R.need = true; });
        R.renderer.setSize(el.clientWidth, el.clientHeight, false);
        R.need = true;
      });
      ro.observe(this.$refs.wrap);
      const fit = () => { this.W = Math.max(320, Math.round(this.$refs.svg.clientWidth)); };
      new ResizeObserver(fit).observe(this.$refs.svg);
      fit();
      this.$refs.svg.setAttribute("viewBox", `0 0 ${this.W} ${H}`);
      const bump = () => { this.theme++; };
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", bump);
      new MutationObserver(bump).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
      this.mountedThree = true;
      this.refresh();
    },
    methods: {
      paneStyle(i) {
        if (!this.compare) return { left: 0, width: "100%", top: 0, bottom: 0 };
        return this.narrow ? { left: 0, width: "100%", top: i * 50 + "%", height: "50%", bottom: "auto" }
          : { left: i * 50 + "%", width: "50%", top: 0, bottom: 0 };
      },
      sx(t) { return M.l + (t / this.xMax) * (this.W - M.l - M.r); },
      sy(v) { const [a, b] = this.yDom; return H - M.b - ((v - a) / (b - a)) * (H - M.t - M.b); },
      fmt(v) { const a = Math.abs(v); return v.toFixed(a >= 100 ? 0 : a >= 10 ? 1 : 2); },
      readingClass(s) { return s.startsWith("walk-off") ? "walk" : s.startsWith("no walk-off") ? "hold" : ""; },
      async loadShown() {
        const prev = this.times.length ? this.tNow : null;
        const fresh = !Object.keys(this.infos).length;
        try {
          await Promise.all(this.shown.map((n) => this.ensure(n)));
        } catch (e) {
          this.error = String(e);
          return;
        }
        const T = this.times;
        this.ti = fresh || prev == null ? T.length - 1 : Math.max(0, T.reduce((k, t, i) => (t <= prev + 1e-6 ? i : k), 0));
        if (fresh) this.setView(VIEWS.some((v) => v.key === hash.get("v")) ? hash.get("v") : "col79");
        this.writeHash();
        this.refresh();
      },
      async ensure(n) {
        const d = await loadRun(n);
        if (this.infos[n]) return;
        const m = d.meta, ev = [];
        for (const [key, label] of EVENTS) if (m.events[key]) ev.push({ key, label, t: m.events[key].t, T: m.events[key].T });
        ev.sort((a, b) => a.t - b.t);
        const diff = Object.entries(m.diff).map(([k, v]) => k + " = " + v).join(", ");
        this.infos[n] = {
          name: n, label: m.label, reading: m.reading, status: m.status, col79: m.col79, walkLat: m.walk_lat, res: m.res,
          ft: m.frames.t, fT: m.frames.T, unorm: m.frames.unorm, tEnd: m.trace.t[m.trace.t.length - 1],
          events: ev, diffText: diff, trace: Vue.markRaw(m.trace),
        };
      },
      refresh() {
        if (!this.mountedThree) return;
        R.count = this.shown.length;
        const opt = { t: this.tNow, scale: this.scale, colorBy: this.colorBy, umax: this.umaxShown,
                      showSlab: this.showSlab, showBolts: this.showBolts, showStuds: this.showStuds, showSupports: this.showSupports };
        this.shown.forEach((n, i) => {
          const p = R.panes[i];
          if (!this.infos[n]) return;
          runs[n].then((d) => {
            if (p.name !== n) setPaneRun(p, d);
            updatePane(p, opt);
            R.need = true;
          });
        });
        R.need = true;
      },
      setView(key) {
        const n = this.shown.find((x) => this.infos[x]);
        if (!n) return;
        runs[n].then((d) => setView(key, d.geom));
      },
      updateNorth() {
        const v = new THREE.Vector3().subVectors(R.controls.target, R.camera.position);
        this.northDeg = Math.hypot(v.x, v.y) < 1e-6 ? 0 : (-Math.atan2(v.x, v.y) * 180) / Math.PI;
      },
      jumpTo(t) {
        this.ti = Math.max(0, this.times.reduce((k, x, i) => (x <= t + 1e-6 ? i : k), 0));
      },
      togglePlay() {
        this.playing = !this.playing;
        clearInterval(this.timer);
        if (!this.playing) return;
        if (this.ti >= this.times.length - 1) this.ti = 0;
        this.timer = setInterval(() => {
          if (this.ti >= this.times.length - 1) { this.playing = false; clearInterval(this.timer); return; }
          this.ti++;
        }, 700);
      },
      hover(e) {
        const svg = this.$refs.svg, rect = svg.getBoundingClientRect(), box = svg.parentElement.getBoundingClientRect();
        const x = ((e.clientX - rect.left) * this.W) / rect.width;
        this.hoverT = ((x - M.l) / (this.W - M.l - M.r)) * this.xMax;
        this.hoverPx = Math.min(e.clientX - box.left, box.width - 300);
      },
      clickTrace() { if (this.hoverInfo) this.jumpTo(this.hoverInfo.t); },
      writeHash() {
        const h = "a=" + encodeURIComponent(this.runA) + (this.compare ? "&b=" + encodeURIComponent(this.runB) : "") +
          (this.colorBy === "disp" ? "&c=disp" : "") + (this.scale !== 1 ? "&s=" + this.scale : "");
        history.replaceState(null, "", "#" + h);
      },
    },
  }).mount("#app");
})();
