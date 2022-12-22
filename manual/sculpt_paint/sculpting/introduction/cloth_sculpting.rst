
***************
Cloth Sculpting
***************

Instead of sculpting cloth manually or creating complex physics simulation setups, 
there are various tools directly in sculpt mode that offer a simplified 
:doc:`Cloth Physics Simulation </physics/cloth/index>`.

.. figure:: /images/sculpt-paint_sculpt_cloth_example.png

This has various advantages but is especially useful for base mesh creation and larger clothing folds and draping.
Detailing is possible, but the slower performance on high resolution meshes and simplified cloth physics
might not lead to desireable results.

The resolution of the topology is the mainly responsible for the size of the folds 
and detail level of the simulation. So an optimal and evenly distributed topology is important.

Many sculpting features are supported, so for example :ref:`Masked <sculpt-mask-menu>` vertices 
are :doc:`pinned </physics/cloth/settings/shape>` in the simulation.
Another example is with :doc:`auto-masked </sculpt_paint/sculpting/controls>` face set boundaries.
The sculpt mode :ref:`gravity <bpy.types.Sculpt.gravity>` factor is also applied on the cloth physics.

The main brushes and tools for this feature are the `Cloth Brush` and `Cloth Filter`, 
but other transform brushes like `Pose` and `Boundary` also support cloth sculpting in the brush settings.

A demo file for trying out the various brushes and tools is available `here <https://www.blender.org/download/demo-files/#sculpting>`_.
