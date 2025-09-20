import bpy
import sys
import mathutils

def get_bounds(objects):
    coords = []
    for obj in objects:
        if obj.type != 'MESH':
            continue
        for v in obj.bound_box:
            coords.append(obj.matrix_world @ mathutils.Vector(v))
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        ldr_file = argv[argv.index("--")+1]
        bpy.ops.import_scene.importldraw(filepath=ldr_file)

        bricks = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        (xmin, xmax), (ymin, ymax), (zmin, zmax) = get_bounds(bricks)
        center = ((xmin+xmax)/2, (ymin+ymax)/2, (zmin+zmax)/2)
        size = (xmax-xmin, ymax-ymin, zmax-zmin)
        print(f"🧱 Model center: {center}")
        print(f"📐 Model size (x,y,z): {size}")
    else:
        print("Usage: blender --background --python debug_bounds.py -- table.ldr")


'''

🧱 Model center: (0.0, 0.0, 0.0)
📐 Model size (x,y,z): (40.0, 40.0, 2.0)

'''