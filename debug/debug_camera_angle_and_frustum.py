# debug_camera_angle_and_frustum.py
import bpy, sys, os, mathutils, math

def get_center(objs):
    coords=[]
    for o in objs:
        if o.type!='MESH': continue
        for v in o.bound_box:
            coords.append(o.matrix_world @ mathutils.Vector(v))
    xs=[c.x for c in coords]; ys=[c.y for c in coords]; zs=[c.z for c in coords]
    return ((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2)

def report(out):
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    center=mathutils.Vector(get_center(meshes))
    lines=[]
    for cam in [o for o in bpy.data.objects if o.type=='CAMERA']:
        forward = cam.matrix_world.to_quaternion() @ mathutils.Vector((0,0,-1))
        to_center = (center - cam.location)
        dist = to_center.length
        dot = max(-1.0, min(1.0, forward.normalized().dot(to_center.normalized())))
        angle_deg = math.degrees(math.acos(dot))
        lines.append(f"{cam.name}: loc={tuple(round(v,3) for v in cam.location)} dist_to_center={dist:.3f} angle_to_center_deg={angle_deg:.3f} (angle>90 means pointing away)")
    open(out,"w").write("\n".join(lines))
    print("Wrote camera angle report to:", out)

if __name__=="__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out=os.path.expanduser("~/Documents/Animations/debug_camera_angles.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        report(out)
    else:
        print("Usage: blender --background --python debug_camera_angle_and_frustum.py -- table.ldr")
