.. index:: Compositor Nodes; Split
.. _bpy.types.CompositorNodeSplit:

**********
Split Node
**********

.. figure:: /images/node-types_CompositorNodeSplit.webp
   :align: right
   :alt: Split Viewer Node.

The *Split* node combines two images for side-by-side display. Typically
used in combination with the :doc:`Viewer Node </compositing/types/output/viewer>`.


Inputs
======

Image
   Shown on the right or top half set by the axis.
Image
   And respectively the left or bottom half.


Properties
==========

Axis
   X or Y used as the split axis.
Factor
   Percentage factor setting the space distribution between the two images.


Outputs
=======

This node has no output sockets.

.. hint::

   This node could be used to plan scene transitions by comparing the end frame of one scene
   with the start frame of another to make sure they align.


Examples
========

.. figure:: /images/compositing_types_color_gamma_example.jpg
   :width: 700px

   Example of a Split Viewer node.
