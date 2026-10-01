"""Shared helpers for the Blender style stills (run headless on the GPU box).

argv after "--": <work_dir> <samples> <resolution_percent>
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
WORK = ARGS[0] if ARGS else os.path.dirname(__file__)
SAMPLES = int(ARGS[1]) if len(ARGS) > 1 else 128
PCT = int(ARGS[2]) if len(ARGS) > 2 else 100


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_render(res=(1920, 1080), samples=None, exposure=0.0, look="None"):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    chosen = None
    for dev_type in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            if any(d.type == dev_type for d in prefs.devices):
                chosen = dev_type
                break
        except TypeError:
            continue
    for d in prefs.devices:
        d.use = d.type == chosen
    sc.cycles.device = "GPU"
    sc.cycles.samples = samples or SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = PCT
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = look
    sc.view_settings.exposure = exposure
    print("DEVICES", [(d.name, d.type, d.use) for d in prefs.devices])


def world(color, strength=1.0):
    w = bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hexcol(color)
    bg.inputs["Strength"].default_value = strength


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def clay(name, color, rough=0.62, bump=0.22, prints=0.12, sss=0.06, coat=0.0):
    """Plasticine: soft sheen, fine noise grain, voronoi thumb dimples."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = hexcol(color)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Subsurface Radius"].default_value = (0.05, 0.03, 0.02)
    p.inputs["Coat Weight"].default_value = coat
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 90
    noise.inputs["Detail"].default_value = 6
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 7
    mix = nt.nodes.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"
    mix.inputs[1].default_value = prints / max(bump, 1e-3)
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = bump
    b.inputs["Distance"].default_value = 0.02
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    nt.links.new(vor.outputs["Distance"], mix.inputs[0])
    nt.links.new(noise.outputs["Fac"], mix.inputs[2])
    nt.links.new(mix.outputs[0], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def lumpy(obj, strength=0.012, scale=0.35, subsurf=2, seed_offset=0.0):
    """Hand-made imperfection: subdivide, then low-frequency displacement."""
    if subsurf:
        s = obj.modifiers.new("sub", "SUBSURF"); s.levels = s.render_levels = subsurf
    tex = bpy.data.textures.new(obj.name + "_lump", "CLOUDS")
    tex.noise_scale = scale
    d = obj.modifiers.new("lump", "DISPLACE")
    d.texture = tex; d.strength = strength; d.mid_level = 0.5
    d.texture_coords = "GLOBAL"
    obj.location.z += 0  # keep position
    return obj


def smooth(obj):
    if obj.type == "MESH":
        obj.data.shade_smooth()
    return obj


def assign(obj, *mats):
    for m in mats:
        obj.data.materials.append(m)
    return obj


def cove(color_mat, depth=14, width=40, radius=3.0, back_y=4.0, height=14):
    """Seamless photo-studio sweep: floor curving up into the backdrop."""
    prof = [(y, 0.0) for y in (-depth, back_y - radius)]
    for i in range(1, 16):
        a = i / 16 * math.pi / 2
        prof.append((back_y - radius + math.sin(a) * radius, radius - math.cos(a) * radius))
    prof.append((back_y, height))
    me = bpy.data.meshes.new("cove")
    bm = bmesh.new()
    rows = []
    for x in (-width / 2, width / 2):
        rows.append([bm.verts.new((x, y, z)) for y, z in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    bm.to_mesh(me)
    ob = link(bpy.data.objects.new("cove", me))
    smooth(ob)
    assign(ob, color_mat)
    return ob


def area_light(name, loc, target, size, energy, color="#ffffff"):
    L = bpy.data.lights.new(name, "AREA")
    L.size = size; L.energy = energy; L.color = hexcol(color)[:3]
    ob = link(bpy.data.objects.new(name, L))
    ob.location = loc
    look_at(ob, target)
    return ob


def look_at(ob, target):
    d = Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50, dof_target=None, fstop=None):
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens
    ob = link(bpy.data.objects.new("cam", cam))
    ob.location = loc
    look_at(ob, target)
    bpy.context.scene.camera = ob
    if dof_target is not None:
        cam.dof.use_dof = True
        cam.dof.focus_distance = (Vector(dof_target) - Vector(loc)).length
        cam.dof.aperture_fstop = fstop or 2.8
    return ob


def text_mesh(body, font_path, size, extrude, bevel, align="CENTER", spacing=1.0):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(font_path)
    cu.size = size; cu.extrude = extrude
    cu.bevel_depth = bevel; cu.bevel_resolution = 4
    cu.align_x = align; cu.space_character = spacing
    tmp = link(bpy.data.objects.new("tmp_txt", cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    return link(bpy.data.objects.new("title_" + body[:6], me))


def prim(kind, **kw):
    getattr(bpy.ops.mesh, "primitive_" + kind + "_add")(**kw)
    return bpy.context.active_object


def render(name):
    out = os.path.join(WORK, name + ".png")
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("DONE", out)
