# debug_keyframes.py
import bpy, sys, os

def keyframe_report(out):
    lines=[]
    for o in bpy.data.objects:
        if o.animation_data and o.animation_data.action:
            lines.append(f"Object {o.name} has action: {o.animation_data.action.name}")
            for f in o.animation_data.action.fcurves:
                lines.append(f"  fcurve: data_path={f.data_path} array_index={f.array_index} keyframes={[kp.co[0] for kp in f.keyframe_points]}")
    open(out,"w").write("\n".join(lines))
    print("Wrote keyframe report to:", out)

if __name__ == "__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out=os.path.expanduser("~/Documents/Animations/debug_keyframes.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        keyframe_report(out)
    else:
        print("Usage: blender --background --python debug_keyframes.py -- table.ldr")
