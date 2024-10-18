.. index:: Compositor Nodes; Alpha Over
.. _bpy.types.CompositorNodeAlphaOver:

***************
Alpha Over Node
***************

.. figure:: /images/compositing_node-types_CompositorNodeAlphaOver.webp
   :align: right
   :alt: Alpha Over Node.

The *Alpha Over* node is used to layer an image on top of another with alpha blending.


Inputs
======

Factor
   The alpha of the foreground image, going from 0 (fully transparent) to 1 (fully opaque).
Image
   The background image.
Image
   The foreground image.


Properties
==========

Convert Premultiplied
   The *Alpha Over* node expects the foreground image to use :term:`Premultiplied Alpha`.
   If it uses :term:`Straight Alpha` instead, you can enable this checkbox to convert it.

Premultiplied
   Interpolate between :term:`Premultiplied Alpha` and :term:`Straight Alpha`.

   When set to 1, the foreground color values will be multiplied by the alpha;
   this is equivalent to enabling *Convert Premultiplied*.
   When set to 0, the color values do not change.

   If *Premultiplied* is not zero, *Convert Premultiplied* will be ignored.

   .. note:: This is a legacy option.


Outputs
=======

Image
   The blended result.


Examples
========

Overlay
-------

In the node tree below, the :doc:`/compositing/types/color/color_ramp` is used to convert an opaque,
grayscale swirl image to a red one with transparency. Then, the *Alpha Over* node is used to overlay
it on top of another image.

.. figure:: /images/compositing_types_converter_color-ramp_create-alpha-mask.png
   :width: 600px

   Assembling a composite image using Alpha Over.


Fade In
-------

The example below uses the :doc:`/compositing/types/input/scene/time_curve` to gradually increase the
*Alpha Over* node's *Factor* from 0 to 1 over the course of 30 frames. This will result in the text
fading in on top of the background image.

.. figure:: /images/compositing_types_color_alpha-over_example.png
   :width: 600px

   Animated fade in effect using Alpha Over.
