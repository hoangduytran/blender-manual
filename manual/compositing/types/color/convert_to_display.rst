.. index:: Compositor Nodes; Convert to Display
.. _bpy.types.CompositorNodeConvertToDisplay:

***********************
Convert to Display Node
***********************

.. figure:: /images/node-types_CompositorNodeConvertToDisplay.webp
   :align: right
   :alt: Convert to Display Node

The *Convert to Display* node applies an :doc:`OpenColorIO </render/color_management/opencolorio>`
:doc:`display, view, and look transform </render/color_management/displays_views>`
to an image in the *scene linear* color space.
It converts linear render data into a color-accurate representation for a specific display and view
combination, following the configuration defined in the active color management settings.

This node complements the :doc:`Convert Colorspace </compositing/types/color/convert_colorspace>` node
by supporting display-view-look combinations, which are not represented as individual color spaces
in modern OCIO configurations.
Unlike *Convert Colorspace*, this node reproduces the same color management transforms used by
the *Save As Render* option or the *Render View* display.

.. note::

   This node does not provide controls for exposure, gamma, or white point.
   These adjustments can be performed using dedicated compositor nodes:

   - :doc:`Exposure </compositing/types/color/adjust/exposure>`
   - :doc:`Gamma </compositing/types/color/adjust/gamma>`
   - :doc:`RGB Curves </compositing/types/color/adjust/rgb_curves>`


Inputs
======

Image
   The input image in *scene linear* color space to be converted.
Invert
   Converts from display space back to *scene linear*.
   Not all view transforms can be inverted exactly, so the result may differ from the original image.


Properties
==========

Display
   The target display device as defined in the current OCIO configuration.
   See :ref:`Display <bpy.types.ColorManagedDisplaySettings.display_device>` for an explanation of all options.
View
   The view transform to apply for the selected display.
   See :ref:`View <bpy.types.ColorManagedViewSettings.view_transform>` for an explanation of all options.
Look
   The look transform to apply.
   Optional, and may be *None* depending on the configuration.
   See :ref:`Look <bpy.types.ColorManagedViewSettings.look>` for an explanation of all options.



Outputs
=======

Image
   The color-converted image, suitable for display according to the chosen display, view, and look.
