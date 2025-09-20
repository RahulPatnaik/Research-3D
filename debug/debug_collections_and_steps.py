# debug_collections_and_steps.py
import bpy, sys, os, re

def report(out):
    cols = list(bpy.data.collections)
    lines = []
    lines.append(f"Total collections: {len(cols)}")
    step_cols = []
    for c in cols:
        lines.append(f"- Collection: {c.name} (objects: {len(list(c.all_objects))})")
        if re.search(r"step", c.name, re.I):
            step_cols.append(c)
    if step_cols:
        lines.append("Detected STEP collections (order):")
        for c in sorted(step_cols, key=lambda x: x.name):
            names = [o.name for o in c.all_objects if o.type=='MESH']
            lines.append(f"  * {c.name}: {len(names)} meshes -> {names[:10]}")
    open(out,"w").write("\n".join(lines))
    print("Wrote collections report to:", out)

if __name__ == "__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out=os.path.expanduser("~/Documents/Animations/debug_collections.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        report(out)
    else:
        print("Usage: blender --background --python debug_collections_and_steps.py -- table.ldr")
