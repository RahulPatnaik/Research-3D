# debug_list_scene.py
import bpy, sys, os, mathutils

def dump_scene(out_path):
    objs = [o for o in bpy.data.objects]
    lines = []
    lines.append(f"Scene objects: {len(objs)}")
    for o in objs:
        typ = o.type
        loc = tuple(round(v,4) for v in o.location)
        rot = tuple(round(v,4) for v in o.rotation_euler)
        scl = tuple(round(v,4) for v in o.scale)
        coll_names = [c.name for c in o.users_collection]
        mat_names = []
        if hasattr(o.data, "materials"):
            mat_names = [m.name if m else "None" for m in o.data.materials]
        verts = None
        if o.type == 'MESH' and o.data:
            verts = len(o.data.vertices)
        lines.append(f"- {o.name} | type={typ} | loc={loc} rot={rot} scale={scl} verts={verts} hide_render={o.hide_render} hide_viewport={o.hide_viewport} visible_get={o.visible_get()} collections={coll_names} materials={mat_names} parent={(o.parent.name if o.parent else None)}")
    open(out_path,"w").write("\n".join(lines))
    print("Wrote scene dump to:", out_path)

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr = argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out = os.path.expanduser("~/Documents/Animations/debug_scene_list.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        dump_scene(out)
    else:
        print("Usage: blender --background --python debug_list_scene.py -- table.ldr")
