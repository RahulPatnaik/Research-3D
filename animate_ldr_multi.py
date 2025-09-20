import bpy
import sys
import os
import mathutils

def clear_keyframes(obj):
    if obj.animation_data:
        obj.animation_data_clear()

def point_camera_at(cam, target=(0, 0, 0)):
    """Rotate camera to look at target point"""
    direction = mathutils.Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

def animate_from_ldr(ldr_path, out_dir):
    # Import LDraw file
    print(f"📥 Importing LDraw file: {ldr_path}")
    bpy.ops.import_scene.importldraw(filepath=ldr_path)

    # Get only bricks (mesh objects)
    bricks = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    print(f"🧱 Found {len(bricks)} bricks")

    frame = 1
    for obj in bricks:
        clear_keyframes(obj)

        # Hide initially
        obj.hide_render = True
        obj.hide_viewport = True
        obj.keyframe_insert(data_path="hide_render", frame=frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=frame)

        # Show after small delay
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=frame + 5)
        obj.keyframe_insert(data_path="hide_viewport", frame=frame + 5)

        frame += 10

    bpy.context.scene.frame_end = frame + 20

    # Render setup
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    # --- 1. Original view (default camera) ---
    scene.render.filepath = os.path.join(out_dir, "lego_from_ldr.mp4")
    print(f"🎬 Rendering default view -> {scene.render.filepath}")
    bpy.ops.render.render(animation=True)

    # --- 2. Front, Side, Top cameras ---
    cam_positions = {
        "front": (0, -80, 20),
        "side": (80, 0, 20),
        "top": (0, 0, 80),
    }

    for name, loc in cam_positions.items():
        cam = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = loc
        point_camera_at(cam_obj, target=(0, 0, 0))
        scene.camera = cam_obj

        out_file = os.path.join(out_dir, f"lego_from_ldr_{name}.mp4")
        scene.render.filepath = out_file
        print(f"🎬 Rendering {name} view -> {out_file}")
        bpy.ops.render.render(animation=True)

    print("✅ All animations saved!")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--") + 1]
        home = os.path.expanduser("~")
        out_dir = os.path.join(home, "Documents", "Animations")
        os.makedirs(out_dir, exist_ok=True)
        animate_from_ldr(ldr_file, out_dir)
    else:
        print("Usage: blender --background --python animate_ldr_multi.py -- table.ldr")
