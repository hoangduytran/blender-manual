.. _bpy.ops.mesh.blend_from_shape:

****************
Blend from Shape
****************

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Blend from Shape`

The *Blend from Shape* operator blends the current mesh towards the vertex positions
stored in a :doc:`Shape Key </animation/shape_keys/index>`.
This allows you to reuse existing shape keys to partially or fully reshape geometry in *Edit Mode*.

This is useful for:

- Correcting or refining geometry by borrowing deformations from a shape key.
- Copying specific shape features into a mesh while editing.
- Mixing shapes interactively without leaving Edit Mode.


Options
=======

Shape
   The shape key to blend from.

Blend
   Factor controlling how much of the shape is applied.

Add
   If enabled, the blended offset is added on top of the current mesh positions.
   If disabled, the mesh is interpolated directly between its current shape and the chosen shape key.
