"""덕트 테이프 편 장면: 선반 위 3단 단면 실험대 (무방비 / 모래주머니 / 덕트 테이프).
각 칸 왼쪽 = 바깥(물이 차오름), 가운데 = 문 단면, 오른쪽 = 집 안(새어 들어온 물)."""
import os, sys, math, random, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine")); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import clay as C
from timeline import *

random.seed(5)
sc = C.reset(FPS, F_END)
C.palette("flood")
C.studio(mat_size=(3.4, 2.0), mat_loc=(0, 0.1, 0.02))

M_SHELF = C.clay("shelf", (0.55, 0.36, 0.2), rough=0.6, bump=0.25, thumb=0.2)
M_WALL = C.clay("wall", (0.93, 0.92, 0.88), rough=0.75, bump=0.15, thumb=0.15, var=0.02)
M_FLOOR = C.clay("floor", (0.72, 0.7, 0.66), rough=0.75, bump=0.2, thumb=0.15)
M_DOOR = C.clay("door", (0.45, 0.25, 0.12), rough=0.55, bump=0.2, thumb=0.15)
M_FRAME = C.clay("frame", (0.98, 0.98, 0.96), rough=0.6, bump=0.1, thumb=0.1, var=0.01)
M_KNOB = C.glossy("knob", (0.85, 0.65, 0.15), rough=0.25)
M_BAG = C.clay("sandbag", (0.72, 0.6, 0.4), rough=0.8, bump=0.5, thumb=0.35)
M_TIE = C.clay("tie", (0.3, 0.22, 0.12), rough=0.6)
M_TAPE = C.steel("tape", (0.78, 0.8, 0.83), rough=(0.28, 0.42), metallic=0.6)
M_SHEET = C.glossy("sheet", (0.85, 0.9, 0.95), rough=0.15, coat=0.2)
M_SHEET.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.45
M_WATER = C.water("water", (0.08, 0.42, 1.0))
_wp = M_WATER.node_tree.nodes["Principled BSDF"]; _wp.inputs["Transmission Weight"].default_value = 0.8; _wp.inputs["Roughness"].default_value = 0.05
M_SOFA = C.clay("sofa", (0.85, 0.2, 0.25), rough=0.7, bump=0.3, thumb=0.3)
M_RUG = C.clay("rug", (0.95, 0.75, 0.2), rough=0.8, bump=0.2, thumb=0.1)
M_GAUGE = C.clay("gauge", (0.04, 0.04, 0.045), rough=0.5, thumb=0.0)

RIG_W, RIG_D, WALL_H = 2.3, 0.62, 0.62
OUT_X = (-RIG_W / 2 + 0.04, -0.07)        # outside compartment x-range
IN_X = (0.07, RIG_W / 2 - 0.04)           # inside room
MAX_W = 0.36                              # 60 cm of water, drawn to scale with the 0.62 cut-away door
MAX_IN = 0.26                             # inside water for the unprotected door at the end
ROW_Z = [1.84, 0.98, 0.12]                # top → bottom

# leak volume grows with the (pressure-driven) outside level; precompute the normalised integral
cum, acc = {}, 0.0
for f in range(1, F_END + 1):
    acc += water_frac(f) ** 1.5; cum[f] = acc
def leaked(f, frac): return MAX_IN * frac * cum[f] / cum[F_END]

# shelf frame
for sx in (-1, 1):
    C.set_mats(C.box(f"post{sx}", (0.1, 0.7, 2.62), (sx * (RIG_W / 2 + 0.08), 0, 1.33), bevel=0.02), [M_SHELF])
anchors3d = {}

