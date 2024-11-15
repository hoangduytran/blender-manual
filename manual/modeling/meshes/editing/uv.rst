
************
UV Operators
************

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`Header --> UV`
   :Shortcut:  :kbd:`U`

Blender offers several ways of mapping UVs.
The simpler projection methods use formulas that map 3D space onto 2D space,
by interpolating the position of points toward a point/axis/plane through a surface.
The more advanced methods can be used with more complex models, and have more specific uses.


.. _bpy.ops.uv.unwrap:

Unwrap
======

.. reference::

   :Editor:    3D Viewport and UV Editor
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Unwrap`
   :Shortcut:  :kbd:`U`

Flattens the mesh surface by cutting along :doc:`seams </modeling/meshes/uv/unwrapping/seams>`.
Useful for organic shapes.


Begin by selecting all the faces you want to unwrap.
In the 3D Viewport, select :menuselection:`UV --> Unwrap` or :kbd:`U` and select :menuselection:`Unwrap`.
You can also do this from the UV Editor with :menuselection:`UV --> Unwrap` or :kbd:`U`.
This method will unwrap all faces and reset previous work.
The UVs menu will appear in the UV Editor after unwrapping has been performed once.

.. figure:: /images/modeling_meshes_editing_uv_unwrap-example.png
   :width: 420px

   Result of unwrapping Suzanne.

This operation unwraps the faces of the object to provide
the "best fit" scenario based on how the faces are connected and will fit within the image,
and takes into account any seams within the selected faces.
If possible, each selected face gets its own different area of the image and is not overlapping any other faces UVs.
If all faces of an object are selected, then each face is mapped to a part of the image.

.. tip::

   A face's UV image texture only has to use *part* of the image, not the *whole* image.
   Also, portions of the same image can be shared by multiple faces.
   A face can be mapped to less and less of the total image.


Options
-------

The :ref:`bpy.ops.screen.redo_last` panel allows fine control over how a mesh is unwrapped:

Method
 :Angle Based:
   Uses Angle Based Flattening (ABF). This method gives a good 2D representation of a mesh.
 :Conformal:
   Uses Least Squares Conformal Mapping (LSCM).
   This usually results in a less accurate UV mapping than Angle Based, but performs better on simpler objects.
 :Minimum Stretch:
   Uses Scalable Locally Injective Mapping (SLIM).
   This tries to balance minimizing area distortion and minimizing angle distortion.
Fill Holes
   Activating Fill Holes will prevent overlapping from occurring and better represent any holes in the UV regions.
Correct Aspect
   Map UVs will take the image's aspect ratio into consideration.
   If an image has already been mapped to the :term:`Texture Space` that is non-square,
   the projection will take this into account and distort the mapping to appear correctly.
Use Subdivision Surface
   Map UVs taking vertex position after Subdivision Surface Modifier into account.
Iterations
   The Minimum Stretch method is iterative, where each iteration reduces the distortion more.
   This option says how many iterations to use before stopping.
Allow Flips
   When using the Minimum Stretch method this option allows faces to flip, which sometimes results in less distortion
   when there are pins.
Importance Weights
   The Minimize Stretch method has a feature that allows a user-specified vertex group to control the relative amount
   of area used by different parts of the unwrapped map. Vertices with higher weights will mark portions of the mesh
   whose adjacent UV map faces should be stretched larger than smaller-weight areas. When this option is chosen, there
   are two additional options to control this:

   :Attribute: The name of the vertex group with the weights to be used.
   :Factor: A global factor to multiply all the weights. A bigger number will result in a more exaggerated difference
    between high-weight and low-weight areas.
Margin Method
   The method to use when calculating the empty space between islands.

   :Scaled: Use scale of existing UVs to multiply margin.
   :Add: Simple method, just add the margin.
   :Fraction: Precisely specify the fraction of the UV unit square for margin. (Slower than other two methods.)
Margin
   The scale for the empty space between islands.


.. _bpy.ops.uv.smart_project:

Smart UV Project
================

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Smart UV Project`
   :Shortcut:  :kbd:`U`

Smart UV Project, cuts a mesh based on an angle threshold (angular changes in your mesh).
This gives you fine control over how automatic seams are created.
It is a good method for simple and complex geometric forms,
such as mechanical objects or architecture.

This algorithm examines the shape of your object,
the selected faces and their relation to one another,
and creates a UV map based on this information and settings that you supply.

In the example below, the Smart Mapper mapped all of the faces of a cube to a neat arrangement of three sides on top,
three sides on the bottom, for all six sides of the cube to fit squarely, just like the faces of the cube.

.. figure:: /images/modeling_meshes_editing_uv_smart-project.png
   :width: 670px

   Smart UV project on a cube.

For more complex mechanical objects,
this operator can quickly and easily create a regular and straightforward UV layout.


Options
-------

The :ref:`bpy.ops.screen.redo_last` panel allows fine control over how a mesh is unwrapped:

