
*********
Selecting
*********

Hair curves, while similar to regular curves are a bit different and have their own selection tools.
Many of these match their regular curve tools but are implemented differently
All hair curve selection operators are documented below for completeness.

These selection operators work in both Sculpt and Edit modes.


.. _bpy.ops.curves.set_selection_domain:

Selection Modes
===============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`3D Viewport Header --> Select Mode`
   :Shortcut:  :kbd:`1`, :kbd:`2`

   Note, this is only supported for "Hair Curves".

Selection modes limits selection operators to certain curve domains.
This feature is makes it easy to select whole segments at once, or to give more granular control over editing.

:Control Points:
   Allows selection of individual control points.
:Curve:
   Limits selection to whole curve segments.


Operators
=========

All
   Select all control points or curves.

None
   Deselect all control points or curves.

Invert
   Invert the selection.

Random
   Randomizes inside the existing selection or create new random selection if nothing is selected already.

Endpoints
   Select endpoints of curves.
   Only supported in the Control Point selection mode.

Grow
   Select points or curves which are close to already selected elements.
