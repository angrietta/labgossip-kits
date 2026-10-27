"""CLAY LAB 공용 엔진: 점토 재질, 노란 스튜디오, 카메라·조명, GPU 감지, 렌더 모드.
각 에피소드의 scene.py가 이 파일을 불러서 장면만 만든다.

렌더 모드 (Blender 실행 시 -- 뒤 인자):
  sample f1 f2 ...   지정 프레임만 렌더 (out/frames/####.png). 요약 이미지는 composite.py가 만든다
  anim a b           a~b 프레임을 두 장마다 렌더 (이미 있는 장은 건너뜀 → 중단해도 이어서)
"""
import sys, os, math, random, time
import bpy, bmesh
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
STEP = 1            # 초당 24장 전부 렌더 (12장은 카메라가 움직일 때 끊겨 보임)
FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

sc = None

def reset(fps=24, f_end=240):
    global sc
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = fps
    sc.frame_start, sc.frame_end = 1, f_end
    return sc

# ------------------------------------------------------------------ geometry helpers
def link(ob):
    sc.collection.objects.link(ob); return ob

def mesh_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me))

def box(name, size, loc, bevel=0.0, seg=3):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = mesh_obj(name, bm); ob.location = loc
    if bevel:
        m = ob.modifiers.new("bv", "BEVEL"); m.width = bevel; m.segments = seg
        ob.modifiers.new("ws", "WEIGHTED_NORMAL")
    return ob

def uvsphere(name, r, loc, scale=(1, 1, 1), seg=40, rings=24):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    for f in bm.faces: f.smooth = True
    ob = mesh_obj(name, bm); ob.location = loc; ob.scale = scale; return ob