def rig(i, name, frac):
    z0 = ROW_Z[i]
    C.set_mats(C.box(f"board{i}", (RIG_W + 0.26, RIG_D + 0.08, 0.06), (0, 0, z0 - 0.03), bevel=0.015), [M_SHELF])
    C.set_mats(C.box(f"floor{i}", (RIG_W, RIG_D, 0.05), (0, 0, z0 + 0.025), bevel=0.01), [M_FLOOR])
    C.set_mats(C.box(f"back{i}", (RIG_W, 0.04, WALL_H), (0, RIG_D / 2 - 0.02, z0 + 0.05 + WALL_H / 2), bevel=0.01), [M_WALL])
    # door in section: white frame posts + brown door slab, knob on the inside face
    zt = z0 + 0.05
    C.set_mats(C.box(f"door{i}", (0.07, RIG_D - 0.06, WALL_H - 0.02), (0, -0.01, zt + (WALL_H - 0.02) / 2 + 0.012), bevel=0.012), [M_DOOR])
    C.set_mats(C.box(f"sill{i}", (0.16, RIG_D, 0.025), (0, 0, zt + 0.0125), bevel=0.006), [M_FRAME])
    C.set_mats(C.box(f"jamb{i}", (0.12, 0.05, WALL_H), (0, -RIG_D / 2 + 0.025, zt + WALL_H / 2), bevel=0.01), [M_FRAME])
    knob = C.uvsphere(f"knob{i}", 0.035, (0.075, -0.1, zt + 0.3)); C.set_mats(knob, [M_KNOB])
    # depth gauge on the back wall (outside side): 0 / 60 cm ticks
    for k in range(7):
        h = 0.03 if k % 2 == 0 else 0.018
        C.set_mats(C.box(f"tick{i}_{k}", (h * 2, 0.01, 0.006), (OUT_X[0] + 0.06, RIG_D / 2 - 0.045, zt + MAX_W * k / 6), bevel=0), [M_GAUGE])
    # outside water: grows from the floor
    wx = (OUT_X[0] + OUT_X[1]) / 2; ww = OUT_X[1] - OUT_X[0]
    wat = C.box(f"water_out{i}", (ww, RIG_D - 0.08, 1.0), (wx, -0.01, zt), bevel=0.02)
    for v in wat.data.vertices: v.co.z += 0.5           # origin at the bottom so scale.z = height
    C.set_mats(wat, [M_WATER])
    pts = [(1, (1, 1, 0.001))] + [(f, (1, 1, max(0.001, water_frac(f) * MAX_W))) for f in range(FILL[0], FILL[1] + 1, 6)] + [(F_END, (1, 1, MAX_W))]
    C.keys(wat, "scale", pts)
    C.show_between(wat, FILL[0] + 4)
    # inside water (leak) + the stream under the door
    ix = (IN_X[0] + IN_X[1]) / 2; iw = IN_X[1] - IN_X[0]
    win = C.box(f"water_in{i}", (iw, RIG_D - 0.08, 1.0), (ix, -0.01, zt), bevel=0.01)
    for v in win.data.vertices: v.co.z += 0.5
    C.set_mats(win, [M_WATER])
    C.keys(win, "scale", [(1, (1, 1, 0.001))] + [(f, (1, 1, max(0.001, leaked(f, frac)))) for f in range(FILL[0], F_END + 1, 6)])
    first = next((f for f in range(FILL[0], F_END) if leaked(f, frac) > 0.004), None)
    if first: C.show_between(win, first)
    else: C.show_between(win, F_END + 1)
    # a little armchair so the right side reads as "inside the house"
    chair = C.blob(f"chair{i}", [((0, 0, 0.07), (0.16, 0.11, 0.07)), ((0, 0.09, 0.17), (0.16, 0.04, 0.12)),
                                 ((-0.15, 0, 0.12), (0.035, 0.11, 0.06)), ((0.15, 0, 0.12), (0.035, 0.11, 0.06))], voxel=0.012)
    chair.location = (IN_X[1] - 0.3, 0.12, zt); C.set_mats(chair, [M_SOFA])
    rug = C.box(f"rug{i}", (0.42, 0.34, 0.008), (IN_X[1] - 0.32, -0.08, zt + 0.004), bevel=0.003); C.set_mats(rug, [M_RUG])
    stream = C.blob(f"stream{i}", [((0.12, -0.02, 0.0), (0.1, 0.22, 0.03)), ((0.24, -0.02, 0.0), (0.12, 0.2, 0.02))], voxel=0.012)
    stream.location = (0, 0, zt + 0.015); C.set_mats(stream, [M_WATER])
    thick = max(0.08, math.sqrt(frac))
    C.keys(stream, "scale", [(1, (0.01, 0.01, 0.01)), (FILL[0] + 30, (0.01, 0.01, 0.01)), (FILL[0] + 48, (thick, thick, thick)),
                             (F_END, (thick, thick, thick))])
    if frac < 0.1:                                      # tape door: only a small puddle by the door
        pud = C.blob(f"puddle{i}", [((0.2, -0.05, 0), (0.16, 0.2, 0.012))], voxel=0.01); pud.location = (0, 0, zt + 0.006)
        C.set_mats(pud, [M_WATER])
        C.keys(pud, "scale", [(1, (0.01, 0.01, 0.01)), (FILL[0] + 80, (0.01, 0.01, 0.01)), (RESULT[0], (1, 1, 1))])
    anchors3d[f"row{i}"] = (OUT_X[0] + 0.05, -RIG_D / 2, zt + WALL_H - 0.08)
    anchors3d[f"in{i}"] = (ix, -RIG_D / 2, zt + 0.22)
    return zt

