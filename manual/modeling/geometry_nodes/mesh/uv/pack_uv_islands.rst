.. index:: Geometry Nodes; Pack UV Islands
.. _bpy.types.GeometryNodeUVPackIslands:

********************
Pack UV Islands Node
********************


.. figure:: /images/node-types_GeometryNodeUVPackIslands.webp
   :align: right
   :alt: Pack UV Islands node.

The *Pack UV Islands Node* scales islands of a UV map and moves them so they fill the UV space as much as possible.


.. seealso::

   The :ref:`bpy.ops.uv.pack_islands` operator performs a similar operation in the UV editor.


Inputs
======

UV
   The UV map to modify.

Selection
   Faces to consider when packing islands.
   UVs that are part of any other face will not be affected.

Margin
   The distance to leave between UV islands.

Rotate
   Allow Rotating islands for best fit.

Method
   The method to use when considering the shape of each island.

   :Bounding Box: Uses the simple bounding box of the island.
   :Convex Hull):
      Takes into account the boundary (Convex Hull) of the island.
      This method will not place islands inside holes.
   :Exact Shape:
      Use the complete shape of the island, including filling any holes or concave regions around the island.


Output
======

UV
   The modified UVs.
