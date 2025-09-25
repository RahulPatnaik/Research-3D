import bpy
import sys
import os

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def add_camera(target_center, size):
    dist = max(size) * 2.0
    bpy.ops.object.camera_add(location=(dist, -dist, dist))
    cam = bpy.context.active_object
    cam.name = "Camera"
    cam.data.type = 'PERSP'
    bpy.context.scene.camera = cam

    # Add empty at center for tracking
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_center)
    empty = bpy.context.active_object
    track = cam.constraints.new(type='TRACK_TO')
    track.target = empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

def make_bright_green_material(name="BrightGreenBrick"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    # Bright neon green
    bsdf.inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 1.0)
    bsdf.inputs["Emission Color"].default_value = (0.0, 1.0, 0.0, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 3.0
    # Transparent start
    bsdf.inputs["Alpha"].default_value = 0.0
    mat.blend_method = 'BLEND'
    return mat

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main(filepath, output_path):
    clear_scene()

    # Parse file
    coords = []
    bricks = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            part, coords_str = line.split("(")
            h, w = map(int, part.split("x"))
            x, y, z = map(int, coords_str.strip(")\n").split(","))
            coords.append((x, y, z))
            bricks.append((h, w, x, y, z))

    # Compute scene center and size
    xs, ys, zs = zip(*coords)
    center = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2)
    size = (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) - min(zs) + 1)

    # Camera
    add_camera(center, size)

    # Animate fade-in
    frame = 1
    for i, (h, w, x, y, z) in enumerate(bricks):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
        obj = bpy.context.active_object

        # Scale (default cube = 2x2x2, so scale to half dims)
        obj.scale = (w / 2, h / 2, 0.5)

        # Give each brick its own material so alpha animates independently
        mat = make_bright_green_material(name=f"BrickMat_{i}")
        obj.data.materials.append(mat)

        # Animate alpha (fade-in)
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Alpha"].default_value = 0.0
        bsdf.inputs["Alpha"].keyframe_insert("default_value", frame=frame)

        bsdf.inputs["Alpha"].default_value = 1.0
        bsdf.inputs["Alpha"].keyframe_insert("default_value", frame=frame + 20)

        frame += 30

    bpy.context.scene.frame_end = frame + 30

    # Render setup
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.filepath = output_path

    bpy.ops.render.render(animation=True)
    print(f"✅ Animation saved to {output_path}")

# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        txtfile = argv[argv.index("--") + 1]
        home = os.path.expanduser("~")
        out_path = os.path.join(home, "Documents", "Animations", "lego_animation.mp4")
        main(txtfile, out_path)
    else:
        print("Usage: blender --background --python animate.py -- input.txt")
