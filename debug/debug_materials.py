# debug_materials.py
import bpy, sys, os

def mat_report(out):
    mats = bpy.data.materials
    lines=[]
    lines.append(f"Total materials: {len(mats)}")
    for m in mats:
        lines.append(f"- {m.name}: use_nodes={m.use_nodes} blend={m.blend_method}")
        if m.use_nodes:
            nodes = m.node_tree.nodes
            if "Principled BSDF" in nodes:
                p = nodes["Principled BSDF"]
                lines.append(f"   Principled: BaseColor={tuple(round(v,3) for v in p.inputs['Base Color'].default_value)} Emission={p.inputs['Emission'].default_value if 'Emission' in p.inputs else 'N/A'} Alpha={p.inputs['Alpha'].default_value if 'Alpha' in p.inputs else 'N/A'}")
    open(out,"w").write("\n".join(lines))
    print("Wrote material report to:", out)

if __name__ == "__main__":
    argv=sys.argv
    if "--" in argv:
        ldr=argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr)
        out=os.path.expanduser("~/Documents/Animations/debug_materials.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        mat_report(out)
    else:
        print("Usage: blender --background --python debug_materials.py -- table.ldr")
