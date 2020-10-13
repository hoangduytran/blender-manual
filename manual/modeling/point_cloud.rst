:orphan:

.. _bpy.ops.object.pointcloud:

***********
Point Cloud
***********

Point Clouds are a special object type that is a container for data points in 3D Space.
Each data point can have a set of `Attributes`_ but must at least have
a `position` attribute to store the X, Y and Z coordinates of each point.
Point Clouds can be used to represent photoscans and in the future can represent particles.

.. figure:: /images/modeling_point-cloud_example.png

   Example of a monkey object represented as a point cloud.


Properties
==========

Attributes
----------

Todo.


Custom Properties
-----------------

See the :ref:`Custom Properties <files-data_blocks-custom-properties>` page for more information.


Editing
=======

Currently, not much can be done with Point Clouds; however,
they can be :doc:`converted to/from meshes </scene_layout/object/editing/convert>`.
