import bpy
import sys
import os
from mathutils import Vector

def create_tracking_empty(location=(0,0,0)):
    """Create an empty object at model center for cameras to track"""
    empty = bpy.data.objects.new("TrackTarget", None)
    empty.location = location
    bpy.context.collection.objects.link(empty)
    return empty

def setup_camera(name, location, target):
    """Create a camera at location, tracking target"""
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = location
    bpy.context.collection.objects.link(cam_obj)

    # Track to constraint
    constraint = cam_obj.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    return cam_obj

def add_cameras(model_center, model_size):
    max_dim = max(model_size)
    dist = max_dim * 2.5  # how far cameras are placed

    target = create_tracking_empty(model_center)

    front_cam = setup_camera("FrontCam", (0, -dist, model_center[2] + model_size[2]/2), target)
    side_cam  = setup_camera("SideCam",  (dist, 0, model_center[2] + model_size[2]/2), target)
    top_cam   = setup_camera("TopCam",   (0, 0, dist), target)

    return [front_cam, side_cam, top_cam]

def compute_bounds(meshes):
    """Compute world-space bounding box for all meshes"""
    coords = []
    for obj in meshes:
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ Vector(corner)
            coords.append(world_corner)

    min_x = min(v.x for v in coords)
    max_x = max(v.x for v in coords)
    min_y = min(v.y for v in coords)
    max_y = max(v.y for v in coords)
    min_z = min(v.z for v in coords)
    max_z = max(v.z for v in coords)

    center = ((min_x + max_x)/2, (min_y + max_y)/2, (min_z + max_z)/2)
    size   = (max_x - min_x, max_y - min_y, max_z - min_z)

    return center, size

# Entry
if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--") + 1]
        print(f"📥 Importing LDraw file: {ldr_file}")
        bpy.ops.import_scene.importldraw(filepath=ldr_file)

        meshes = [o for o in bpy.data.objects if o.type == 'MESH']
        if meshes:
            center, size = compute_bounds(meshes)
            print(f"🧱 Model center: {center}")
            print(f"📐 Model size: {size}")

            add_cameras(center, size)
        else:
            print("⚠️ No meshes found after import")
