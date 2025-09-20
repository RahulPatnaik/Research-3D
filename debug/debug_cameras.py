# debug_cameras.py
import bpy, sys, os, math
import mathutils

def cam_report(out):
    cams = [o for o in bpy.data.objects if o.type=='CAMERA']
    scene_cam = bpy.context.scene.camera
    lines=[]
    lines.append(f"Total cameras: {len(cams)}; active: {(scene_cam.name if scene_cam else None)}")
    for c in cams:
        d=c.data
        loc=tuple(round(v,4) for v in c.location)
        rot_deg=tuple(round(math.degrees(v),3) for v in c.rotation_euler)
        lines.append(f"- {c.name} | loc={loc} rot_deg={rot_deg} type={d.type} lens={getattr(d,'lens',None)} ortho_scale={getattr(d,'ortho_scale',None)} clip=({d.clip_start},{d.clip_end})")
    open(out,"w").write("\n".join(lines))
    print("Wrote camera report to:", out)

if __name__ == "__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out=os.path.expanduser("~/Documents/Animations/debug_camera_report.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        cam_report(out)
    else:
        print("Usage: blender --background --python debug_cameras.py -- table.ldr")
