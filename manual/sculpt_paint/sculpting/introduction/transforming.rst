
************
Transforming
************

Transform tools to :doc:`move, rotate and scale </sculpt_paint/sculpting/tools/transforms>`
are also available in Sculpt Mode,
but with an important difference to other modes. Sculpt Mode uses its own pivot point,
which can be manually positioned via :ref:`bpy.ops.sculpt.set_pivot_position`
or automatically positioned with :ref:`Mask Expand <bpy.ops.sculpt.mask_expand>`.
This ensures that the pivot point can be more freely placed and always moves with the transformed geometry.

.. tip::
   For even more control, assign a shortcut to the Set Pivot to "Surface" menu operator.
   This way the pivot can be placed on any point on a surface, similar to placing the 3D Cursor.


Optionally instead of keeping the transform tools active, you can enable the
:doc:`viewport gizmos </editors/3dview/display/gizmo>` to have access to the gizmo at all times.

.. note::
   The gizmo can in some cases block areas from being sculpted on.
   In that case move the pivot point somewhere else to be able to click on the desired surface.

Apart from the transform tools there are also special brushes to move,
rotate and scale the topology like :doc:`Pose </sculpt_paint/sculpting/tools/pose>`,
:doc:`Boundary </sculpt_paint/sculpting/tools/boundary>`
and :doc:`Elastic Deform </sculpt_paint/sculpting/tools/elastic_deform>`.
