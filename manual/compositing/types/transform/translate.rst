.. index:: Compositor Nodes; Translate
.. _bpy.types.CompositorNodeTranslate:

**************
Translate Node
**************

.. figure:: /images/node-types_CompositorNodeTranslate.webp
   :align: right
   :alt: Translate Node.

The Translate node moves an image.

Could also be used to add a 2D camera shake.


Inputs
======

Image
   Standard color input.
X, Y
   Used to move the input image horizontally and vertically.


Properties
==========

Interpolation
   Interpolation Methods.

   :Nearest: No interpolation, uses nearest neighboring pixel.
   :Bilinear: Simple interpolation between adjacent pixels.
   :Bicubic: Highest quality interpolation.

X/Y Extension Mode
   The extension mode applied to the X axis.

   :Clip: Areas outside of the image are filled with transparency.
   :Extend: Areas outside of the image are filled with the closest boundary pixel in the image.
   :Repeat: Areas outside of the image are filled with repetitions of the image.


Outputs
=======

Image
   Standard color output.
