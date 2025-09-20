# debug_import_operator.py
import bpy, sys, os

def report(out):
    op_exists = hasattr(bpy.ops.import_scene, "importldraw")
    addons = [k for k in bpy.context.preferences.addons.keys()]
    lines=[]
    lines.append(f"import_scene.importldraw exists: {op_exists}")
    lines.append(f"Enabled addons count: {len(addons)}")
    # list addons that contain 'ldraw' or 'import'
    lines.append("Addons (some names): " + ", ".join(addons[:50]))
    open(out,"w").write("\n".join(lines))
    print("Wrote import operator report to:", out)

if __name__=="__main__":
    out=os.path.expanduser("~/Documents/Animations/debug_import_operator.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    report(out)