zts = [rig(i, n, fr) for i, (n, fr) in enumerate(ROWS)]

# ---- row 2: sandbags (+ plastic sheet) piled against the outside of the door
zt = zts[1]
bags = [(-0.16, y, 0.06 + 0.105 * L) for L in range(4) for y in (-0.18, 0.0, 0.18)] + \
       [(-0.34, y, 0.06 + 0.105 * L) for L in range(2) for y in (-0.18, 0.0, 0.18)]
bags.sort(key=lambda b: (b[2], b[0]))
for k, (x, y, h) in enumerate(bags):
    bag = C.blob(f"bag{k}", [((0, 0, 0), (0.095, 0.1, 0.058)), ((0, 0.085, 0.0), (0.06, 0.04, 0.042))], voxel=0.012)
    tie = C.uvsphere(f"tie{k}", 0.02, (0, 0.125, 0.0)); C.set_mats(tie, [M_TIE])
    C.set_mats(bag, [M_BAG]); C.parent(tie, bag)
    rest = Vector((x, y, zt + h)); bag.rotation_euler = (random.uniform(-0.08, 0.08), 0, random.uniform(-0.25, 0.25))
    f0 = 4 + 2 * k
    C.keys(bag, "location", [(1, tuple(rest + Vector((0, 0, 1.2)))), (f0, tuple(rest + Vector((0, 0, 1.2)))), (f0 + 4, tuple(rest))])
    C.keys(bag, "scale", [(f0 + 3, (1, 1, 1)), (f0 + 4, (1.15, 1.1, 0.75)), (f0 + 7, (0.97, 0.98, 1.06)), (f0 + 9, (1, 1, 1))])
sheet = C.box("sheet", (0.012, RIG_D - 0.1, 0.46), (-0.045, -0.01, zt + 0.23), bevel=0.004); C.set_mats(sheet, [M_SHEET])
C.show_between(sheet, 4 + 2 * len(bags) + 4)

# ---- row 3: duct tape over the gaps, on the outside face of the door + the roll
zt = zts[2]
strips = [C.box(f"strip{k}", (0.012, RIG_D - 0.08, 0.16), (-0.042, -0.01, zt + 0.08 + k * 0.14), bevel=0.003) for k in range(2)]
floor_strip = C.box("strip_floor", (0.16, RIG_D - 0.08, 0.008), (-0.12, -0.01, zt + 0.006), bevel=0.002)
for s, f0 in zip(strips + [floor_strip], TAPE_STRIPS + [TAPE_STRIPS[0]]):
    C.set_mats(s, [M_TAPE])
    C.keys(s, "scale", [(1, (1, 0.01, 1)), (f0, (1, 0.01, 1)), (f0 + 4, (1, 1.05, 1)), (f0 + 6, (1, 1, 1))])
