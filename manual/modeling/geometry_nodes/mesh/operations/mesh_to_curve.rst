.. index:: Geometry Nodes; Mesh to Curve
.. _bpy.types.GeometryNodeMeshToCurve:

******************
Mesh to Curve Node
******************

.. figure:: /images/node-types_GeometryNodeMeshToCurve.webp
   :align: right
   :alt: Mesh to Curve node.

The *Mesh to Curve* node turns each string of connected mesh edges into a poly spline.
Whenever two or more strings cross each other, the splines will be split.

Loose vertices are ignored -- they will not be turned into single-point splines.

Attributes, both named and unnamed ones, are transferred to the resulting splines.
If there is a ``radius`` attribute, it will be applied as such,
although you may find it more convenient to use the
:doc:`/modeling/geometry_nodes/curve/write/set_curve_radius` for this.


Inputs
======

Mesh
   Standard mesh input.

Selection
   A field input evaluated on the edge domain to determine whether each edge will be included in the result.

   .. tip::

      Using this input is more efficient than deleting parts of the geometry before or after the conversion.


Properties
==========

This node has no properties.


Outputs
=======

Curve
   Generated curve.
