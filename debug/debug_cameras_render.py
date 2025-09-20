import bpy
import sys
import os
from mathutils import Vector

def compute_bounds(meshes):
    coords = []
    for obj in meshes:
        for corner in obj.bound_box:
            coords.append(obj.matrix_world @ Vector(corner))
    min_x = min(v.x for v in coords); max_x = max(v.x for v in coords)
    min_y = min(v.y for v in coords); max_y = max(v.y for v in coords)
    min_z = min(v.z for v in coords); max_z = max(v.z for v in coords)
    return ((min_x+max_x)/2, (min_y+max_y)/2, (min_z+max_z)/2), (max_x-min_x, max_y-min_y, max_z-min_z)

def create_cam(name, loc, target):
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = loc
    bpy.context.collection.objects.link(cam_obj)
    # track-to constraint
    empty = bpy.data.objects.new(f"{name}_Target", None)
    empty.location = target
    bpy.context.collection.objects.link(empty)
    c = cam_obj.constraints.new(type="TRACK_TO")
    c.target = empty; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return cam_obj

def render_from_cams(cameras, outdir):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'
    os.makedirs(outdir, exist_ok=True)
    for cam in cameras:
        scene.camera = cam
        outpath = os.path.join(outdir, f"{cam.name}.png")
        scene.render.filepath = outpath
        bpy.ops.render.render(write_still=True)
        print(f"📸 Rendered {outpath}")

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr = argv[argv.index("--") + 1]
        print(f"📥 Importing {ldr}")
        bpy.ops.import_scene.importldraw(filepath=ldr)

        meshes = [o for o in bpy.data.objects if o.type == 'MESH']
        if not meshes:
            print("⚠️ No meshes found!"); sys.exit(1)

        center, size = compute_bounds(meshes)
        print(f"🧱 Model center: {center}, size: {size}")

        # distance scaled to largest dim
        dist = max(size) * 2
        front = create_cam("FrontCam", (0, -dist, size[2]/2), center)
        side  = create_cam("SideCam", (dist, 0, size[2]/2), center)
        top   = create_cam("TopCam", (0, 0, dist), center)

        outdir = os.path.join(os.path.expanduser("~"), "Documents", "Animations", "camera_tests")
        render_from_cams([front, side, top], outdir)
