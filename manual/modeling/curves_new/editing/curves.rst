
******
Curves
******

Transform
=========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Curves --> Transform`

A curves objects can be edited by transforming the locations of control points.

Move, Rotate, Scale
   Like other elements in Blender, control points can be moved, rotated, or scaled as described in
   :doc:`Basic Transformations </scene_layout/object/editing/transform/introduction>`.
To Sphere, Shear, Bend, Push/Pull
   The transform tools are described in
   the :doc:`Transformations </modeling/meshes/editing/mesh/transform/index>` sections.


.. _bpy.ops.curves.duplicate_move:

Duplicate
=========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Curves --> Duplicate`
   :Shortcut:  :kbd:`Shift-D`

This operator duplicates the selected control points,
along with the curve segments implicitly selected (if any).
.. If only a handle is selected, the full point will be duplicated too.
The copy is selected so you can move it to another place.


.. _bpy.ops.curves.delete:

Delete
======

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Curves --> Delete`
   :Shortcut:  :kbd:`X`

The Delete operator can remove Control Points or Segments.
Deleting can be used to make curves shorter or simplify
segments by deleting control points in the mid section of a segment.
