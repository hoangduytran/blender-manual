
*******
Editing
*******

The tools and panels available to edit masks are the same in both editors.
Editing of mask splines happens in a way similar to editing Bézier curves or paths in GIMP or other curve editors.

.. tip::

   To get interactive feedback on the resulting mask,
   a Mask node can be connected directly to a Viewer node in the Compositor,
   which will then keep updating the compositing result while editing.


Transform
=========

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Transform`

Existing control points can be moved with :kbd:`LMB` and
moved, scaled and rotated with the usual :kbd:`G`, :kbd:`S`, :kbd:`R` shortcuts.
The whole spline can be moved by dragging the center dot with :kbd:`LMB`.

Scale Feather :kbd:`Alt-S`
   Will scale the feather size.


Toggle Cyclic
=============

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Toggle Cyclic`
   :Hotkey:    :kbd:`Alt-C`

Toggle to create a closed curve or open it again.
Close the mask by joining the last control point to the first.


Set Handle Type
===============

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Set Handle Type`
   :Hotkey:    :kbd:`V`

Set handle type for selected spline points.


Recalculate Handles
===================

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Recalculate Handles`
   :Hotkey:    :kbd:`Ctrl-N`

Make normals (handle directions) consistent.


Switch Direction
================

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Switch Direction`

Switch Direction handle directions in/out.


Copy Paste
==========

Todo.


Parent
======

Todo.


Animation
=========

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Animation`

Masks can be animated with the shape keying system.
This can be useful when there are not enough good feature points to track in the footage,
or the mask is not based on footage.
Mask animation timing can be edited from the *Dope Sheet's* :ref:`Mask Mode <dope-sheet-mask>`.

Insert Shape Key :kbd:`I`
   Will insert a shape key for the active mask layer at the current frame.
   This works on the level of mask layers,
   so inserting a shape key will keyframe all the splines and points contained in it.
Clear Shape Key :kbd:`Alt-I`
   Will clear the shape key for the active mask layer at the current frame.
Feather Reset Animation
   Resets the feather offset across all animated frames.
Re-Key Points of Selected Shapes
   Re-interpolate selected points on across the range of keys selected in the *Dope Sheet*.


Show/Hide
=========

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Show/Hide`

- Hide Selected :kbd:`H`
- Hide Unselected :kbd:`Shift-H`
- Clear Restricted View :kbd:`Alt-H`


Delete
======

.. admonition:: Reference
   :class: refbox

   :Mode:      Mask Mode
   :Menu:      :menuselection:`Mask --> Delete`
   :Hotkey:    :kbd:`X`

Removes control points.


Miscellaneous
=============

Slide Spline Curvature
   :kbd:`LMB` click on curve and drag to move the handle.

Add Vertex and Slide :kbd:`Ctrl-LMB`
   :kbd:`Ctrl-LMB` is used to place new control points and define handle orientations by a continued mouse drag.
   A :kbd:`Ctrl-LMB` double-click will also close the curve if the last point was selected.

Add Feather Vertex and Slide :kbd:`Shift-LMB`
   :kbd:`Shift-LMB` is used to define a feathering outline curve. To create an initial feather,
   sliding from a spline control point outside or inside will create and position feather points.
   After this :kbd:`Shift-LMB`
   will insert new feather point and mouse sliding can be used to move them around.
