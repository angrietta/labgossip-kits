"""종말 예언 편 장면: 탁상 달력 + 점토 지구 + 유압 프레스(1960 FORMULA) + 인구 구슬."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine")); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import clay as C
from timeline import *

random.seed(11)
sc = C.reset(FPS, F_END)
C.palette("doom")
C.studio(mat_size=(3.6, 3.0), mat_loc=(0, 0.2, 0.02))

# ------------------------------------------------------------------ materials
M_RED = C.clay("press_red", (0.78, 0.09, 0.12), rough=0.5, bump=0.2, thumb=0.15)
M_STEEL = C.steel("steel")
M_YEL = C.clay("plate_yel", (1.0, 0.8, 0.05), rough=0.55, bump=0.15, thumb=0.1)
M_INK = C.clay("ink", (0.04, 0.04, 0.045), rough=0.5, bump=0.05, thumb=0.0, var=0.01)
M_PAPER = C.clay("paper", (0.96, 0.95, 0.9), rough=0.8, bump=0.1, thumb=0.05, var=0.02)
M_CALRED = C.clay("cal_red", (0.85, 0.08, 0.1), rough=0.6, bump=0.15, thumb=0.1)
M_BEAD = C.clay("bead_formula", (0.86, 0.12, 0.14), rough=0.5, bump=0.3, thumb=0.3)
M_REAL = C.clay("bead_real", (0.97, 0.96, 0.93), rough=0.5, bump=0.3, thumb=0.3)
M_STAND = C.clay("stand", (0.15, 0.13, 0.13), rough=0.4, thumb=0.05)

def earth_mat():
    m = bpy.data.materials.new("earth"); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links; p = N["Principled BSDF"]; p.inputs["Roughness"].default_value = 0.6
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.8
    nz.inputs["Detail"].default_value = 3; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "CONSTANT"
    rp.color_ramp.elements[0].color = (0.08, 0.32, 0.78, 1); rp.color_ramp.elements[1].position = 0.56
    rp.color_ramp.elements[1].color = (0.22, 0.62, 0.22, 1)
    L.new(nz.outputs["Fac"], rp.inputs["Fac"]); L.new(rp.outputs["Color"], p.inputs["Base Color"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 50; L.new(tc.outputs["Object"], fine.inputs["Vector"])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.35; b.inputs["Distance"].default_value = 0.01
    L.new(fine.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    return m

# ------------------------------------------------------------------ earth on a stand
EC, ER = Vector((0.15, 0.35, 0.68)), 0.46
stand = C.cylinder("stand", 0.22, 0.18, (EC.x, EC.y, 0.13), r2=0.14); C.set_mats(stand, [M_STAND])
earth = C.uvsphere("earth", ER, EC, seg=64, rings=40); C.set_mats(earth, [earth_mat()])
earth.rotation_euler = (0.3, 0.2, 0)

# ------------------------------------------------------------------ hydraulic press
PX = EC.x
for sx in (-1, 1):
    col = C.cylinder(f"col{sx}", 0.09, 3.1, (PX + 0.95 * sx, EC.y, 1.57)); C.set_mats(col, [M_STEEL])
    foot = C.box(f"foot{sx}", (0.36, 0.5, 0.12), (PX + 0.95 * sx, EC.y, 0.08), bevel=0.03); C.set_mats(foot, [M_RED])
beam = C.box("beam", (2.3, 0.62, 0.4), (PX, EC.y, 3.15), bevel=0.05); C.set_mats(beam, [M_RED])
housing = C.cylinder("housing", 0.26, 0.55, (PX, EC.y, 2.7)); C.set_mats(housing, [M_RED])
ram = C.box("ram", (1.62, 0.78, 0.2), (PX, EC.y, 0), bevel=0.03); C.set_mats(ram, [M_STEEL])
rod = C.cylinder("rod", 0.13, 1.1, (PX, EC.y, 0.65)); C.set_mats(rod, [M_STEEL]); C.parent(rod, ram)
# label plate on the ram front, hinged at its left end so it can swing down and fall
plate_piv = C.link(bpy.data.objects.new("plate_piv", None)); plate_piv.location = (PX - 0.62, EC.y - 0.41, 0)
plate = C.box("plate", (1.22, 0.04, 0.17), (PX, EC.y - 0.41, 0), bevel=0.012); C.set_mats(plate, [M_YEL])
ptxt = C.text3d("plate_txt", "1960 FORMULA", 0.13, (PX, EC.y - 0.435, 0), extrude=0.008); C.set_mats(ptxt, [M_INK])
C.parent(plate, plate_piv); C.parent(ptxt, plate_piv); C.parent(plate_piv, ram)

RAM_TOP, RAM_STOP = 2.1, EC.z + ER + 0.15       # ram bottom heights
def ram_z(n):                                    # lower as the formula's population grows
    k = math.log(max(n, 2.8) / 2.8) / math.log(MAX_BEADS / 2.8)
    return RAM_TOP - (RAM_TOP - RAM_STOP) * min(1, k) ** 1.4 + 0.1
pts = [(1, RAM_TOP + 0.1)]
for f in range(EXP1[0], EXP2[1] + 1, 6):
    pts.append((f, ram_z(formula(year_at(f)) / 1e9)))
pts += [(EXP2[1] + 6, RAM_STOP + 0.25), (SLAM - 4, RAM_STOP + 0.14), (SLAM, RAM_STOP + 0.1)]
for i, f in enumerate(range(SLAM + 1, SLAM + 12)):                     # screech shudder
    pts.append((f, RAM_STOP + 0.1 + (0.025 if i % 2 else -0.012) * (1 - i / 11)))
pts += [(560, RAM_STOP + 0.1), (590, 1.95), (F_END, 1.95)]
C.keys(ram, "location", [(f, (PX, EC.y, z)) for f, z in pts])

# plate: tilts at PLATE, then drops onto the mat
C.keys(plate_piv, "rotation_euler", [(1, (0, 0, 0)), (PLATE, (0, 0, 0)), (PLATE + 4, (0, 0.25, 0)), (PLATE + 8, (0, 0.18, 0)),
                                    (PLATE + 20, (0, 0.18, 0)), (PLATE + 26, (0, 1.75, 0)), (PLATE + 31, (0, 1.38, 0)),
                                    (PLATE + 36, (0, 1.62, 0)), (PLATE + 41, (0, 1.52, 0)), (PLATE + 46, (0, 1.57, 0))])

# ------------------------------------------------------------------ population beads (1 bead = 1 billion)
BR = 0.052
def fib_cap(n):
    """Points on the earth's upper surface, top first."""
    out, ga = [], math.pi * (3 - math.sqrt(5))
    for i in range(3000):
        z = 1 - (i + 0.5) / 3000 * 2; r = math.sqrt(1 - z * z); th = ga * i
        out.append(Vector((r * math.cos(th), r * math.sin(th), z)))
    out = [p for p in out if p.z > -0.4]
    out.sort(key=lambda p: -p.z)
    keep = []
    for p in out:                                  # thin out so beads don't overlap
        if all((p - q).length > 2.15 * BR / ER for q in keep): keep.append(p)
    return keep[:n]
