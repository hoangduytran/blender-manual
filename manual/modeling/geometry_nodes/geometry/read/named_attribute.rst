.. index:: Geometry Nodes; Named Attribute
.. _bpy.types.GeometryNodeInputNamedAttribute:

********************
Named Attribute Node
********************

.. figure:: /images/node-types_GeometryNodeNamedAttribute.png
   :align: right
   :alt: Named Attribute node.

The *Named Attribute* node outputs the data of an attribute based on the
context of where it is connected (the :ref:`field-context`).


Inputs
======

Name
   The name of the attribute to read.


Properties
==========

Data Type
   The :ref:`data type <attribute-data-types>` used for the retrieved data.
   :ref:`geometry-nodes-attribute-search` can be used to give a basic list of possible
   attribute names and data types. When a value is chosen from the search menu, the data
   type is set to automatically choose the data type from the geometry nodes result.

Outputs
=======

Attribute
   The attribute data stored on the geometry.
