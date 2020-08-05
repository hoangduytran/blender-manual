
************
Cloth Filter
************

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Cloth Filter`

This tool works similar to to the :doc:`Cloth Brush </sculpt_paint/sculpting/tools/cloth>`,
however, this tool applies a cloth simulation to all vertices in the mesh at the same time.
To use this tool, click and drag away from the object to have a positive effect
and click and drag towards the mesh to have a negative effect.

.. tip::

   Vertices can be "pinned" by :doc:`masking` vertices that should remain stationary,
   or by using :ref:`Face Sets <sculpting-editing-facesets>`.

Filter Type
  Operation that is going to be applied to the mesh.

  Gravity
     Applies gravity to the simulation.
  Inflate
     Inflates the cloth.
  Expand
     Expands the cloth's dimensions.
  Pinch
     Pinches the cloth to the point were the cursor was when the filter started.

Strength
   The amount of effect the filter has on the mesh.

Cloth Mass
   Mass of each simulation particle.

Cloth Damping
   How much the applied forces are propagated through the cloth.

Use Face Sets
   Only applies the mesh filter to the vertices assigned to the
   :ref:`Face Set <sculpting-editing-facesets>` that is under the mouse.
