import bpy
import sys
import os
from mathutils import Vector

# ---------------------------
# Utility functions
# ---------------------------
def print_model_bounds():
    bricks = [o for o in bpy.data.objects if o.type == 'MESH']
    if not bricks:
        print("⚠️ No bricks found in scene.")
        return None, None

    xs, ys, zs = [], [], []
    for obj in bricks:
        for v in obj.data.vertices:
            gv = obj.matrix_world @ v.co
            xs.append(gv.x); ys.append(gv.y); zs.append(gv.z)

    center = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    size = Vector((max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))

    print(f"🧱 Model center: {tuple(center)}")
    print(f"📐 Model size (x,y,z): {tuple(size)}")
    return center, size

def print_camera_info():
    cam = bpy.context.scene.camera
    if cam:
        print(f"📷 Active Camera: {cam.name}")
        print(f"   Location: {tuple(cam.location)}")
        print(f"   Rotation (Euler): {tuple(cam.rotation_euler)}")
        print(f"   Type: {cam.data.type}")
        print(f"   Lens: {cam.data.lens} mm")
    else:
        print("⚠️ No active camera found.")

    for obj in bpy.data.objects:
        if obj.type == 'CAMERA' and obj != cam:
            print(f"📷 Extra Camera: {obj.name}")
            print(f"   Location: {tuple(obj.location)}")
            print(f"   Rotation (Euler): {tuple(obj.rotation_euler)}")

def create_debug_cameras(center, size):
    cams = []

    # Distances
    dist_xy = max(size.x, size.y) * 1.5
    dist_z  = size.z * 3.0 + 5.0

    # Front (+Y)
    cam_front = bpy.data.cameras.new("FrontCam")
    obj_front = bpy.data.objects.new("FrontCam", cam_front)
    obj_front.location = (center.x, center.y - dist_xy, center.z)
    obj_front.rotation_euler = (1.5708, 0, 0)  # look towards +Y
    bpy.context.collection.objects.link(obj_front)
    cams.append(obj_front)

    # Side (+X)
    cam_side = bpy.data.cameras.new("SideCam")
    obj_side = bpy.data.objects.new("SideCam", cam_side)
    obj_side.location = (center.x - dist_xy, center.y, center.z)
    obj_side.rotation_euler = (1.5708, 0, 1.5708)  # look towards +X
    bpy.context.collection.objects.link(obj_side)
    cams.append(obj_side)

    # Top
    cam_top = bpy.data.cameras.new("TopCam")
    obj_top = bpy.data.objects.new("TopCam", cam_top)
    obj_top.location = (center.x, center.y, center.z + dist_z)
    obj_top.rotation_euler = (0, 0, 0)  # look down -Z
    bpy.context.collection.objects.link(obj_top)
    cams.append(obj_top)

    print(f"🎥 Added {len(cams)} debug cameras (Front, Side, Top).")
    return cams

def render_test_frames(out_dir):
    scene = bpy.context.scene

    # Disable denoising
    if hasattr(scene, "cycles"):
        scene.cycles.use_denoising = False
    if hasattr(scene.view_layers[0], "cycles"):
        scene.view_layers[0].cycles.use_denoising = False

    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'
    os.makedirs(out_dir, exist_ok=True)

    cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
    if not cams:
        print("⚠️ No cameras to render from.")
        return

    for cam in cams:
        scene.camera = cam
        out = os.path.join(out_dir, f"debug_frame_{cam.name}.png")
        scene.render.filepath = out
        print(f"🎥 Rendering single frame from {cam.name} -> {out}")
        bpy.ops.render.render(write_still=True)

    print(f"✅ Rendered {len(cams)} frames. Check {out_dir}")

# ---------------------------
# Entry Point
# ---------------------------
if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--") + 1]
        print(f"📥 Importing LDraw file: {ldr_file}")
        bpy.ops.import_scene.importldraw(filepath=ldr_file)

        center, size = print_model_bounds()
        print_camera_info()

        if center and size:
            create_debug_cameras(center, size)

        home = os.path.expanduser("~")
        out_dir = os.path.join(home, "Documents", "Animations", "debug_camera_frames")
        render_test_frames(out_dir)
    else:
        print("Usage: blender --background --python debug_all.py -- table.ldr")