roll = C.link(bpy.data.objects.new("roll", None))
bm_t = bpy.data.meshes.new("torus")
import bmesh
bm = bmesh.new()
R1, R2, NS = 0.11, 0.045, 32
rings_v = []
for a in range(NS):
    th = a / NS * 2 * math.pi
    ring = []
    for b in range(16):
        ph = b / 16 * 2 * math.pi
        r = R1 + R2 * math.cos(ph) * 0.6
        ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), R2 * math.sin(ph) * 1.4)))
    rings_v.append(ring)
for a in range(NS):
    for b in range(16):
        bm.faces.new((rings_v[a][b], rings_v[(a + 1) % NS][b], rings_v[(a + 1) % NS][(b + 1) % 16], rings_v[a][(b + 1) % 16]))
for f_ in bm.faces: f_.smooth = True
torus = C.mesh_obj("roll_mesh", bm); C.set_mats(torus, [M_TAPE])
C.parent(torus, roll)
rest = Vector((0.55, -0.1, zt + R2 * 1.4))
C.keys(roll, "location", [(1, tuple(rest + Vector((0, 0, 1.3)))), (TAPE_ROLL, tuple(rest + Vector((0, 0, 1.3)))),
                          (TAPE_ROLL + 5, tuple(rest)), (TAPE_ROLL + 9, tuple(rest + Vector((0, 0, 0.12)))), (TAPE_ROLL + 13, tuple(rest))])
C.keys(roll, "scale", [(TAPE_ROLL + 4, (1, 1, 1)), (TAPE_ROLL + 5, (1.2, 1.2, 0.7)), (TAPE_ROLL + 8, (0.95, 0.95, 1.1)),
                       (TAPE_ROLL + 13, (1.1, 1.1, 0.85)), (TAPE_ROLL + 16, (1, 1, 1))])

# ------------------------------------------------------------------ contestant intro: turntable off to the right
P = Vector((5.0, 0.2, 0.0))
M_TT = C.clay("turntable", (0.96, 0.95, 0.92), rough=0.6, bump=0.15, thumb=0.1)
C.set_mats(C.cylinder("tt_base", 0.62, 0.1, P + Vector((0, 0, 0.05))), [M_SHELF])
spin = C.link(bpy.data.objects.new("spin", None)); spin.location = P + Vector((0, 0, 0.1))
top = C.cylinder("tt_top", 0.58, 0.05, P + Vector((0, 0, 0.125))); C.set_mats(top, [M_TT]); C.parent(top, spin)
C.keys(spin, "rotation_euler", [(INTRO[0], (0, 0, -0.6)), (INTRO[1], (0, 0, -0.6 + 2 * math.pi * 1.2))], interp="LINEAR")
Z = P.z + 0.15
items = []
# 1) an ordinary front door
d = [C.box("c_door", (0.5, 0.07, 0.92), P + Vector((0, 0, Z + 0.46)), bevel=0.015),
     C.box("c_post_l", (0.06, 0.1, 1.0), P + Vector((-0.28, 0, Z + 0.5)), bevel=0.01),
     C.box("c_post_r", (0.06, 0.1, 1.0), P + Vector((0.28, 0, Z + 0.5)), bevel=0.01),
     C.box("c_head", (0.62, 0.1, 0.06), P + Vector((0, 0, Z + 1.0)), bevel=0.01),
     C.uvsphere("c_knob", 0.04, P + Vector((0.17, -0.06, Z + 0.45))),
     C.box("c_panel", (0.34, 0.02, 0.3), P + Vector((0, -0.04, Z + 0.68)), bevel=0.01)]