spots = fib_cap(MAX_BEADS)
# 1 ball = 1 billion people: the count on screen must match the caption (Codex review PR #1)
assert len(spots) == MAX_BEADS, f"only {len(spots)} ball positions for {MAX_BEADS} balls"
drops = bead_drop_frames()
red_beads, white_beads = [], []
last = 0
for i, n in enumerate(spots):
    f0 = max(drops[i] if i < len(drops) else EXP2[1], last + (2 if i < 12 else 0)) + random.randint(0, 2)
    last = f0
    rest = EC + n * (ER + BR * 0.75)
    b = C.uvsphere(f"bead{i}", BR, rest, seg=20, rings=12); C.set_mats(b, [M_BEAD])
    up = rest + Vector((0, 0, 1.6))
    C.keys(b, "location", [(1, tuple(up)), (f0, tuple(up)), (f0 + 5, tuple(rest))])
    C.keys(b, "scale", [(f0 + 4, (1, 1, 1)), (f0 + 5, (1.25, 1.25, 0.7)), (f0 + 8, (0.95, 0.95, 1.08)), (f0 + 10, (1, 1, 1))])
    C.show_between(b, f0, REAL if i < REAL_BEADS else None)
    if i >= REAL_BEADS:                            # formula-only beads pop away after the reveal
        g = REAL + 4 + int((i - REAL_BEADS) * 0.6)
        C.keys(b, "scale", [(g, (1, 1, 1)), (g + 3, (1.3, 1.3, 1.3)), (g + 6, (0.01, 0.01, 0.01))])
        C.show_between(b, f0, g + 6)
    red_beads.append(b)
    if i < REAL_BEADS:                             # the real population, in white, stays
        w = C.uvsphere(f"real{i}", BR, rest, seg=20, rings=12); C.set_mats(w, [M_REAL]); C.show_between(w, REAL)
        C.keys(w, "scale", [(REAL, (1.3, 1.3, 1.3)), (REAL + 4, (1, 1, 1))])

