import bpy
import sys
import os

def import_ldr(path):
    print(f"📥 Importing LDraw file: {path}")
    bpy.ops.import_scene.importldraw(filepath=path)

def get_model_bounds():
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    min_x = min(v[0] for m in meshes for v in m.bound_box)
    max_x = max(v[0] for m in meshes for v in m.bound_box)
    min_y = min(v[1] for m in meshes for v in m.bound_box)
    max_y = max(v[1] for m in meshes for v in m.bound_box)
    min_z = min(v[2] for m in meshes for v in m.bound_box)
    max_z = max(v[2] for m in meshes for v in m.bound_box)

    center = ((min_x+max_x)/2, (min_y+max_y)/2, (min_z+max_z)/2)
    size = (max_x-min_x, max_y-min_y, max_z-min_z)
    return center, size

def create_camera(name, location, target, lens=50.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = location

    # point camera at target
    direction = (target[0]-location[0], target[1]-location[1], target[2]-location[2])
    cam_obj.rotation_euler = (0, 0, 0)
    cam_obj.constraints.new(type='TRACK_TO')
    cam_obj.constraints["Track To"].target = bpy.data.objects.new("Empty", None)
    bpy.context.collection.objects.link(cam_obj.constraints["Track To"].target)
    cam_obj.constraints["Track To"].target.location = target
    cam_obj.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    cam_obj.constraints["Track To"].up_axis = 'UP_Y'
    return cam_obj

def test_render(ldr_path, outdir):
    import_ldr(ldr_path)
    center, size = get_model_bounds()
    max_dim = max(size)

    os.makedirs(outdir, exist_ok=True)

    dist_multipliers = [0.027, 0.05, 0.27, 0.5, 1.0, 1.5, 2.0]
    lens_values = [35, 50, 85]

    views = {
        "Front": (0, -1, 0),
        "Side": (1, 0, 0),
        "Top": (0, 0, 1),
    }

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    for view_name, axis in views.items():
        for d in dist_multipliers:
            for lens in lens_values:
                loc = (center[0] + axis[0]*max_dim*d,
                       center[1] + axis[1]*max_dim*d,
                       center[2] + axis[2]*max_dim*d)

                cam = create_camera(f"{view_name}_d{d}_l{lens}", loc, center, lens=lens)
                scene.camera = cam
                scene.render.filepath = os.path.join(outdir, f"{view_name}_dist{d}_lens{lens}.png")
                print(f"🎥 Rendering {scene.render.filepath}")
                bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--") + 1]
        home = os.path.expanduser("~")
        out_dir = os.path.join(home, "Documents", "Animations", "camera_tests")
        test_render(ldr_file, out_dir)
    else:
        print("Usage: blender --background --python debug_sweep.py -- table.ldr")
