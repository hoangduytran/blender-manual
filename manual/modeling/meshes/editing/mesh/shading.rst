.. _modeling-meshes-editing-normals-shading:

*******
Shading
*******

.. admonition:: Reference
   :class: refbox

   :Mode:      Object Mode
   :Menu:      :menuselection:`Object --> Shade Smooth / Shade Flat`

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Mesh --> Shading`
   :Menu:      :menuselection:`Face --> Shade Smooth / Shade Flat`


.. _bpy.ops.object.shade_flat:

Flat
====

.. list-table:: Example mesh flat (left) and smooth-shaded (right).
   `Sample blend-file <https://wiki.blender.org/wiki/File:25-manual-meshsmooth-example.blend>`__.

   * - .. figure:: /images/modeling_meshes_editing_normals_example-flat.png
          :width: 200px

     - .. figure:: /images/modeling_meshes_editing_normals_example-smooth.png
          :width: 200px

As seen in the previous sections, polygons are central to Blender.
Most objects are represented by polygons and truly curved objects
are often approximated by polygon meshes. When rendering images,
you may notice that these polygons appear as a series of small, flat faces.
Sometimes this is a desirable effect, but usually we want our objects to look nice and smooth.


.. _bpy.ops.object.shade_smooth:

Smooth
======

The easiest way is to set an entire object as smooth or faceted by selecting a mesh object,
and in *Object Mode*, select *Shade Smooth* in the *Object* menu.
This forces the assignment of the "smoothing" attribute to each face in the mesh,
including when you add or delete geometry.

Notice that the outline of the object is still strongly faceted.
Activating the smoothing features does not actually modify the object's geometry;
it changes the way the shading is calculated across the surfaces (normals will be interpolated),
giving the illusion of a smooth surface.

Select the *Shade Flat* item in the *Object* menu
to revert the shading back (normals will be constant)
to that shown in the first image above.


Smoothing Parts of a Mesh
-------------------------

Alternatively, you can choose which faces to smooth by entering *Edit Mode*,
then selecting some faces and picking *Shade Smooth* from the *Face Menu*.

When the mesh is in *Edit Mode*,
only the selected faces will receive the "smoothing" attribute.
You can set faces as flat (removing the "smoothing" attribute)
in the same way by selecting edges and picking the *Shade Flat* from the *Face Menu*.

.. seealso::

   The :ref:`Auto Smooth <auto-smooth>` option is a quick and easy way to combine smooth and
   faceted faces in the same object.
