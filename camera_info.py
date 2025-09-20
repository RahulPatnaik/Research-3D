import bpy

def print_camera_info():
    cam = bpy.context.scene.camera
    if cam is None:
        print("⚠ No active camera in scene!")
        return

    print(f"📷 Active Camera: {cam.name}")
    print(f"   Location: {cam.location[:]}")
    print(f"   Rotation (Euler): {cam.rotation_euler[:]}")
    print(f"   Rotation (Quaternion): {cam.rotation_quaternion[:]}")
    print(f"   Camera Type: {cam.data.type}")
    if cam.data.type == 'PERSP':
        print(f"   Lens (focal length): {cam.data.lens} mm")
    elif cam.data.type == 'ORTHO':
        print(f"   Ortho scale: {cam.data.ortho_scale}")

    print(f"   Clip Start: {cam.data.clip_start}")
    print(f"   Clip End: {cam.data.clip_end}")

if __name__ == "__main__":
    print_camera_info()


'''
CAMERA DEFAULT INFORMATION:

   Active Camera: Camera
   Location: (7.358891487121582, -6.925790786743164, 4.958309173583984)
   Rotation (Euler): (1.1093189716339111, 0.0, 0.8149281740188599)
   Rotation (Quaternion): (1.0, 0.0, 0.0, 0.0)
   Camera Type: PERSP
   Lens (focal length): 50.0 mm
   Clip Start: 0.10000000149011612
   Clip End: 100.0
'''