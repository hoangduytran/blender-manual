
****************
Simulation Nodes
****************

Through the use of :doc:`Simulation Zones </modeling/geometry_nodes/simulation/simulation_zone>`,
:doc:`/modeling/geometry_nodes/index` can be used to create custom physic simulations through nodes.
Simulation zones allow the result of one frame to influence the next one.
That way even a set of simple rules can lead to complex results, with the passing of time.
The most common type of them is physics simulation, with specific solvers for physical phenomena.

.. seealso::

   Read more about :doc:`Simulation Zones </modeling/geometry_nodes/simulation/simulation_zone>`


.. _bpy.types.Object.use_simulation_cache:
.. _bpy.ops.object.simulation_nodes_cache_calculate_to_frame:
.. _bpy.ops.object.simulation_nodes_cache_bake:
.. _bpy.ops.object.simulation_nodes_cache_delete:

Baking
======

The simulation is automatically cached during playback.
The valid cache can be seen as a strong yellow line in the timeline editor.
This allows for animators to quickly inspect all the previous frames of a simulation.

.. figure:: /images/modeling-geometry_nodes-simulation-baking_timeline.png
   :align: center

   Cached frames in the Timeline.

For the cases where the current frame is the only one relevant, users can opt-out of "Keep All Cache" to save memory.

When the result is ready to be sent to a render-farm, it can be baked to disk.
This allows for the simulation to be rendered in a non-sequential order.

.. figure:: /images/modeling-geometry_nodes-simulation-baking.png
   :align: center

   Simulation and Physics, Geometry Nodes user interface.

.. note::

   Baking the simulation will bake all the simulations in all modifiers for the selected objects.


Examples
========

Combined with the :doc:`/modeling/geometry_nodes/geometry/sample/index_of_nearest`,
this can be used for a number of sphere-based simulations.

.. figure:: /images/modeling-geometry_nodes-simulation-example.png
   :align: center

   Index of Nearest sample file CC-BY Sean Christofferson.
