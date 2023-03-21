.. index:: Geometry Nodes; Mesh Circle
.. _bpy.types.GeometryNodeMeshCircle:

****************
Mesh Circle Node
****************

.. figure:: /images/node-types_GeometryNodeMeshCircle.webp
   :align: right
   :alt: Mesh Circle Node.

The *Mesh Circle* node generates a circular ring of edges that is optionally filled with faces.


Inputs
======

Vertices
   Number of vertices on the circle.
   No geometry is generated when the number is below three.

Radius
   Distance of the vertices from the origin.


Properties
==========

Fill Type
   How the circle is filled with faces.

   :None: Output just the edge ring without any faces.
   :N-Gon: Fill the circle with a single face.
   :Triangles: Fill the circle with triangles connected to a new vertex at the origin.


Outputs
=======

Mesh
   Standard geometry output.

UV Map
   A 2D vector representing the default X/Y coordinates of the :term:`UV Map` for the primitive's shape.
   This can be connected to the :doc:`/modeling/geometry_nodes/attribute/store_named_attribute`,
   to be used once the Geometry Nodes Modifier get applied.
   The UV map must be stored on the face corner in order to be accessed.
