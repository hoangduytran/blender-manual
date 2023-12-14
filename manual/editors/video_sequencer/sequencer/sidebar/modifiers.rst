.. index:: Modifiers; Video Sequencer Modifiers
.. index:: Video Sequencer Modifiers

.. _bpy.types.SequenceModifier:

*********
Modifiers
*********

.. reference::

   :Panel:     :menuselection:`Sidebar region --> Modifiers --> Modifiers`

.. figure:: /images/video-editing_sequencer_sidebar_modifiers_panel.png
   :align: right

Modifiers are used to make adjustments on the image, like contrast,
brightness, saturation, color balance and applying masks.

You can add these modifiers directly to the selected strip,
or you can use it within an "Adjustment Layer" effect strip,
which allows you to apply these modifiers onto several strips the same time.

Use Linear Modifiers
   Calculates modifiers in :ref:`linear color space` instead of the
   :ref:`Sequencer color space <bpy.types.ColorManagedSequencerColorspaceSettings.name>`.

   Calculating modifiers in linear space will match the image processing of the compositor.
   In most cases this should be enabled, working in a non-linear workflow could have unpredictable results.
Copy to Selected Strips
   Allows you to copy the modifiers to selected strips.
   This works two ways, you can either replace the old modifiers or append/add to the previous modifiers.


Common Options
==============

Each modifier has several buttons at its top:

Mute (eye icon)
   Disables the modifier. Very useful to compare the image, with / without modifications.
Move (up/down arrow icon)
   The next two buttons are used to change the modifier's position in the stack.
Remove ``X``
   The cross is to delete the modifier from the stack.


Masking
-------

Use it for masking the other modifiers in the stack which are below.

For example, to correct the brightness only on a certain zone of the image,
you can filter the Brightness/Contrast modifier by placing a Mask modifier,
just before it in the stack. You can choose to use a Mask created in the Mask editor,
or to use another strip as a mask (the image of this strip must have an alpha channel).
This mask will be applied on all the others modifiers below it in the stack.

Mask Input Type
   Type of input data used for mask.

   :Strip:
      Uses the grayscale representation of the image in a strip to affect the alpha of the current strip.
   :Mask:
      Use a mask data-block to affect the alpha of the current strip.

Mask
   The Strip or Mask data-block to use as an input.

Mask Time :guilabel:`Mask Input Only`
   How the start frame of the mask is calculated.

   :Relative: Mask animation is offset to the start of the strip.
   :Absolute: Mask animation is in sync with scene frame.


Types
=====

Currently, the following modifiers are supported:


.. index:: Video Sequencer Modifiers; Brightness/Contrast Modifier
.. _bpy.types.BrightContrastModifier:

Brightness/Contrast Modifier
----------------------------

Adjusts the brightness and contrast of the modifier input.


.. index:: Video Sequencer Modifiers; Color Balance Modifier
.. _bpy.types.ColorBalanceModifier:

Color Balance Modifier
----------------------

Color balance adjustments, either by the Lift, Gamma, and Gain or the Slope, Offset and Power method.

This modifier works similar to the :doc:`Color Balance Node </compositing/types/color/adjust/color_balance>`.

.. figure:: /images/video-editing_sequencer_sidebar_color-balance-modifier.png
   :align: right

Depending on the selected method, the following operations can be applied to the color values in the
sequencer color space:

Lift/Gamma/Gain
   Lift
      Increases the value of dark colors.
   Gamma
      Adjusts midtones.
   Gain
      Adjusts highlights.

Offset/Power/Slope (ASC-CDL)
   The following formula is applied to each RGB color value separately: :math:`c_{out} =  (c_{in}*s + o)^p`

   Slope
      The multiplier :math:`s` influences all color values except black. Its effect is stronger
      the brighter the source color is.
   Offset
      Shifts color values after applying Slope by adding the Offset :math:`o` to them. Note that
      the selected value shown in the UI will be subtracted by 1, so the default value of 1 means
      effectively no offset is applied.
   Power
      Over-all exponent :math:`p`, which mainly adjusts the midtones.


.. index:: Video Sequencer Modifiers; Curves Modifier
.. _bpy.types.CurvesModifier:

Curves Modifier
---------------

Color and RGB curves.

This modifier works the same as the :doc:`Curves Node </compositing/types/color/adjust/rgb_curves>`.


.. index:: Video Sequencer Modifiers; Hue Correct Modifier
.. _bpy.types.HueCorrectModifier:

Hue Correct Modifier
--------------------

HSV multi points curves.

This modifier works the same as the :doc:`Curves Node </compositing/types/color/adjust/hue_correct>`.


.. index:: Video Sequencer Modifiers; Mask Modifier

Mask Modifier
-------------

The mask modifier is used to affect the :term:`Alpha Channel` of the current strip.

For example, to correct the brightness only on a certain zone of the image,
you can filter the Brightness/Contrast modifier by placing a Mask modifier,
just before it in the stack. You can choose to use a Mask created in the Mask editor,
or to use another strip as a mask (the image of this strip must have an alpha channel).
This mask will be applied on all the others modifiers below it in the stack.

.. _bpy.types.SequenceModifier.input_mask_type:

Mask Input Type
   Type of input data used for mask.

   :Strip:
      Uses the grayscale representation of the image in a strip to affect the alpha of the current strip.
   :Mask:
      Use a mask data-block to affect the alpha of the current strip.

.. _bpy.types.SequenceModifier.input_mask_id:
.. _bpy.types.SequenceModifier.input_mask_strip:

Mask
   The Strip or Mask data-block to use as an input.

.. _bpy.types.SequenceModifier.mask_time:

Mask Time :guilabel:`Mask Input Only`
   How the start frame of the mask is calculated.

   :Relative: Mask animation is offset to the start of the strip.
   :Absolute: Mask animation is in sync with scene frame.


.. index:: Video Sequencer Modifiers; Tone Map Modifier

Tone Map Modifier
-----------------

Used to map one set of colors to another in order to approximate the appearance
of high dynamic range images in a medium that has a more limited dynamic range.

This modifier works the same as the :doc:`Tone Map Node </compositing/types/color/adjust/tone_map>`.


.. index:: Video Sequencer Modifiers; White Balance Modifier
.. _bpy.types.WhiteBalanceModifier:

White Balance Modifier
----------------------

Use it to adjust the white balance by choosing the color that should be white.


.. index:: Video Sequencer Modifiers; Sound Equalizer Modifier
.. _bpy.types.SoundEqualizerModifier:

Sound Equalizer Modifier
------------------------

This modifier can be used to emphasize or suppress sound frequencies.
The range is limited to 35Hz - 20kHz and +/-35dB
