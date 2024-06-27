.. index:: Geometry Nodes; Axis to Rotation
.. _bpy.types.FunctionNodeAxesToRotation:

*********************
Axis to Rotation Node
*********************

.. figure:: /images/node-types_FunctionNodeAxesToRotation.webp
    :align: right
    :alt: Axis to Rotation node.

The *Axis to Rotation* node creates a rotation from a primary and secondary axis.

The node rotates one axis (X, Y, or Z) to the given primary axis direction.
Then it rotates around that primary direction to align the second axis to the given secondary direction.
Ideally, both input axes are orthogonal.

.. tip::

   In many cases, the primary and secondary axis inputs are a normal and tangent of a mesh or curve.


Inputs
======

Primary Axis
   The amount of rotation around the primary axis.

Secondary Axis
   The amount of rotation around the secondary axis.


Properties
==========

Primary Axis
   Axis that is aligned exactly to the provided primary direction.

Secondary Axis
   Axis that is aligned as well as possible given the alignment of the primary axis.


Outputs
=======

Rotation
    Standard rotation value.
