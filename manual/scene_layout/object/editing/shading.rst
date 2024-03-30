
*******
Shading
*******

.. _bpy.ops.object.shade_smooth:

Shade Smooth
============

.. reference::

   :Mode:      Object Mode
   :Menu:      :menuselection:`Object --> Shade Smooth`

The easiest way is to set an entire object as smooth or faceted by selecting a mesh object,
and in *Object Mode*, select *Shade Smooth* in the *Object* menu.
This forces the assignment of the "smoothing" attribute to each face in the mesh,
including when you add or delete geometry.

Notice that the outline of the object is still strongly faceted.
Activating the smoothing features does not actually modify the object's geometry;
it changes the way the shading is calculated across the surfaces (normals will be interpolated),
giving the illusion of a smooth surface.

Using :ref:`bpy.ops.object.shade_flat` will revert the shading back (normals will be constant)
to that shown in the first image below.

.. list-table:: Example mesh flat (left) and smooth-shaded (right).
   `Sample blend-file <https://archive.blender.org/wiki/2015/index.php/File:25-manual-meshsmooth-example.blend>`__.

   * - .. figure:: /images/scene-layout_object_editing_shading_example-flat.png
          :width: 200px

     - .. figure:: /images/scene-layout_object_editing_shading_example-smooth.png
          :width: 200px

Keep Sharp Edges
   Do not clear sharp edges (which are redundant with objects shaded as flat or smooth).
   This option is useful to not destroy data in case you want to revert changes later.


.. _bpy.ops.object.shade_smooth_by_angle:

Shade Smooth by Angle
=====================

.. reference::

   :Mode:      Object Mode
   :Menu:      :menuselection:`Object --> Shade Smooth by Angle`

Set the sharpness of mesh edges based on the angle between the neighboring faces.

Angle
   Maximum angle between face normals that will be considered as smooth.

The *Shade Flat* operator will revert the shading back to flat;
additionally, the *Shade Smooth* operator will disable all flat normals,
making the entire object appear smooth again.


.. _bpy.ops.object.shade_flat:

Shade Flat
==========

.. reference::

   :Mode:      Object Mode
   :Menu:      :menuselection:`Object --> Shade Flat`

Signify the object to render and display faces uniformly,
using the :ref:`Face Normals <modeling-meshes-structure-normals>`.
This is usually desirable for objects with flat surfaces.

Keep Sharp Edges
   Do not clear sharp edges (which are redundant with objects shaded as flat or smooth).
   This option is useful to not destroy data in case you want to revert changes later.
