.. index:: Geometry Nodes; Corners of Edge
.. _bpy.types.GeometryNodeCornersOfEdge:

********************
Corners of Edge Node
********************

.. figure:: /images/node-types_GeometryNodeCornersOfEdge.webp
   :align: right
   :alt: Corners of Edge node.

The *Corners of Edge* node retrieves face corners connected to each edge in a mesh.
The node first gathers a list of face corners which are connected to the edges.
It's important to note that the list only has one corner per face.
Using the :doc:`/modeling/geometry_nodes/mesh/topology/offset_corner_in_face`
to offset the index inside the face by 1 gives the other corner from the face that is connected to the edge.
That list is then sorted based on the values of the *Sort Weight* input.
The *Total* output is the number of connected faces/corners, and the *Corner Index*
output is one of those corners, chosen using the *Sort Index* input.

.. figure:: /images/modeling_geometry-nodes_corners-of-edge_explanation.png
   :align: center
   :width: 400px

   A graphic for which corners are returned for a given edge

* Red: selected edge
* Blue: corners that get individually returned, depending on the sorting
* Purple: corners that can be retrieved by offseting the blue corner indices using
  :doc:`/modeling/geometry_nodes/mesh/topology/offset_corner_in_face`

Inputs
======

Edge Index
   The index of the input edge.

   .. note::

      By default this uses the :doc:`index </modeling/geometry_nodes/geometry/read/input_index>`
      from the field context, which makes it important that the node is evaluated on
      the edge domain.

Weights
   Values used to sort the corners connected to the edge.
   By default the corners are sorted by index, so the corners with the smallest indices come first.

Sort Index
   Which of the sorted corners to use for the *Corner Index* output. If the value is larger than
   the total number of connected face corners, it will wrap around to the beginning.


Properties
==========

This node has no properties.


Outputs
=======

Corner Index
   A corner of the input edge in its face's winding order, chosen by the *Sort Index* input.

Total
   The number of faces or face corners connected to the edge.
