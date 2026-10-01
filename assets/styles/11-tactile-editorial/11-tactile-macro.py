"""TACTILE EDITORIAL — plate: a macro 'photograph' at real-world scale. One ripe cherry resting in a
bed of roasted beans; 100mm at f/2, warm low window light, falloff to shadow. The type is composited
in HTML over this plate (quiet serif, grain) so the plate can be re-graded independently."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import bmesh
from mathutils import Vector

reset()
setup_render(exposure=-0.2, look="AgX - High Contrast")
world("#20150f", 0.03)
random.seed(11)

# --- materials
def roasted():
    m = bpy.data.materials.new("roasted"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    info = nt.nodes.new("ShaderNodeObjectInfo")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexcol("#2a150b")
    ramp.color_ramp.elements[1].color = hexcol("#5a321b")
    nt.links.new(info.outputs["Random"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.32
    p.inputs["Coat Weight"].default_value = 0.25
    p.inputs["Coat Roughness"].default_value = 0.2
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 900; n.inputs["Detail"].default_value = 8
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.25; b.inputs["Distance"].default_value = 0.0002
    nt.links.new(n.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m

def cherry_mat():
    """Ripe coffee cherry: crimson body warming to orange toward the stem end, waxy not glassy."""
    m = bpy.data.materials.new("cherry"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -1.2; mr.inputs["From Max"].default_value = 1.2
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexcol("#8e0a14")
    ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.elements[1].color = hexcol("#d9481c")
    e = ramp.color_ramp.elements.new(0.62); e.color = hexcol("#b3121b")
    nt.links.new(tc.outputs["Object"], sep.inputs[0]); nt.links.new(sep.outputs["Y"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.34
    p.inputs["Subsurface Weight"].default_value = 0.3
    p.inputs["Subsurface Radius"].default_value = (0.003, 0.0006, 0.0004)
    p.inputs["Coat Weight"].default_value = 0.25
    p.inputs["Coat Roughness"].default_value = 0.12
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 400
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.08; bmp.inputs["Distance"].default_value = 0.0002
    nt.links.new(n.outputs["Fac"], bmp.inputs["Height"]); nt.links.new(bmp.outputs["Normal"], p.inputs["Normal"])
    return m

def matte(name, col, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = hexcol(col); p.inputs["Roughness"].default_value = rough
    return m

ROAST = roasted()

# --- bean mesh (two halves -> centre cut), shared by every instance
def bean_mesh():
    bm = bmesh.new()
    for sgn in (-1, 1):
        tmp = bmesh.new()
        bmesh.ops.create_uvsphere(tmp, u_segments=24, v_segments=14, radius=1)
        bmesh.ops.bisect_plane(tmp, geom=tmp.verts[:] + tmp.edges[:] + tmp.faces[:], plane_co=(0, 0, 0),
                               plane_no=(sgn, 0, 0), clear_outer=True)
        for v in tmp.verts:
            v.co.x = v.co.x * 0.42 + sgn * 0.06
            v.co.y *= 0.56
            v.co.z *= 0.36
            # flat face: squash the underside
            if v.co.z < 0: v.co.z *= 0.45
        me_t = bpy.data.meshes.new("t"); tmp.to_mesh(me_t); bm.from_mesh(me_t); bpy.data.meshes.remove(me_t)
    me = bpy.data.meshes.new("bean"); bm.to_mesh(me)
    me.shade_smooth()
    return me

BEAN = bean_mesh()
S = 0.0105  # bean length ~ 11 mm
count = 0
for layer in range(2):
    for i in range(1700):
        y = random.uniform(-0.06, 0.42)
        spread = 0.07 + y * 0.45
        x = random.uniform(-spread, spread)
        ob = link(bpy.data.objects.new("b", BEAN))
        s = S * random.uniform(0.9, 1.1) / 1.12
        ob.scale = (s, s, s)
        ob.location = (x, y, 0.0035 + layer * 0.0045 + random.uniform(-0.001, 0.001))
        ob.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5) + (math.pi if random.random() < 0.3 else 0),
                             random.uniform(0, math.tau))
        if not ob.data.materials: ob.data.materials.append(ROAST)
        count += 1
print("beans", count)

# ground under the beans (hidden in shadow)
g = prim("plane", size=2); assign(g, matte("ground", "#1a0f09"))

# --- the hero cherry (+ a second, out of focus, behind)
CH = cherry_mat()
def cherry(loc, r, yaw):
    c = prim("uv_sphere", radius=1, segments=64, ring_count=32)
    c.scale = (r, r * 1.22, r * 0.95); c.location = loc; c.rotation_euler = (0, 0, yaw)
    smooth(c); assign(c, CH)
    # blossom-end calyx: a small dark ring + nub at the -Y end
    tip = Vector(loc) + Vector((math.sin(-yaw) * -r * 1.2, -math.cos(yaw) * r * 1.2, 0))
    ring = prim("torus", major_radius=r * 0.2, minor_radius=r * 0.06, major_segments=32, minor_segments=8)
    ring.location = tip; ring.rotation_euler = (math.radians(90), 0, yaw)
    smooth(ring); assign(ring, matte("calyx", "#2e1a0e", 0.7))
    return c
cherry((-0.012, 0.0, 0.0152), 0.0078, math.radians(215))
cherry((0.03, 0.12, 0.0155), 0.0078, math.radians(-20))

# --- light & lens
area_light("window", (-0.45, 0.1, 0.16), (0, 0.02, 0.01), 0.3, 30, "#ffbf85")
area_light("bounce", (0.35, -0.3, 0.1), (0, 0, 0.01), 0.3, 1.2, "#e8d9c8")
area_light("rim", (0.25, 0.5, 0.12), (0, 0.05, 0.01), 0.2, 5, "#bcd0ff")
camera((0.02, -0.165, 0.105), (-0.002, 0.015, 0.006), lens=100, dof_target=(-0.012, 0.0, 0.015), fstop=2.8)
render("11-tactile-macro")
