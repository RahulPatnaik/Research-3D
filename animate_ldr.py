import bpy
import sys
import os

def clear_keyframes(obj):
    if obj.animation_data:
        obj.animation_data_clear()

def animate_from_ldr(ldr_path, output_path):
    # Import LDraw file
    print(f"📥 Importing LDraw file: {ldr_path}")
    bpy.ops.import_scene.importldraw(filepath=ldr_path)

    # Get only bricks (mesh objects)
    bricks = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    print(f"🧱 Found {len(bricks)} bricks")

    frame = 1
    for i, obj in enumerate(bricks):
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
    scene.render.filepath = output_path

    # Render animation
    print(f"🎬 Rendering animation to {output_path} ...")
    bpy.ops.render.render(animation=True)
    print(f"✅ Animation saved to {output_path}")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--") + 1]
        home = os.path.expanduser("~")
        out_path = os.path.join(home, "Documents", "Animations", "lego_from_ldr.mp4")
        animate_from_ldr(ldr_file, out_path)
    else:
        print("Usage: blender --background --python animate_ldr.py -- table.ldr")
