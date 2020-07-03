.. _bpy.types.PivotConstraint:

****************
Pivot Constraint
****************

The *Pivot* constraint allows the owner to rotate around a target object.
It was originally intended for pivot joints found in humans
e.g. fingers, feet, elbows, etc.


Options
=======

.. TODO2.8
   .. figure:: /images/animation_constraints_relationship_pivot_panel.png

      Pivot panel.

Target
   :ref:`ui-data-id` for the selection of the object to be used as a pivot point.

Use Relative Offset
   Offset will be an absolute point in space instead of relative to the target.

Pivot Point X, Y, Z
   Offset of pivot from target.

Rotation Range
   Rotation range on which pivoting should occur.

   Always
      Use the pivot point in every rotation.
   -X/-Y/-Z/X/Y/Z Rotation
      Use the pivot point in the corresponding direction around the corresponding axis.


Example
=======

.. vimeo:: 171554353
