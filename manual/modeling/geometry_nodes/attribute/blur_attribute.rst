.. index:: Geometry Nodes; Blur Attribute
.. _bpy.types.GeometryNodeBlurAttribute:

************************
Blur Attribute Node
************************

.. figure:: /images/node-types_GeometryNodeBlurAttribute.jpg
   :align: right
   :alt: Blur Attribute node.
   :width: 300px

The *Blur Attribute* node is implementation of Blur effect for attributes based on geometry topology.

Meen of each step is mixing value of each primitive with neighbors.
Weight of primitive is factor for multiplying all neighboards value before accumulate its as new primitive value.

Blurring can work when values on primitives have explicit relations.
Therefore, the attribute can only be affected on the :doc:`Meshes </modeling/meshes/introduction>` and :doc:`Curves </modeling/curves/introduction>` components.

Attribute domain expect same limitation as components.
Explicit relation for correct blurring have Points, Edges, Faces of mesh, and Points of curve.

.. note::

   Face corner no implemented due to this type of primitive have a lot of possible relation that mean it can't be implemented in general correct.

Defining domain of node inputs evaluating is based on context of node output evaluation.

For correct expected result available all :ref:`Attribute Type <attribute-data-types>` without boolean.
The Boolean attribute type has mixing issues.

.. tip::

   You can avoid this limitation with using Int type.


Inputs
======

Value
   The immediate value of each primitive to blur.

Iterations
   Number of repeats of mixing value with neighboards.
   Each iteration is independent. Until one iteration is completed, its results are not used as a source for next blurring.

Weight
   Weight of each primitive.


Properties
==========

Data Type
   The :ref:`data type <attribute-data-types>` used for the evaluated data.


Outputs
=======

Value
   Values, mixed with neighboards defined number of times.


Examples
========

.. figure:: /images/modeling_geometry-nodes_blur_attribute-attribute_example.png

Input is Mesh Plane. First :doc:`/modeling/geometry_nodes/mesh/operations/subdivide_mesh` add some
faces for capture color with :doc:`/modeling/geometry_nodes/utilities/random_value`
used as hue in :doc:`/modeling/geometry_nodes/utilities/color/combine_color` on this.
Now second :doc:`/modeling/geometry_nodes/mesh/operations/subdivide_mesh` split each face on a lot of new.
Each one new duplicate original attribute.
Blur Attribute node mixing all attributes for each faces. Due to this result so smooth.
