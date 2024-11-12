.. index:: Geometry Nodes; For Each Element
.. _bpy.types.GeometryNodeForEachGeometryElementInput:
.. _bpy.types.GeometryNodeForEachGeometryElementOutput:

******************************
For Each Geometry Element Zone
******************************

This zone type allows executing nodes for each element of a geometry. For example, the nodes can process
every face of a mesh, or every instance.

.. figure:: /images/modeling_geometry-nodes_foreach_geometry_element_zone.png
   :align: center

   The *For Each Element* zone.


Inputs
======

Selection
    Which subset of the chosen *Domain* to process.

Geometry
    Standard geometry input.

Properties
==========

Domain
   Which :ref:`attribute domain <attribute-domains>` to process.

Inspection Index
   Geometry element index that is used by inspection features like the :doc:`/modeling/geometry_nodes/output/viewer`
   or :doc:`socket inspection </modeling/geometry_nodes/inspection>`.
