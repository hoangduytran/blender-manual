.. index:: Geometry Nodes; Rotate Euler
.. _bpy.types.FunctionNodeRotateRotation:

********************
Rotate Rotation Node
********************

.. figure:: /images/node-types_FunctionNodeRotateRotation.webp
   :align: right
   :alt: Rotate Euler node.

The *Rotate Rotate Rotation* node applies an additional rotation amount to a rotation value.

To rotate a :term:`Euler Rotation`, first use the :doc:`/modeling/geometry_nodes/utilities/rotation/euler_to_rotation`


Inputs
======

Rotation
   The rotation to rotate.

Rotate By
   Specifies how much a rotation is rotated.


Properties
==========

Space
   Base orientation for the rotation.

   :Global: Rotate a rotation in :term:`Global Space`.
   :Local: Rotate a rotation in :term:`Local Space`.


Outputs
=======

Rotation
   The rotated rotation.
