
*****
Cloth
*****

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Sculpt`

The Cloth brush uses a simplified :doc:`Cloth Solver </physics/cloth/index>`
to simulate cloth physics on the mesh under the brush.
:ref:`Masked <sculpt-mask-menu>` vertices are :doc:`pinned </physics/cloth/settings/shape>` in the simulation,
and it applies the sculpt :ref:`gravity <bpy.types.Sculpt.gravity>` directly in the solver.
Note, using a relatively small brush makes the solver's calculations much faster,
larger brush sizes might be too slow to get a usable brush.

Simulation Limit
   The Factor added relative to the size of the radius to limit the cloth simulation effects.
Simulation Falloff
   The area to apply deformation falloff to the effects of the simulation.
   This setting is a factor of the *Simulation Limit* and is shown as a dashed line around the cursor.

Deformation
   The type of cloth deformation that is used by the brush.

   Drag
      Simulates pulling the cloth to the cursor,
      similar to placing a finger on a table cloth and pulling.
   Push
      Simulates pushing the cloth away from the cursor,
      similar to placing a finger on a table cloth and pushing.
   Pinch Point
      Simulates pulling the cloth into a point.
   Pinch Perpendicular
      Simulates pulling the brush into a line.
   Inflate
      Simulates air being blown under the cloth so that the cloth lifts up.
   Grab
      Simulates picking up and moving the cloth.
   Expand
      Simulates stretching the cloth out.
Force Falloff
   Shape used in the brush to apply force to the cloth.

   Radial
      Applies the force as a sphere.
   Plane
      Applies the force as a plane.

Cloth Mass
   Mass of each simulation particle.
Cloth Damping
   How much the applied forces are propagated through the cloth.
