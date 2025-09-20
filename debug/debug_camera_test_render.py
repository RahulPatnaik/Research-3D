# debug_camera_test_render.py
import bpy, sys, os

def test_render(out_dir):
    scene = bpy.context.scene
    # disable denoising if present
    if hasattr(scene, "cycles"):
        scene.cycles.use_denoising = False
    if hasattr(scene.view_layers[0], "cycles"):
        scene.view_layers[0].cycles.use_denoising = False

    # ensure still-image format
    scene.render.image_settings.file_format = 'PNG'
    frame = scene.frame_start if hasattr(scene, 'frame_start') else 1
    scene.frame_set(frame)
    cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
    os.makedirs(out_dir, exist_ok=True)
    for cam in cams:
        scene.camera = cam
        out = os.path.join(out_dir, f"debug_frame_{cam.name}.png")
        scene.render.filepath = out
        print("Rendering single frame for camera:", cam.name, "->", out)
        bpy.ops.render.render(write_still=True)
    print("Done. PNGs in:", out_dir)


if __name__=="__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        outdir=os.path.expanduser("~/Documents/Animations/debug_camera_frames")
        test_render(outdir)
    else:
        print("Usage: blender --background --python debug_camera_test_render.py -- table.ldr")
