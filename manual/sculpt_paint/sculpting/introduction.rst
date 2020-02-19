
************
Introduction
************

*Sculpt Mode* is similar to *Edit Mode* in that it is used to alter the shape of a model,
but Sculpt Mode uses a very different workflow:
instead of dealing with individual elements (vertices, edges, and faces),
an area of the model is altered using a brush.
In other words, instead of selecting a group of vertices,
Sculpt Mode manipulates geometry in the brush region of influence.


Sculpt Mode
===========

Sculpt Mode is selected from the mode menu of the 3D View header.
Once Sculpt Mode is activated, the Toolbar of the 3D View will change to
Sculpt Mode specific panels. The panels will be *Brush*, *Texture*, *Stroke*,
*Falloff*, *Display*, *Dyntopo*, *Symmetry*, and *Options*.
A red circle will appear and follow the location of the cursor in the 3D View.

.. note::

   To have a predictable brush behavior, apply the scale of your mesh.

.. figure:: /images/sculpt-paint_sculpting_introduction_mode-selector.png

   3D View Mode selector: Sculpt Mode.

.. figure:: /images/sculpt-paint_sculpting_introduction_brush-circle.png

   The cursor in Sculpt Mode.


The Brush
=========

Sculpt Mode uses a similar brush to other the other :doc:`painting modes </sculpt_paint/brush/introduction>`,
however, it is slightly more advanced. All the normal brush controls still apply,
and it functions the exact same however the brush for sculpting is displayed in 3D.
This means that the brush will follow the contours of the mesh and the is displayed
by orienting the brush to match the meshes :term:`normal`.
How closely the cursor follows the curvature of the mesh can be changed in the
:doc:`Brush Settings </sculpt_paint/sculpting/tool_settings/brush_settings>`.

The brush can also change depending on the currently active :doc:`tool </sculpt_paint/sculpting/tools>`
to better display how that tool works.
