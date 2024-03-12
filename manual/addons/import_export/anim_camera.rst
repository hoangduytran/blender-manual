
****************
Camera Animation
****************

.. reference::

   :Category:  Import-Export
   :Menu:      :menuselection:`File --> Export --> Cameras & Markers (.py)`

Exports a .py file containing information about the animation of cameras in the scene.
This file can be used to 'import' these cameras and their animation to another blend-file.


Exported Data
=============

This is the type of data associated with the camera that get included in the .py file.


Static Data
-----------

- Shift X
- Shift Y
- Depth of Field Focus Distance
- Clip Start
- Clip End
- Viewport Display Size
- Render Visibility


Animated Data
-------------

- Focal Length
- Location
- Rotation
- Scale


Properties
==========

Export
------

Transform
^^^^^^^^^

Start / End
   Sets the range of animation frames to export to the .py file.
Only Selected
   Toggle between exporting only selected cameras or all cameras in the scene.


Import
------

To import the .py file, go to Blender's Text Editor.
:menuselection:`Text --> Open --> YourExportedFile (.py)`
