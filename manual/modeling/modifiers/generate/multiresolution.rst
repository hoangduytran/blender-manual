..    TODO/Review: {{review|im=needs examples}}.

.. _bpy.types.MultiresModifier:

************************
Multiresolution Modifier
************************

The *Multiresolution* modifier (often shortened to "Multires") gives you the ability to subdivide a mesh similarly
to the :doc:`Subdivision Surface </modeling/modifiers/generate/subdivision_surface>` modifier,
but also allows you to edit the new subdivision levels in :doc:`Sculpt Mode </sculpt_paint/sculpting/introduction>`.

.. note::

   *Multiresolution* is the only modifier that cannot be repositioned in the stack after any modifier that will
   change geometry or other object data (i.e. all *Generate*, some *Modify* and some *Simulate* modifiers
   cannot come before the *Multiresolution* one).


Options
=======

.. figure:: /images/modeling_modifiers_generate_multiresolution_panel.png
   :align: right

   The Multiresolution modifier.

Type
   Sets the type of subdivision.

   Simple
      Maintains the current shape, and simply subdivides edges.
   Catmull-Clark
      Creates a smooth surface, usually smaller than the original, using the standard
      `Catmull-Clark <https://en.wikipedia.org/wiki/Catmull%E2%80%93Clark_subdivision_surface>`__
      subdivision surface algorithm.

Levels Viewport
   Set the level of subdivisions to show in Object Mode.
Sculpt
   Set the level of subdivisions to use in Sculpt Mode.
Render
   Set the level of subdivisions to show when rendering.

Optimal Display
   When rendering the wireframe of this object, the wires of the new subdivided edges will be skipped
   (only displays the edges of the original geometry).


Subdivisions
------------

Unsubdivide
   Rebuild a lower subdivision level of the current base mesh.

Subdivide
   Adds another level of subdivision.

Delete Higher
   Deletes all subdivision levels that are higher than the current one.


Shape
-----

Reshape
   Copies vertex coordinates from another mesh.

   To use it, first select a different mesh object with matching topology and vertex indices,
   then :kbd:`Shift` select the object you wish to copy vertex coordinates to, and click *Reshape*.

Apply Base
   Modifies the original unsubdivided mesh to match the form of the subdivided mesh.


Generate
--------

Rebuild Subdivisions
   Rebuilds all possible subdivisions levels to generate a lower resolution base mesh.
   This is used to create an optimized multiresolution version of a pre-existing sculpt.
   This option is only available when no subdivision level have been created through the modifier.

Save External
   Saves displacements to an external ``.btx`` file.


Advanced
--------

Quality
   How precisely the vertices are positioned (relatively to their theoretical position),
   can be lowered to get a better performance when working on high-poly meshes.

UV Smooth
   How to handle UVs during subdivision.

   Smooth, keep corners
      UV islands are smoothed, but their boundary remain sharp.
   Sharp
      UV remain unchanged.

Use Custom Normals
   Interpolates existing :ref:`modeling_meshes_normals_custom` to resulting mesh.
