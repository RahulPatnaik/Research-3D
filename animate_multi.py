import bpy
import sys
import os

def clear_keyframes(obj):
    if obj.animation_data:
        obj.animation_data_clear()

def import_ldr(path):
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

def create_camera(name, axis, center, max_dim, dist=0.027, lens=85):
    loc = (center[0] + axis[0]*max_dim*dist,
           center[1] + axis[1]*max_dim*dist,
           center[2] + axis[2]*max_dim*dist)

    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = loc

    # Aim camera
    constraint = cam_obj.constraints.new(type='TRACK_TO')
    empty = bpy.data.objects.new(f"{name}_Target", None)
    bpy.context.collection.objects.link(empty)
    empty.location = center
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    return cam_obj

def animate_from_ldr(ldr_path, outdir):
    print(f"📥 Importing {ldr_path}")
    import_ldr(ldr_path)

    center, size = get_model_bounds()
    max_dim = max(size)
    print(f"🧱 Model center {center}, size {size}, max_dim {max_dim}")

    # Animate bricks
    bricks = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    frame = 1
    for i, obj in enumerate(bricks):
        clear_keyframes(obj)
        obj.hide_render = True
        obj.hide_viewport = True
        obj.keyframe_insert(data_path="hide_render", frame=frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=frame)
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=frame+5)
        obj.keyframe_insert(data_path="hide_viewport", frame=frame+5)
        frame += 10
    bpy.context.scene.frame_end = frame+20

    # Camera setups
    views = {
        "Front": (0, -1, 0),
        "Side": (1, 0, 0),
        "Top": (0, 0, 1),
    }

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    for view_name, axis in views.items():
        cam = create_camera(view_name, axis, center, max_dim, dist=0.027, lens=85)
        scene.camera = cam
        scene.render.filepath = os.path.join(outdir, f"lego_{view_name}.mp4")
        print(f"🎬 Rendering {view_name} view -> {scene.render.filepath}")
        bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--")+1]
        home = os.path.expanduser("~")
        out_dir = os.path.join(home, "Documents", "Animations")
        animate_from_ldr(ldr_file, out_dir)
    else:
        print("Usage: blender --background --python animate_multi.py -- table.ldr")
