
*********
Line Mask
*********

.. reference::

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Line Mask`

This tool creates a :doc:`Mask </sculpt_paint/sculpting/editing/mask>`
across one side of a drawn line.
The affected areas is visualized by the shaded side of the line.

Usage
=====

Use the tool by:

#. Orient the 3D Viewport to define the direction in depth.
#. :kbd:`LMB` and hold while moving the cursor to define direction of the line mask.
#. Adjust the operation with extra *Controls* shortcuts.
#. Release :kbd:`LMB` to confirm.

Hold :kbd:`Ctrl` to subtract from the mask instead.


Controls
========

Flip :kbd:`F`
   Changes the side of the line that the tool creates a mask.
Snap :kbd:`Ctrl`
   Constrains the rotation of the line to 15 degree intervals.
Move :kbd:`Ctrl-Spacebar`
   Reposition the line.


Tool Settings
=============

Front Faces Only
   Only creates a mask on the faces that face towards the view.

Limit to Segment
   The affected area will not extend the length of the drawn line.
   This helps defining a smaller area instead of extending the line infinitely long.
