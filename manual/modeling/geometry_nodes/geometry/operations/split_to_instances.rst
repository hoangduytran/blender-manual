.. index:: Geometry Nodes; Split To Instances
.. _bpy.types.GeometryNodeSplitToInstances:

***********************
Split To Instances Node
***********************

.. figure:: /images/node-types_GeometryNodeSplitToInstances.webp
   :align: right
   :alt: Split to Instance node.

The *Split to Instances* node splits up geometry elements into :doc:`/modeling/geometry_nodes/instances`,
based on a Group ID.


Inputs
======

Geometry
   Standard geometry input.

Selection
   Boolean field that is true for parts of the geometry to be evaluated.
   Parts not in the selection will not be in the node's output.

Group ID
   ID field (integer) used to distinguish different groups.


Properties
==========

Domain
   The domain on which the selection and group ID fields are evaluated. 

   :Point:
      The fields are evaluated on points, control points, and vertices.
   :Edge:
      The fields are evaluated on the edges of the mesh component.
   :Faces:
      The fields are evaluated on the faces of the mesh component. 
   :Spline:
      The fields are evaluated on the splines in the curve component.
   :Instances:
      The fields are evaluated on the top-level instances. Realized instances are ignored.

.. note::

      When selecting a domain that doesn't modify all components, the unmodified
      components will not be present in the output.


Output
======

Instances
   input geometry splitted up as instances.

Group ID
   ID field from the input Group ID


Examples
========

.. figure:: /images/modeling_geometry-nodes_geometry_split-to-instances_example.png
   :align: center

   Here, a grid is split into instances based on a voronoi texture, then translated randomly in Z.
   Note that the GroupID field expects different integers values (0, 1, 2, 3…), not floats (0.1, 0.2, 0.3), 
   which is why the color needs to be multiplied by 1000. 
   