# ------------------------------------------------------------------ desk calendar (front-left)
CAL = Vector((-1.12, -0.55, 0.04))
base = C.box("cal_base", (0.66, 0.44, 0.1), CAL + Vector((0, 0.05, 0.05)), bevel=0.03); C.set_mats(base, [M_STAND])
back = C.box("cal_back", (0.62, 0.04, 0.78), CAL + Vector((0, 0.2, 0.47)), bevel=0.02); C.set_mats(back, [M_STAND])
rings = [C.cylinder(f"ring{k}", 0.025, 0.06, CAL + Vector((x, 0.06, 0.86))) for k, x in enumerate((-0.18, 0.18))]
for r in rings: r.rotation_euler = (math.radians(90), 0, 0); C.set_mats(r, [M_STEEL])
HINGE = CAL + Vector((0, 0.06, 0.84))
def page(name, top, big, bottom, y_off, big_col=M_INK):
    piv = C.link(bpy.data.objects.new(name, None)); piv.location = HINGE + Vector((0, y_off, 0))
    p = C.box(name + "_p", (0.56, 0.012, 0.7), piv.location + Vector((0, 0, -0.36)), bevel=0.006); C.set_mats(p, [M_PAPER])
    hdr = C.box(name + "_h", (0.56, 0.016, 0.12), piv.location + Vector((0, -0.002, -0.07)), bevel=0.006); C.set_mats(hdr, [M_CALRED])
    y = piv.location.y - 0.012
    t1 = C.text3d(name + "_t1", top, 0.085, (piv.location.x, y - 0.004, piv.location.z - 0.075), extrude=0.004); C.set_mats(t1, [M_PAPER])
    t2 = C.text3d(name + "_t2", big, 0.36, (piv.location.x, y, piv.location.z - 0.36), extrude=0.008); C.set_mats(t2, [big_col])
    t3 = C.text3d(name + "_t3", bottom, 0.085, (piv.location.x, y, piv.location.z - 0.62), extrude=0.004); C.set_mats(t3, [M_INK])
    for o in (p, hdr, t1, t2, t3): C.parent(o, piv)
    return piv
# back to front: 2032 page (revealed at the end), doomsday page, then three pages that flip away first
p2032 = page("pg2032", "SAT", "13", "NOV 2032", 0.06)
pdoom = page("pgdoom", "FRI", "13", "NOV 2026", 0.02)
early = [page(f"pg{k}", d, n, m, 0.02 - 0.04 * k) for k, (d, n, m) in enumerate([("TUE", "27", "OCT 2026"), ("SUN", "1", "NOV 2026"), ("MON", "9", "NOV 2026")][::-1], 1)][::-1]
def flip(piv, f0, dur=8):
    C.keys(piv, "rotation_euler", [(1, (0, 0, 0)), (f0, (0, 0, 0)), (f0 + dur // 2, (math.radians(-110), 0, 0)),
                                   (f0 + dur, (math.radians(-205), 0, 0))])
    def hide_tree(o):
        if o.type != "EMPTY": C.show_between(o, 1, f0 + dur + 1)
        for c in o.children: hide_tree(c)
    hide_tree(piv)
for piv, f0 in zip(early, CAL_FLIPS):
    flip(piv, f0)
# red circle drawn around "13"
circ = C.link(bpy.data.objects.new("circle", bpy.data.curves.new("circle", "CURVE")))
cu = circ.data; cu.dimensions = "3D"; cu.bevel_depth = 0.018; cu.bevel_resolution = 4
sp = cu.splines.new("POLY"); NPT = 40; sp.points.add(NPT - 1)
for k in range(NPT):
    a = k / (NPT - 1) * 2 * math.pi * 1.08 + 0.6
    sp.points[k].co = (0.2 * math.cos(a), 0.0, 0.17 * math.sin(a) + 0.006 * math.sin(5 * a), 1)
circ.location = HINGE + Vector((0, 0.02 - 0.03, -0.36)); C.set_mats(circ, [M_CALRED])
cu.bevel_factor_mapping_end = "SPLINE"
cu.bevel_factor_end = 0.0; cu.keyframe_insert("bevel_factor_end", frame=CIRCLE[0])
cu.bevel_factor_end = 1.0; cu.keyframe_insert("bevel_factor_end", frame=CIRCLE[1])
C.parent(circ, pdoom)
flip(pdoom, FLIP_2032, 10)

# ------------------------------------------------------------------ camera & light
cam, focus = C.camera(lens=45, fstop=4.0)
C.lights(focus)
CLOSE = (Vector((CAL.x + 0.12, CAL.y - 1.75, 0.95)), Vector((CAL.x, CAL.y + 0.05, 0.78)))
WIDE = (Vector((0.95, -5.0, 2.05)), Vector((0.05, 0.3, 1.45)))
LOW = (Vector((0.75, -3.7, 1.55)), Vector((0.15, 0.35, 1.25)))
def at(f, pose):
    cam.location = pose[0]; cam.keyframe_insert("location", frame=f)
    focus.location = pose[1]; focus.keyframe_insert("location", frame=f)
at(1, CLOSE); at(HOOK[1] - 6, CLOSE); at(SETUP[0] + 60, WIDE); at(EXP1[1], WIDE)
at(EXP2[1] - 20, LOW); at(SLAM - 1, LOW)
rng = random.Random(4)
for f in range(SLAM, SLAM + 10):
    a = 0.05 * (1 - (f - SLAM) / 10)
    cam.location = LOW[0] + Vector((rng.uniform(-a, a), rng.uniform(-a, a), rng.uniform(-a, a))); cam.keyframe_insert("location", frame=f)
at(SLAM + 12, LOW); at(PLATE - 20, WIDE); at(OUTRO[0], WIDE); at(OUTRO[0] + 16, CLOSE); at(F_END, CLOSE)

C.setup_render()
C.run(os.path.join(HERE, "out"))