def cylinder(name, r, depth, loc, seg=40, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    for f in bm.faces: f.smooth = len(f.verts) == 4
    ob = mesh_obj(name, bm); ob.location = loc; return ob

def bake(ob):
    """Apply modifiers/transforms into a fresh mesh (works headless)."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    me.transform(ob.matrix_world)
    new = link(bpy.data.objects.new(ob.name, me))
    bpy.data.objects.remove(ob, do_unlink=True)
    return new

def blob(name, parts, voxel=0.02, smooth_it=12):
    """Union of ellipsoids -> voxel remesh -> smooth: one watertight hand-made clay lump."""
    bm = bmesh.new()
    for c, rad in parts:
        g = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=1.0)
        bmesh.ops.scale(bm, vec=Vector(rad), verts=g["verts"]); bmesh.ops.translate(bm, vec=Vector(c), verts=g["verts"])
    ob = mesh_obj(name, bm)
    rm = ob.modifiers.new("rm", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = voxel; rm.use_smooth_shade = True
    sm = ob.modifiers.new("sm", "LAPLACIANSMOOTH"); sm.lambda_factor = 1.0; sm.iterations = smooth_it; sm.use_volume_preserve = True
    ob = bake(ob)
    for p in ob.data.polygons: p.use_smooth = True
    return ob

def set_mats(ob, mats):
    ob.data.materials.clear()
    for m in mats: ob.data.materials.append(m)
    return ob

def text3d(name, body, size, loc, rot=(math.radians(90), 0, 0), font="Anton-Regular.ttf", extrude=0.02, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body
    cu.font = bpy.data.fonts.load(os.path.join(FONTS, font), check_existing=True)
    cu.size = size; cu.extrude = extrude; cu.bevel_depth = extrude * 0.3; cu.bevel_resolution = 2
    cu.align_x = align; cu.align_y = "CENTER"
    ob = link(bpy.data.objects.new(name, cu)); ob.location = loc; ob.rotation_euler = rot
    return ob

def parent(child, par):
    bpy.context.view_layer.update()          # new objects have a stale matrix_world until updated
    mw = child.matrix_world.copy()
    child.parent = par; child.matrix_parent_inverse = par.matrix_world.inverted()
    child.matrix_world = mw

# ------------------------------------------------------------------ palettes (편마다 색 톤을 다르게)
PALETTES = {
    "classic": dict(back=(0.95, 0.62, 0.02), mat=((0.09, 0.33, 0.26), (0.75, 0.88, 0.8)),
                    key=(1, 0.97, 0.92), fill=(0.9, 0.95, 1), rim=(1, 1, 1), world=(1, 0.92, 0.75), power=1.0),
    # 종말: 어두운 남보라 무대 + 주황 석양 조명 + 자홍 역광
    "doom":    dict(back=(0.16, 0.09, 0.3), mat=((0.06, 0.05, 0.08), (0.42, 0.3, 0.5)),
                    key=(1, 0.62, 0.32), fill=(0.55, 0.45, 1), rim=(1, 0.25, 0.6), world=(0.35, 0.22, 0.5), power=1.15),
    # 홍수: 비 오는 날 회청색 무대 + 차가운 조명, 시멘트색 바닥
    "flood":   dict(back=(0.4, 0.5, 0.58), mat=((0.33, 0.34, 0.36), (0.6, 0.62, 0.64)),
                    key=(0.92, 0.97, 1), fill=(0.75, 0.88, 1), rim=(1, 0.95, 0.85), world=(0.7, 0.8, 0.9), power=1.0),
}
PAL = PALETTES["classic"]
def palette(name):
    global PAL
    PAL = PALETTES[name]

# ------------------------------------------------------------------ materials
def clay(name, rgb, rough=0.62, bump=0.35, thumb=0.25, var=0.06):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    p = N["Principled BSDF"]; p.inputs["Roughness"].default_value = rough
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = [max(0, c - var) for c in rgb] + [1]
    ramp.color_ramp.elements[1].color = [min(1, c + var) for c in rgb] + [1]
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], p.inputs["Base Color"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 60; fine.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], fine.inputs["Vector"])
    vor = N.new("ShaderNodeTexVoronoi"); vor.feature = "SMOOTH_F1"; vor.inputs["Scale"].default_value = 4.0
    L.new(tc.outputs["Object"], vor.inputs["Vector"])
    b1 = N.new("ShaderNodeBump"); b1.inputs["Strength"].default_value = bump; b1.inputs["Distance"].default_value = 0.004
    L.new(fine.outputs["Fac"], b1.inputs["Height"])
    b2 = N.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = thumb; b2.inputs["Distance"].default_value = 0.02
    L.new(vor.outputs["Distance"], b2.inputs["Height"]); L.new(b1.outputs["Normal"], b2.inputs["Normal"])
    L.new(b2.outputs["Normal"], p.inputs["Normal"])
    return m

def glossy(name, rgb, rough=0.1, coat=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = list(rgb) + [1]; p.inputs["Roughness"].default_value = rough
    p.inputs["Coat Weight"].default_value = coat
    return m

def steel(name, rgb=(0.32, 0.34, 0.38), rough=(0.4, 0.55), metallic=0.4):
    """Clay-style steel: low mirror reflection so it reads as a solid slab, not glass."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = list(rgb) + [1]; p.inputs["Metallic"].default_value = metallic
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Detail"].default_value = 4
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (60, 1.5, 60)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeMapRange"); r.inputs["To Min"].default_value = rough[0]; r.inputs["To Max"].default_value = rough[1]
    nt.links.new(nz.outputs["Fac"], r.inputs["Value"]); nt.links.new(r.outputs["Result"], p.inputs["Roughness"])
    return m

def water(name, rgb=(0.12, 0.45, 0.85)):
    """Stylised clay-world water: glossy, slightly see-through blue jelly with soft ripples."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links; p = N["Principled BSDF"]
    p.inputs["Base Color"].default_value = list(rgb) + [1]; p.inputs["Roughness"].default_value = 0.08
    p.inputs["Transmission Weight"].default_value = 0.55; p.inputs["IOR"].default_value = 1.2
    p.inputs["Coat Weight"].default_value = 0.4
    tc = N.new("ShaderNodeTexCoord"); w = N.new("ShaderNodeTexNoise"); w.inputs["Scale"].default_value = 6; w.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], w.inputs["Vector"])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.25; b.inputs["Distance"].default_value = 0.02
    L.new(w.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    return m

def cutting_mat(name="mat_grid", period=0.05, colors=None):
    dark, light = colors or PAL["mat"]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links; p = N["Principled BSDF"]; p.inputs["Roughness"].default_value = 0.75
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs["Vector"])
    def line(axis):
        mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 1 / period
        L.new(sep.outputs[axis], mul.inputs[0])
        fr = N.new("ShaderNodeMath"); fr.operation = "FRACT"; L.new(mul.outputs[0], fr.inputs[0])
        lt = N.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.035
        L.new(fr.outputs[0], lt.inputs[0]); return lt
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L.new(line("X").outputs[0], mx.inputs[0]); L.new(line("Y").outputs[0], mx.inputs[1])
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "CONSTANT"
    rp.color_ramp.elements[0].color = list(dark) + [1]; rp.color_ramp.elements[1].position = 0.5
    rp.color_ramp.elements[1].color = list(light) + [1]
    L.new(mx.outputs[0], rp.inputs["Fac"]); L.new(rp.outputs["Color"], p.inputs["Base Color"])
    return m

# ------------------------------------------------------------------ studio, camera, light
def studio(mat_size=(3.4, 3.0), mat_loc=(0, 0.15, 0.02), back=None):
    back = back or PAL["back"]
    bm = bmesh.new()
    prof = [(y, 0.0) for y in (-14, -6, -2, 1.5)]
    R = 3.0
    for k in range(1, 13):
        a = k / 12 * math.pi / 2; prof.append((1.5 + R * math.sin(a), R - R * math.cos(a)))
    prof += [(1.5 + R, 12.0)]
    rows = [[bm.verts.new((x, y, z)) for y, z in prof] for x in (-18, 18)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    for f in bm.faces: f.smooth = True
    set_mats(mesh_obj("cyc", bm), [clay("backdrop", back, rough=0.9, bump=0.05, thumb=0.0, var=0.01)])
    if mat_size:
        mg = box("cutmat", (mat_size[0], mat_size[1], 0.04), mat_loc, bevel=0.015)
        set_mats(mg, [cutting_mat()])

def camera(lens=50, fstop=5.6, loc=(0, -5, 2.5), focus_loc=(0, 0, 0.6)):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens; cd.sensor_width = 36
    cd.dof.use_dof = fstop is not None
    cam = link(bpy.data.objects.new("cam", cd)); sc.camera = cam; cam.location = loc
    focus = link(bpy.data.objects.new("focus", None)); focus.location = focus_loc
    if fstop: cd.dof.aperture_fstop = fstop; cd.dof.focus_object = focus
    t = cam.constraints.new("TRACK_TO"); t.target = focus; t.track_axis = "TRACK_NEGATIVE_Z"; t.up_axis = "UP_Y"
    return cam, focus

def lights(focus, scale=1.0):
    def area(name, loc, size, power, color=(1, 1, 1)):
        d = bpy.data.lights.new(name, "AREA"); d.size = size * scale; d.energy = power * scale * scale; d.color = color
        ob = link(bpy.data.objects.new(name, d)); ob.location = [v * scale for v in loc]
        c = ob.constraints.new("TRACK_TO"); c.target = focus; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    pw = PAL["power"]
    area("key", (-3.2, -4.0, 5.2), 4.0, 520 * pw, PAL["key"])
    area("fill", (4.5, -3.5, 2.5), 5.0, 150 * pw, PAL["fill"])
    area("rim", (1.5, 4.5, 4.0), 2.5, 380 * pw, PAL["rim"])
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = list(PAL["world"]) + [1]
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2

# ------------------------------------------------------------------ animation helpers
def keys(ob, path, pts, interp=None):
    """pts = [(frame, value), ...]; value is a float or a tuple."""
    for f, v in pts:
        if isinstance(v, (tuple, list)): getattr(ob, path)[:] = v
        else: setattr(ob, path, v)
        ob.keyframe_insert(path, frame=f)
    if interp and ob.animation_data and ob.animation_data.action:
        for fc in fcurves(ob):
            if fc.data_path == path:
                for kp in fc.keyframe_points: kp.interpolation = interp

def fcurves(ob):
    act = ob.animation_data.action
    try:
        return list(act.fcurves)
    except AttributeError:                   # Blender 5: layered actions
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out += list(bag.fcurves)
        return out

def show_between(ob, f_on, f_off=None):
    ob.hide_render = True; ob.keyframe_insert("hide_render", frame=1)
    ob.hide_render = False; ob.keyframe_insert("hide_render", frame=f_on)
    if f_off:
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=f_off)
    for fc in fcurves(ob):
        if fc.data_path == "hide_render":
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------ render
def setup_render(samples=32):
    r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = 1080, 1920; r.resolution_percentage = 100
    sc.cycles.samples = samples; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.04
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 4
    r.film_transparent = False; r.image_settings.file_format = "PNG"
    r.use_motion_blur = True; r.motion_blur_shutter = 0.5; r.motion_blur_position = "START"          # 움직임이 부드럽게 이어지도록
    sc.view_settings.view_transform = "Standard"; sc.view_settings.exposure = -0.35
    dev = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for backend in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
            try:
                prefs.compute_device_type = backend
            except TypeError:
                continue
            prefs.get_devices()
            if [d for d in prefs.devices if d.type == backend]:
                for d in prefs.devices: d.use = d.type == backend
                sc.cycles.device = "GPU"; dev = backend; break
    except KeyError:
        pass
    if dev == "CPU":
        sc.cycles.device = "CPU"; r.resolution_x, r.resolution_y = 720, 1280; sc.cycles.samples = 12
    if os.environ.get("PREVIEW"):           # quick look: tiny + few samples
        r.resolution_x, r.resolution_y = 360, 640; sc.cycles.samples = 8
    print("RENDER DEVICE:", dev, r.resolution_x, "x", r.resolution_y, "samples", sc.cycles.samples, flush=True)

def run(out_dir):
    os.makedirs(os.path.join(out_dir, "frames"), exist_ok=True)
    mode = ARGS[0] if ARGS else "sample"
    if mode == "sample":
        frames = [int(x) for x in ARGS[1:]]
    elif mode == "anim":
        a = int(ARGS[1]) if len(ARGS) > 1 else 1
        b = int(ARGS[2]) if len(ARGS) > 2 else sc.frame_end
        frames = list(range(a, b + 1, STEP))
    else:
        return
    for f in frames:
        p = os.path.join(out_dir, "frames", f"{f:04d}.png")
        if os.path.exists(p) and mode == "anim":
            continue
        t0 = time.time(); sc.frame_set(f); sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print(f"FRAME {f}/{frames[-1]}  {time.time() - t0:.1f} sec", flush=True)
