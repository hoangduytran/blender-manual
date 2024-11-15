.. _bpy.types.TransformSequence:

***************
Transform Strip
***************

Transform is a Swiss Army knife of image manipulation.
It moves, rotates, and scales the images within a strip.


Options
=======

.. _bpy.types.TransformSequence.interpolation:

Interpolation
   :None: No interpolation, uses nearest neighboring pixel.
   :Bilinear: Simple interpolation between adjacent pixels.
   :Bicubic: Highest quality interpolation.

.. _bpy.types.TransformSequence.translation_unit:

Translation Unit
   Control whether the input values are in *Percent* or *Pixels*.

.. _bpy.types.TransformSequence.translate_start:

Position
   Moves the input along the X and Y axis.

.. _bpy.types.TransformSequence.use_uniform_scale:

Uniform Scale
   Scale the input evenly along the X and Y axis.

.. _bpy.types.TransformSequence.scale_start:

Scale
   Scale the image on the X and Y axis.

.. _bpy.types.TransformSequence.rotation_start:

Rotation
   Rotates the input two-dimensionally along the Z axis.


Example
=======

.. figure:: /images/video-editing_sequencer_strips_effects_transform_example.png

   Transform Effect.
