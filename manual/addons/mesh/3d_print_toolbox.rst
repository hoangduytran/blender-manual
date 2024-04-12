
****************
3D Print Toolbox
****************

.. reference::

   :Category: Mesh
   :Description: Utilities for 3D printing.
   :Location: :menuselection:`3D Viewport --> Sidebar`
   :File: object_print3d_utils folder
   :Author: Campbell Barton


Installation
============

- This add-on is bundled with Blender.
- Open Blender and go to Preferences, then the Add-ons tab.
- Click Mesh then 3D Print Toolbox to enable the script.


Description
===========

Blender can be used to create meshes for 3D printing.
Meshes exported from Blender are usually imported into a piece of software that
takes the mesh and "slices" it into paths that the 3D printer can execute.
An example of such `Slicer <https://en.wikipedia.org/wiki/Slicer_(3D_printing)>`__
software is `Cura <https://github.com/Ultimaker/Cura>`__.

In order to correctly slice a mesh, it needs to be "watertight",
meaning that the surface is closed everywhere. Additionally,
there should be no edges or faces sticking out.
3D Print Toolbox helps you analyze problems in your mesh that could cause slicing issues.

It can be found in :menuselection:`3D Viewport --> Sidebar --> 3D-Print`, when a mesh is selected.

--------------

Analyze
=======

Statistics
----------

By clicking either `Volume` or `Area`, the volume or area of the mesh is calculated and shown.


Checks
------

.. figure:: /images/3dprint_checks.jpg
   :align: right

   The Checks panel.

A number of different checks can be performed to analyze
in which ways your mesh might be invalid for use with a Slicer.

Upon execution of one of the checks, the `Result` field shows which, if any, parts of your mesh are invalid.

When in `Edit Mode`, clicking these results selects these parts of your mesh.
You can use `View Selected` :kbd:`Backslash` to focus on these parts.

Although Slicers are becoming increasingly tolerant when it comes to "tidiness"
of meshes, it is always worth trying to provide as clean a mesh as possible.

--------------

Solid
   Checks for Non-Manifold edges and Bad Contiguous edges.

   Edges should connect to exactly 2 faces. If it connects to only one,
   it means there's a hole in the mesh. More is also not allowed. These edges are considered Non-manifold.
   If one of the faces' normals is pointing in a different direction than its neighbors,
   its edges are marked as "Bad Contiguous".

   In this screenshot, the left shape has a hole, and the right shape has one of its faces flipped.

   .. figure:: /images/3dprint_solid.jpg

      Left, marked in blue: Non-manifold edges. Right, marked in red: Bad contiguous edges.

Intersections
   These two cubes have intersecting faces. A Boolean modifier would help in this example.
   It's worth noting that some slicer applications can deal with this,
   so it's not always required to resolve this issue.

   .. figure:: /images/3dprint_intersect.jpg

Degenerate
   Faces and edges which have 0 area or length, are considered `degenerate`.
   In this example, the top face of a cube has been scaled down to 0,
   but have not been merged. A :menuselection:`Merge --> By Distance` would resolve this issue.

   .. figure:: /images/3dprint_degenerate.jpg

      There's a hidden face here.

Distorted
   The vertices of a quad or ngon can be folded in such a way that the face is not flat.
   In practice, quads are rarely ever flat. When exporting, these faces are converted to triangles.
   If the surface is excessively deformed, this can result in unexpected shapes.

   In this example, a quad has been folded into a saddle-like shape.
   This triggers the `Distorted` check. It would be best to triangulate by hand here.

   .. figure:: /images/3dprint_distorted.jpg

      This quad can triangulate in unexpected ways.

Thickness
   Faces that form very thin geometry might be missed entirely by the slicer. Such faces are marked as `Thin`.

   .. figure:: /images/3dprint_thickness.jpg

Edge Sharp
   Similar to `Thickness`, sharp edges can thin pieces of geometry which might be missed by the `slicer`

Overhang
   As 3D printers can't print in mid-air, parts of the model which overhang will not print correctly.
   In practice, slicers can add additional material, `support`, to anticipate for overhanging layers.

   .. figure:: /images/3dprint_overhang.jpg

Check All
   Performs all of the above checks at once. In this example, Suzanne shows quite a few problems.
   This is because the eyes are separate parts, and the sockets have holes.
   This makes the mesh not `Solid` and `Intersecting`. Some of the faces are `Distorted`.

   .. figure:: /images/3dprint_suzanne.jpg


Clean Up
========

Distorted
  Triangulates the faces which are considered `Distorted`, as explained above.

Make Manifold
  Attempts to fix various problems which might make a mesh non-manifold,
  such as by fixing `bad normals`, filling holes, and removing empty edges and faces.


Edit
====

Hollow
------

This tool generates an offset surface from the target object using `OpenVDB <https://www.openvdb.org/>`__.
It is useful for hollowing out a model for 3D printing, for instance, to save material and/or speedup print.
It is also possible to create a thin-walled mold for the object, when using an outside offset surface.

The target object must be a closed surface to allow for an inside offset surface, but not necessarily manifold.
On the other hand, outside offset surfaces can be created even for open objects.

Offset Direction
   Where the offset surface is created relative to the object. An *Inside* surface is useful to hollow out the the
   target, while an *Outside* surface can be used to create a thin-walled mold.

Offset
   Surface offset in relation to the original mesh.

Voxel size
   Lower values capture finer details but increase processing time and memory usage. Too large a value may lead to
   the offset surface intersecting the original object.

Hollow Duplicate
   When unchecked, only the offset surface is generated. When checked, the tool generates a hollowed out copy
   of the target.

.. figure:: /images/3dprint_hollow_in_out.jpg

   An inside (left) and an outside (right) hollowed out object, both cut in half to show the interior.


Scale To
--------

Volume
   Scales the model to an exact given volume.

Bounds
   Scales the model so that the biggest axis of the objects `bounds` (or `dimensions`) match the given value.

Align XY
--------

Rotates the object so that the selected faces are parallel, in average, to the XY plane.

Face Areas
   Take into account the sizes of the selected faces, so that larger ones contribute proportionally more to
   the orientation than the smaller ones.

Export
======

Provides quick access to Blender's object exporting operators found in :menuselection:`File --> Export`.
