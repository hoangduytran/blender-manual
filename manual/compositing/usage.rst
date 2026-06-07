
********************
Using The Compositor
********************

The compositor can be used directly inside the Video Sequencer through
compositor strips and compositor-based modifiers.

This allows node-based image processing and effects to be integrated into
editing workflows without leaving the Sequencer.

Video Sequence Strips & Modifiers
=================================

Compositor functionality can be used in the Sequencer in two ways:

- :ref:`Compositor Strips <bpy.types.CompositorStrip>` process one or more
  strips through a compositor node group and output the result as a strip.
- :ref:`Compositor Modifiers <bpy.types.SequencerCompositorModifierData>` apply compositor
  node groups as modifiers to existing strips.

Both workflows use compositor node groups and support many of the same
compositor nodes and operations available in the regular Compositor editor.


Compositor Strips
-----------------

Compositor strips create effects directly in the Sequencer timeline.

They can be used for transitions, stylized effects, color processing,
image manipulation, blurs, distortions, overlays, and custom workflows.

Depending on the strip type, compositor strips can process:

- A single strip.
- Two input strips for transitions and blend effects.
- No inputs for fully procedural effects.


Compositor Modifiers
--------------------

Compositor modifiers apply a compositor node group directly to an existing strip.

Unlike compositor strips, modifiers do not create a separate strip in the timeline.
Instead, the effect is evaluated as part of the strip itself.

This is useful for reusable effects such as:

- Color correction.
- Glows and blurs.
- Stylization effects.
- Distortion and warping.
- Overlays and masks.


Node Groups
-----------

Both compositor strips and modifiers use compositor node groups.

The available inputs depend on the compositor strip or modifier type.

.. note::

   - The first node group output socket must use the ``Color`` type.
   - Some strip types automatically provide image inputs to matching sockets.
   - If a compositor strip does not contain a ``Float`` input socket,
     the strip Fade control has no effect.
