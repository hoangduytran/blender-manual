.. index:: Compositor Nodes; Tone Map
.. _bpy.types.CompositorNodeTonemap:

*************
Tone Map Node
*************

.. figure:: /images/node-types_CompositorNodeTonemap.webp
   :align: right
   :alt: Tone Map Node.

Tone mapping is used to map high dynamic range colors into a more limited dynamic
range supported by the display, while preserving the appearance as much as possible.

This is a legacy node. It is recommended to use view transforms in the
color management settings instead, and output linear high dynamic range images
from the compositor instead of low dynamic range.


Inputs
======

Image
   :abbr:`HDR (High Dynamic Range)` image.


Properties
==========

Type
   Rh Simple
      Key
         The value the average luminance is mapped to.
      Offset
         Normally always 1, but can be used as an extra control to alter the brightness curve.
      Gamma
         If not used, set to 1.

   R/D Photoreceptor
      Intensity
         If less than zero, darkens image; otherwise, makes it brighter.
      Contrast
         Set to 0 to use estimate from input image.
      Adaptation
         If 0, global; if 1, based on pixel intensity.
      Color Correction
         If 0, same for all channels; if 1, each independent.


Outputs
=======

Image
   :abbr:`LDR (Low Dynamic Range)` image.
