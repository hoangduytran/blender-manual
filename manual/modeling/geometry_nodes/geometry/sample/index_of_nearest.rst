.. index:: Geometry Nodes; Index of Nearest
.. _bpy.types.GeometryNodeIndexOfNearest:

****************
Index of Nearest
****************

.. figure:: /images/node-types_GeometryNodeIndexOfNearest.webp
   :align: center
   :alt: Index of Nearest node.


Find the nearest element in a geometry.
It is similar to the :doc:`/modeling/geometry_nodes/geometry/sample/sample_nearest` node.

.. tip::

    This is often combined with the :doc:`/modeling/geometry_nodes/geometry/sample/sample_index` node.


Inputs
======

Position
   The position to start from when finding the closest location.
   By default, this is the same as if the :doc:`/modeling/geometry_nodes/geometry/read/position` was connected.

Group ID
   ID to group elements together.


Outputs
=======

Index
   The :doc:`index </modeling/geometry_nodes/geometry/read/input_index>` of the closest geometry element.

Has Neighbor
   This is true when the group of the element has at least two elements.
   This is only relevant when using *Group ID*.
