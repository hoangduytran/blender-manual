
************
Cloth Filter
************

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Cloth Filter`

This tool works similar to the :doc:`Cloth Brush </sculpt_paint/sculpting/tools/cloth>`,
however, it applies a cloth simulation to all vertices in the mesh at the same time.
Click and drag away from the object for a positive effect and towards for a negative effect.

.. tip::

   Vertices can be "pinned" by :doc:`masking </sculpt_paint/sculpting/tools/mask>` vertices
   that should remain stationary, or by using :ref:`Face Sets <sculpting-editing-facesets>`.


Brush Settings
==============

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

Force Axis
   Apply the force along the selected axis.

Orientation
   :doc:`Orientation </editors/3dview/controls/orientation>` of the axis to limit the filter force.

   Local
      Use the Local axis to limit the force and set the gravity direction.
   World
      Use the World axis to limit the force and set the gravity direction.
   View
      Use the View axis to limit the force and set the gravity direction.

Cloth Mass
   Mass of each simulation particle.

Cloth Damping
   How much the applied forces are propagated through the cloth.

Use Face Sets
   Only applies the cloth forces to the vertices assigned to the :ref:`Face Set <sculpting-editing-facesets>`
   that are under the mouse.
