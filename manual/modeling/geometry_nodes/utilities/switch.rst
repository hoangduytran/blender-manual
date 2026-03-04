.. index:: Geometry Nodes; Switch
.. _bpy.types.GeometryNodeSwitch:

***********
Switch Node
***********

.. figure:: /images/node-types_GeometryNodeSwitch.webp
   :align: right
   :alt: Switch Node.

The *Switch* node outputs one of two inputs depending on a condition.

When the inputs are regular values, only the input that is passed through
the node is evaluated. This means the unused input is not computed.

When the inputs are :term:`fields <Field>`, both inputs may be evaluated
before the switch is applied. The switch then selects which result is used
for each element. Because of this, the node should not be relied on to avoid
evaluating expensive field inputs.

.. seealso::

   The :doc:`/modeling/geometry_nodes/utilities/menu_switch`
   and :doc:`/modeling/geometry_nodes/utilities/index_switch`
   can be used to switch between an arbitrary amount of inputs.


Inputs
======

Switch
   Determines which of the two inputs below will be passed through.

False
   Is passed through when the switch is set to false.

True
   Is passed through when the switch is set to true.


Properties
==========

Type
   Determines the type of the data that is handled by the node.


Outputs
=======

Output
   One of the two inputs without any modifications.
