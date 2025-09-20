# debug_render_settings.py
import bpy, sys, os

def report(out):
    s=bpy.context.scene
    rs=s.render
    lines=[]
    lines.append(f"engine: {s.render.engine}")
    lines.append(f"image_settings.file_format: {rs.image_settings.file_format}")
    if rs.image_settings.file_format == 'FFMPEG':
        lines.append(f"ffmpeg.format: {rs.ffmpeg.format}")
        lines.append(f"ffmpeg.codec: {rs.ffmpeg.codec}")
    lines.append(f"filepath: {rs.filepath}")
    lines.append(f"resolution: {rs.resolution_x}x{rs.resolution_y} fps:{s.render.fps}")
    open(out,"w").write("\n".join(lines))
    print("Wrote render settings to:", out)

if __name__ == "__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out=os.path.expanduser("~/Documents/Animations/debug_render_settings.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        report(out)
    else:
        print("Usage: blender --background --python debug_render_settings.py -- table.ldr")
