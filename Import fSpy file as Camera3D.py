# Import fSpy file as Camera3D
# created by nizar
# contact: http://twitter.com/nizarneezR

# Usage:
# Download fSpy from https://fspy.io/ and match a camera position using a reference image of your shot. Save the .fspy file.
#   For more information on how to use fSpy, see the tutorial on the official website: https://fspy.io/tutorial/
# In DaVinci Resolve, open Fusion and run "Import fSpy file as Camera3D" from DaVinci Resolve's dropdown menu (Workspace > Scripts)
# Select the .fspy-file that you want to import
# The script will create a new Camera3D-node and MediaIn-node containing your reference image in your current Fusion composition

# Install:
# Install Python (at least version 3.7) from https://python.org/
# Download this file and save it in the "Scripts" folder of DaVinci Resolve:
#   on Windows: C:\Users\<YOUR_NAME>\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp
#   on MacOS: /Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp
#   on Linux: /opt/resolve/Fusion/Scripts/Comp


import math
import json
from struct import unpack
from tkinter.filedialog import askopenfilename

def guess_file_format(data: bytes):
    # source for all magic numbers: https://en.wikipedia.org/wiki/List_of_file_signatures
    if data.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"):
        return "png"
    elif data.startswith(b"\xFF\xD8\xFF"):
        return "jpg"
    elif data.startswith(b"\x52\x49\x46\x46"):
        return "webp"
    elif data.startswith(b"\x42\x4D"):
        return "bmp"
    elif data.startswith(b"\x47\x49\x46"):
        return "gif" # chromium (= fspy) should understand static gif? so just to be sure
    else:
        return "png" # default

fspy_file_path = askopenfilename(filetypes=[("fSpy file", "*.fspy")])

# reading image data and state dict
# file format specification: https://github.com/stuffmatic/fSpy/blob/develop/project_file_format.md
# inspired by https://github.com/stuffmatic/fSpy-Blender/blob/master/fspy_blender/fspy.py
with open(fspy_file_path, mode="rb") as f:
    # read buffer sizes from header
    file_id = unpack("<I", f.read(4))[0]
    project_version = unpack("<I", f.read(4))[0]
    state_dict_size = unpack("<I", f.read(4))[0]
    img_buffer_size = unpack("<I", f.read(4))[0]
    
    f.seek(16) # skip header
    state_dict = f.read(state_dict_size).decode("utf-8")
    state_dict = json.loads(state_dict)
    
    image_data = f.read(img_buffer_size)
    img_file_extension = guess_file_format(image_data)
    img_file_path = fspy_file_path.replace(".fspy", f"_fspy.{img_file_extension}")
    with open(img_file_path, mode="wb") as f:
        f.write(image_data)
    
# setting values from fSpy in the Fusion tool

try:
    comp.Lock()

    media_pool = resolve.GetProjectManager().GetCurrentProject().GetMediaPool()
    tool = comp.AddTool("Camera3D")
    camera_params = state_dict["cameraParameters"]
    rotation_matrix = camera_params["cameraTransform"]["rows"]

    # rotation matrix (fSpy) to euler angles (Fusion)

    scale_y = math.sqrt(rotation_matrix[0][0] ** 2 + rotation_matrix[1][0] ** 2)

    if scale_y < 1e-5: # if matrix is singular
        rot_x = math.atan2(-rotation_matrix[1][2], rotation_matrix[1][2])
        rot_y = math.atan2(-rotation_matrix[2][0], scale_y)
        rot_z = 0
    else: # if matrix is not singular
        rot_x = math.atan2(rotation_matrix[2][1], rotation_matrix[2][2])
        rot_y = math.atan2(-rotation_matrix[2][0], scale_y)
        rot_z = math.atan2(rotation_matrix[1][0], rotation_matrix[0][0])

    # setting data in Fusion tool

    tool.Transform3DOp.Translate.X = rotation_matrix[0][-1]
    tool.Transform3DOp.Translate.Y = rotation_matrix[1][-1]
    tool.Transform3DOp.Translate.Z = rotation_matrix[2][-1]

    tool.Transform3DOp.Rotate.X = math.degrees(rot_x)
    tool.Transform3DOp.Rotate.Y = math.degrees(rot_y)
    tool.Transform3DOp.Rotate.Z = math.degrees(rot_z)

    tool.AoV = math.degrees(camera_params["horizontalFieldOfView"])

    # import image as MediaIn/Loader, connect to 3Cm.ImageInput
    reference_img = comp.AddTool("Loader")
    reference_img.Clip = img_file_path
    tool.SetInput("ImageInput", reference_img)

    comp.SetActiveTool(tool)
    comp.Unlock()
finally:
    comp.Unlock()
