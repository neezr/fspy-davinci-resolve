# fSpy-Importer for DaVinci Resolve

Import a scene from [fSpy](https://fspy.io/) to a ```Camera3D```-node in DaVinci Resolve, to match the 3D camera positions.


## Usage:
- Download [fSpy](https://fspy.io/) and match a camera position using a reference image of your shot. Save the ```.fspy``` file.
    - For more information on how to use fSpy, see [the tutorial on the official website](https://fspy.io/tutorial/)
- In DaVinci Resolve, open Fusion and run ```Import fSpy file as Camera3D``` from DaVinci Resolve's dropdown menu (```Workspace > Scripts```)
- Select the ```.fspy``` file that you want to import
- The script will create a new ```Camera3D``` node and ```MediaIn``` node containing your reference image in your current Fusion composition

## Install:
- Install Python (at least version 3.7) from [python.org](https://python.org/)
- Download the file [```Import fSpy file as Camera3D.py```](Import%20fSpy%20file%20as%20Camera3D.py)
- Save the file in the *Scripts* folder of DaVinci Resolve:
  - On Windows: ```C:\Users\<YOUR_NAME>\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp```
  - On MacOS: ```/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp```
  - On Linux: ```/opt/resolve/Fusion/Scripts/Comp```