Angle Limit
   This controls how faces are grouped: a higher limit will lead to many small groups but less distortion,
   while a lower limit will create fewer groups at the expense of more distortion.
Margin Method
   The method to use when calculating the empty space between islands.

   :Scaled: Use scale of existing UVs to multiply margin.
   :Add: Simple method, just add the margin.
   :Fraction: Precisely specify the fraction of the UV unit square for margin. (Slower than other two methods.)
Rotation Method
   :Axis-aligned: Rotated to a minimal rectangle, either vertical or horizontal.
   :Axis-aligned (Horizontal): Rotate islands to be aligned horizontally.
   :Axis-aligned (Vertical): Rotate islands to be aligned vertically.
Island Margin
   This controls how tightly the UV islands are packed together.
   A higher number will add more space between islands.
Area Weight
   Weight projection's vector by faces with larger areas.
Correct Aspect
   Map UVs will take the image's aspect ratio into consideration.
   If an image has already been mapped to the :term:`Texture Space` that is non-square,
   the projection will take this into account and distort the mapping to appear correctly.
Scale to Bounds
   If the UV map is larger than the (0 to 1) range, the entire map will be scaled to fit inside.


.. _bpy.ops.uv.lightmap_pack:

Lightmap Pack
=============

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Lightmap Pack`
   :Shortcut:  :kbd:`U`

Lightmap Pack takes each of a mesh's faces, or selected faces,
and packs them into the UV bounds. Lightmaps are used primarily in realtime rendering,
where lighting information is baked onto texture maps,
when it is needed to use as much UV space as possible.
It has several options that appear in the :ref:`bpy.ops.screen.redo_last` panel:


Options
-------

Selection
   :Selected Faces: Only unwraps the selected faces.
   :All Faces: Unwraps the whole mesh.
Share Texture Space
   This is useful if mapping more than one mesh.
   It attempts to fit all of the objects' faces in the UV bounds without overlapping.
New UV Map
   If mapping multiple meshes, this option creates a new UV map for each mesh.
   See :ref:`uv-maps-panel`.
Pack Quality
   Pre-packing before the more complex Box packing.
Margin
   This controls how tightly the UV islands are packed together.
   A higher number will add more space between islands.


.. _bpy.ops.uv.follow_active_quads:

Follow Active Quads
===================

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Follow Active Quads`
   :Shortcut:  :kbd:`U`

Extrapolate UV's based on the active quad by following continuous face loops,
even if the mesh face is irregularly-shaped.

.. note::

   For a clean 90-degree unwrap it's typically best to first make sure the quad a rectangle in UV space.

   Otherwise any distortion in the active UV is extended which doesn't result in a useful grid-layout.

.. note::

   The resulting unwrap is not clamped within the UV bounds,
   you may wish to scale down the active quad's UV's so the result is in a usable range.


Options
-------

Edge Length Mode
   Method to space UV edge loops.

   :Even:
      Space all UVs evenly, where the shape of the quad in the 3D viewport is ignored.
   :Length:
      Each face's UV's are calculated based on the edge length.

      While this minimizes distortion, adjacent loops may become disconnected.
   :Length Average:
      Average space UVs edge length of each loop.

      This has the benefit of minimizing distortion, while keeping UV's connected.


.. _bpy.ops.uv.cube_project:

Cube Projection
===============

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Cube Projection`
   :Shortcut:  :kbd:`U`

Cube Projection maps the mesh onto the faces of a cube, which is then unfolded.
It projects the mesh onto six separate planes, creating six UV islands.
In the UV editor, these will appear overlapped, but can be moved.
See :doc:`Editing UVs </modeling/meshes/uv/editing>`.


Options
-------

Cube Size
   Set the size of the cube to be projected onto.
Correct Aspect
   Map UVs will take the image's aspect ratio into consideration.
   If an image has already been mapped to the :term:`Texture Space` that is non-square,
   the projection will take this into account and distort the mapping to appear correctly.
Clip to Bounds
   Any UVs that lie outside the (0 to 1) range will be clipped to that range
   by being moved to the UV space border it is closest to.
Scale to Bounds
   If the UV map is larger than the (0 to 1) range, the entire map will be scaled to fit inside.


.. _bpy.ops.uv.cylinder_project:

Cylinder Projection
===================

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Cylinder Projection`
   :Shortcut:  :kbd:`U`

Normally, to unwrap a cylinder (tube) as if you slit it lengthwise and folded it flat,
Blender wants the view to be vertical, with the tube standing "up".
Different views will project the tube onto the UV map differently, skewing the image if used.
However, you can set the axis on which the calculation is done manually.


Options
-------

Direction
   :View on Poles:
      Use when viewing from the top (at a pole) by using an axis that is straight down from the view.
   :View on Equator:
      Use if view is looking at the equator, by using a vertical axis.
   :Align to Object:
      Uses the object's transform to calculate the axis.
