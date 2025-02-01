.. index:: Compositor Nodes; Invert Color
.. _bpy.types.CompositorNodeInvert:
.. Editor's Note: This page gets copied into:
.. - :doc:`</render/shader_nodes/color/invert_color>`
.. - :doc:`</editors/texture_node/types/color/invert_color>`

.. --- copy below this line ---

*****************
Invert Color Node
*****************

.. figure:: /images/node-types_CompositorNodeInvert.webp
   :align: right
   :alt: Invert Color Node.

Inverts the colors in the input image, producing a negative.


Inputs
======

Factor
   The amount of influence the node exerts on the image.
Color
   Standard color input.


Properties
==========

In the compositing context, this node has the following properties:

RGB
   Invert the color channels.
Alpha
   Invert the alpha channel.


Outputs
=======

Color
   Standard color output.


Example
=======

.. figure:: /images/compositing_types_input_mask_example.png

   The Invert node is used to invert the mask.