for o, m in zip(d, [M_DOOR, M_FRAME, M_FRAME, M_FRAME, M_KNOB, M_DOOR]): C.set_mats(o, [m])
items.append(d)
# 2) sandbags + plastic sheet
g = []
for k, (x, y, z) in enumerate([(-0.2, 0, 0.06), (0, 0, 0.06), (0.2, 0, 0.06), (-0.1, 0, 0.17), (0.1, 0, 0.17), (0, 0, 0.28)]):
    b = C.blob(f"c_bag{k}", [((0, 0, 0), (0.1, 0.13, 0.06)), ((0.0, 0.11, 0), (0.06, 0.04, 0.045))], voxel=0.012)
    b.location = P + Vector((x, y - 0.05, Z + z)); b.rotation_euler = (0, 0, math.radians(90) + random.uniform(-0.2, 0.2))
    C.set_mats(b, [M_BAG]); g.append(b)
sh = C.box("c_sheet", (0.8, 0.5, 0.01), P + Vector((0, -0.05, Z + 0.006)), bevel=0.004); C.set_mats(sh, [M_SHEET]); g.append(sh)
items.append(g)
# 3) a roll of duct tape with a strip pulled out
big = torus.copy(); big.data = torus.data.copy(); C.link(big); big.parent = None
big.location = P + Vector((0, 0.05, Z + 0.225)); big.rotation_euler = (math.radians(90), 0, 0); big.scale = (1.7, 1.7, 1.7)
strip = C.box("c_strip", (0.2, 0.34, 0.006), P + Vector((0.0, -0.18, Z + 0.004)), bevel=0.002)
C.set_mats(strip, [M_TAPE])
items.append([big, strip])
for (f0, f1), objs in zip(INTRO_ITEMS, items):
    for o in objs:
        C.parent(o, spin)
        sc0 = tuple(o.scale)
        C.keys(o, "scale", [(f0, tuple(v * 0.01 for v in sc0)), (f0 + 5, tuple(v * 1.15 for v in sc0)), (f0 + 9, sc0),
                            (f1 - 4, sc0), (f1, tuple(v * 0.01 for v in sc0))])
        C.show_between(o, f0, f1 + 1)

# ------------------------------------------------------------------ camera
cam, focus = C.camera(lens=40, fstop=None)
C.lights(focus)
CLOSE = (Vector((0.12, -2.3, 1.2)), Vector((0.02, 0, 0.66)))
WIDE = (Vector((0.18, -5.1, 1.95)), Vector((0.0, 0, 1.62)))
TIGHT = (Vector((0.1, -2.7, 0.95)), Vector((0.05, 0, 0.5)))
def at(f, pose):
    cam.location = pose[0]; cam.keyframe_insert("location", frame=f)
    focus.location = pose[1]; focus.keyframe_insert("location", frame=f)
PODIUM = (P + Vector((0.0, -2.6, 1.15)), P + Vector((0, 0, 0.55)))
PODIUM2 = (P + Vector((0.0, -2.2, 1.05)), P + Vector((0, 0, 0.55)))
at(1, CLOSE); at(INTRO[0] - 1, CLOSE); at(INTRO[0], PODIUM); at(INTRO[1] - 1, PODIUM2); at(INTRO[1], CLOSE)
at(SETUP[0] + 50, WIDE); at(RESULT[0] + 60, WIDE)
at(RESULT[0] + 90, TIGHT); at(RESULT[1] - 10, TIGHT); at(CATCH[0] + 20, WIDE); at(F_END, WIDE)
for ob in (cam, focus):                       # hard cuts in and out of the intro (no in-between frames)
    for fc in C.fcurves(ob):
        for kp in fc.keyframe_points:
            if int(kp.co[0]) in (INTRO[0] - 1, INTRO[1] - 1):
                kp.interpolation = "CONSTANT"

C.setup_render()
# label anchors (screen space, at the wide shot) for the composite step
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
sc.frame_set(RESULT[0]); bpy.context.view_layer.update()
an = {k: (lambda v: [v.x, 1 - v.y])(world_to_camera_view(sc, cam, Vector(p))) for k, p in anchors3d.items()}
json.dump(an, open(os.path.join(HERE, "out", "anchors.json"), "w"))

C.run(os.path.join(HERE, "out"))