Align
   How to determine rotation around the pole.

   :Polar ZX: Polar 0 is on the X axis.
   :Polar ZY: Polar 0 is on the Y axis.
Pole
   How to handle faces at the poles.

   :Pinch: UVs are pinched at the poles.
   :Fan: UVs are fanned at the poles.
Preserve Seams
   Separate projections by islands isolated by seams.
Radius
   The radius of the cylinder to use.
Correct Aspect
   Map UVs will take the image's aspect ratio into consideration.
   If an image has already been mapped to a :term:`Texture Space` that is non-square,
   the projection will take this into account and distort the mapping to appear correctly.
Clip to Bounds
   Any UVs that lie outside the (0 to 1) range will be clipped to that range
   by being moved to the UV space border it is closest to.
Scale to Bounds
   If the UV map is larger than the (0 to 1) range, the entire map will be scaled to fit inside.


.. _bpy.ops.uv.sphere_project:

Sphere Projection
=================

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Sphere Projection`
   :Shortcut:  :kbd:`U`

Spherical mapping is similar to cylinder but the difference is that
a cylindrical mapping projects the UVs on a plane toward the cylinder shape,
while a spherical map takes into account the sphere's curvature,
and each latitude line becomes evenly spaced.
*Sphere Projection* is useful for spherical shapes, like eyes, planets, etc.

Recall the opening cartographer's approaching to mapping the world? Well,
you can achieve the same here when unwrapping a sphere from different points of view.
Normally, to unwrap a sphere, view the sphere with the poles at the top and bottom.
After unwrapping, Blender will give you an equirectangular projection;
the point at the equator facing you will be in the middle of the image.
A polar view will give a very different but common projection map.
Using an equirectangular projection map of the earth as the UV image
will give a good planet mapping onto the sphere.

.. figure:: /images/modeling_meshes_editing_uv_sphere-projection.png

   Using an equirectangular image with a Sphere Projection.


Options
-------

Direction
   Direction of the sphere.

   :View on Poles:
      Use when viewing from the top (at a pole) by using an axis that is straight down from the view.
   :View on Equator:
      Use if view is looking at the equator, by using a vertical axis.
   :Align to Object:
      Uses the object's transform to calculate the axis.
Align
   Select which axis is up.

   :Polar ZX: Polar 0 is on the X axis.
   :Polar ZY: Polar 0 is on the Y axis.
Pole
   How to handle faces at the poles.

   :Pinch: UVs are pinched at the poles.
   :Fan: UVs are fanned at the poles.
Preserve Seams
   Separate projections by islands isolated by seams.
Correct Aspect
   Map UVs will take the image's aspect ratio into consideration.
   If an image has already been mapped to a :term:`Texture Space` that is non-square,
   the projection will take this into account and distort the mapping to appear correctly.
Clip to Bounds
   Any UVs that lie outside the (0 to 1) range will be clipped to that range
   by being moved to the UV space border it is closest to.
Scale to Bounds
   If the UV map is larger than the (0 to 1) range, the entire map will be scaled to fit inside.


.. _bpy.ops.uv.project_from_view:

Project from View
=================

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Project from View`
   :Shortcut:  :kbd:`U`

Project from View takes the current view in the 3D Viewport and flattens the mesh as it appears.
Use this option if you are using a picture of a real object as a UV Texture for an object that
you have modeled. You will get stretching in areas where the model recedes away from you.


Options
-------

Orthographic
   Apply an orthographic projection.
Camera Bounds
   Map UVs to the camera region taking resolution and aspect into account
Correct Aspect
   Map UVs will take the image's aspect ratio into consideration.
   If an image has already been mapped to a :term:`Texture Space` that is non-square,
   the projection will take this into account and distort the mapping to appear correctly.
Clip to Bounds
   Any UVs that lie outside the (0 to 1) range will be clipped to that range
   by being moved to the UV space border it is closest to.
Scale to Bounds
   If the UV map is larger than the (0 to 1) range, the entire map will be scaled to fit inside.


Project from View (Bounds)
==========================

.. reference::

   :Editor:    3D Viewport
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Project from View (Bounds)`
   :Shortcut:  :kbd:`U`

The same as :ref:`bpy.ops.uv.project_from_view`, but with *Scale to Bounds* activated by default.


.. _bpy.ops.uv.reset:

Reset
=====

.. reference::

   :Editor:    3D Viewport and UV Editor
   :Mode:      Edit Mode
   :Menu:      :menuselection:`UV --> Reset`
   :Shortcut:  :kbd:`U`

Reset UVs maps each face to fill the UV grid, giving each face the same mapping.

If you want to use an image that is tileable,
the surface will be covered in a smooth repetition of that image,
with the image skewed to fit the shape of each individual face.
Use this unwrapping option to reset the map and undo any unwrapping (go back to the start).
