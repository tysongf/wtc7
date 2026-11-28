# Phase 3 47-storey 3D model verification (`phase3/building_model.py`)

## 1. Mesh, mass scaling, and static gravity initialization (`docs/phase3_preregistration.md` §8)

| Metric | Model value | Pre-registered criterion / Reference | Status |
|---|---|---|---|
| Nodes / 6-DOF equations | `24,762` / `148,572` | Full 47-storey + penthouse 3D frame | — |
| 3D fibre beam-column elements | `16,939` | 16-fibre Gauss-Legendre × 3-pt Gauss-Lobatto | — |
| Breakable joints (interior / spandrel / splice / slab) | `7,162` / `5,436` / `1,781` / `3,357` | Coupled 6-DOF fracture & walk-off | — |
| Explicit time step `dt` | `0.000170 s` | Gershgorin Courant-verified (`0.337 %` added mass) | PASS |
| Settled `KE / IE` at `t = 1.85 s` | `0.065 %` | `< 1.0 %` | PASS |
| Max roof vertical speed `|v_z|` at trigger onset | `0.0799 in./s` | `< 0.10 in./s` | PASS |
| Settled mechanical energy balance error | `0.061 %` | `< 5.0 %` | PASS |
| Detached joints during static service gravity | `0` interior, `0` spandrel, `0` splice, `0` slab | `0` premature collapses under `1.0x` service load | PASS |

## 2. Floor 8 gravity load comparison (`NCSTAR 1-9 Fig. 11-21` & §11.3.1)

- **Total building gravity supported below Floor 8 (Floors 8–Roof + penthouses):** **`173,636.8 kip`** vs NIST target **`174,136 kip`** (`-0.29 %`; NIST LS-DYNA = `172,897 kip`, NIST ANSYS = `176,500 kip`).

| Column | 3D Model (`kip`) | NIST `Fig. 11-21` (`kip`) | Difference |
|---|---|---|---|
| Column 79 | `7,631.5` | `7,525` | `+1.4 %` |
| Column 80 | `5,486.9` | `5,478` | `+0.2 %` |
| Column 81 | `4,920.4` | `4,945` | `-0.5 %` |
| Column 76 | `5,868.9` | `5,854` | `+0.3 %` |
| Column 77 | `3,597.2` | `3,346` | `+7.5 %` |
| Column 78 | `3,451.1` | `3,409` | `+1.2 %` |
| Column 44 | `2,812.2` | `2,962` | `-5.1 %` |

## 3. Natural periods computed prior to dynamic collapse runs (`§5.3` & `§5.4`)

- **First vertical natural period of East / Column 79 superstructure (`T_v1`):** `0.6498 s` (`1.54 Hz`).
- **Locked column-removal ramp duration (`t_r = 0.1 * T_v1`):** **`0.06498 s`** (used for `R1`–`R9`, `RC`, `RU`, `RU_debris`; halved and doubled in the Step 6 `t_r` sensitivity check).
- **Fundamental elastic lateral sway periods (bare centerline steel frame):** E-W `T_1 = 4.86 s` (`0.21 Hz`), N-S `T_1 = 5.46 s` (`0.18 Hz`). Informational comparison: NIST low-amplitude ambient wind measurements (`3.45 s` E-W, `3.61 s` N-S in `NCSTAR 1-9 App. C`) include non-structural granite facade cladding, interior partitions, and uncracked composite slab flange stiffness omitted in centerline bare-steel framing.
