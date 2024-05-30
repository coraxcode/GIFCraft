GIFCraft - GIF Editor

GIFCraft is a versatile and user-friendly GIF editor that allows you to create, edit, and manipulate GIF animations with ease. This application, built using Python's Tkinter and PIL (Pillow) libraries, provides a range of functionalities for handling GIF, PNG, and WebP files.
Features

Load GIF/PNG/WebP Files: Import image files and extract their frames.
Frame Manipulation: Add, delete, and reorder frames.
Frame Delay Settings: Customize the delay between frames.
Animation Playback: Play and pause animations within the editor.
Save and Export: Save your work in GIF, PNG, or WebP formats.
Undo/Redo: Undo and redo actions to manage changes easily.
Batch Frame Extraction: Extract and save individual frames from your animations.
Keyboard Shortcuts: Efficient navigation and manipulation using keyboard shortcuts.

Installation

Clone the repository:

git clone https://github.com/seehrum/GIFCraft.git

Navigate to the project directory:

cd GIFCraft

Install the required dependencies:

sudo apt-get install python3 python3-tk python3-pil python3-pil.imagetk python3-pip 

pip install pillow

Usage

Run the application:

python GIFCraft.py

Load a GIF/PNG/WebP file:
Go to File > Load GIF/PNG/WebP or press Ctrl+O.
Select your file from the file dialog.

Add or Delete Frames:
To add frames, go to Edit > Add Image.
To delete frames, select the frames in the list and press Delete.

Reorder Frames:
Use Edit > Move Frame Up or Move Frame Down to change the order of frames.

Set Frame Delay:
Select a frame, enter the delay in milliseconds, and click Set Frame Delay.

Play/Pause Animation:
Toggle play/pause using Animation > Play/Stop Animation or press Space.

Save Your Work:
Save your work by going to File > Save or Save As.

Extract Frames:
Extract all frames to individual images using File > Extract Frames.

Keyboard Shortcuts

Load File: Ctrl+O
Save: Ctrl+S
Save As: Ctrl+Shift+S
Add Image: (No shortcut)
Delete Frame(s): Delete
Move Frame Up: Arrow Up
Move Frame Down: Arrow Down
Play/Stop Animation: Space
Undo: Ctrl+Z
Redo: Ctrl+Y
Check/Uncheck All: (No shortcut)
Toggle Checkbox of Current Frame: X

License

GIFCraft is licensed under the GNU General Public License v3.0. You can redistribute it and/or modify it under the terms of the GNU GPL as published by the Free Software Foundation.
