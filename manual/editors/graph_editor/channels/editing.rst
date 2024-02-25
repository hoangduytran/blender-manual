
*******
Editing
*******

.. _bpy.ops.anim.channels_delete:

Delete Channels
===============

.. reference::

   :Menu:      :menuselection:`Channel --> Delete Channels`
   :Shortcut:  :kbd:`X`

Deletes the whole channel from the current action
(i.e. unlink the underlying F-Curve data-block from this action data-block).

.. warning::

   The :kbd:`X` shortcut is area-dependent: if you use it in the left list part,
   it will delete the selected channels, whereas if you use it in the main area,
   it will delete the selected keyframes.


.. _bpy.ops.anim.channels_group:
.. _bpy.ops.anim.channels_ungroup:

Un/Group Channels
=================

.. reference::

   :Menu:      :menuselection:`Channel --> Un/Group Channels`
   :Shortcut:  :kbd:`Ctrl-Alt-G`, :kbd:`Ctrl-G`

Un/Groups the selected channels into a collection that can be renamed by double clicking on the group name.
For example, this helps to group channels that relate a part of an armature to keep the editor more organized.


.. _bpy.ops.anim.channels_setting_toggle:
.. _bpy.ops.anim.channels_setting_enable:
.. _bpy.ops.anim.channels_setting_disable:

Toggle/Enable/Disable Channel Settings
======================================

.. reference::

   :Menu:      :menuselection:`Channel --> Toggle/Enable/Disable Channel Settings`
   :Shortcut:  :kbd:`Shift-W`, :kbd:`Shift-Ctrl-W`, :kbd:`Alt-W`

Enable/disable a channel's setting (selected in the menu that pops up).

Protect, Mute
   Todo.


.. _bpy.ops.anim.channels_editable_toggle:

Toggle Channel Editability
==========================

.. reference::

   :Menu:      :menuselection:`Channel --> Toggle Channel Editability`
   :Shortcut:  :kbd:`Tab`

Locks or unlocks a channel for editing.


.. _editors-graph-fcurves-settings-extrapolation:
.. _bpy.ops.graph.extrapolation_type:

Extrapolation Mode
==================

.. reference::

   :Menu:      :menuselection:`Channel --> Extrapolation Mode`
   :Shortcut:  :kbd:`Shift-E`

Change the extrapolation between selected keyframes.

Extrapolation defines the behavior of a curve before the first and after the last keyframes.

There are two basic extrapolation modes:

:Constant:
   .. figure:: /images/editors_graph-editor_fcurves_introduction_extrapolate1.png
      :align: right
      :width: 300px

      Constant extrapolation.

   The default one, curves before their first keyframe and after their last one have a constant value
   (the one of these first and last keyframes).

:Linear:
   .. figure:: /images/editors_graph-editor_fcurves_introduction_extrapolate2.png
      :align: right
      :width: 300px

      Linear extrapolation.

   Curves ends are straight lines (linear), as defined by the slope of their first and last keyframes.

Additional extrapolation methods (e.g. the *Cycles* modifier)
are located in the :doc:`F-Curve Modifiers </editors/graph_editor/fcurves/modifiers>`.


.. _bpy.ops.graph.fmodifier_add:

Add F-Curve Modifier
====================

.. reference::

   :Menu:      :menuselection:`Channel --> Add F-Curve Modifier`
   :Shortcut:  :kbd:`Shift-Ctrl-M`

Opens a pop-up allowing you to add modifiers to the active F-Curve.
Settings for the :doc:`modifier </editors/graph_editor/fcurves/modifiers>` can be found in
the :menuselection:`Sidebar --> Modifiers` tab.


.. _bpy.ops.graph.hide:
.. _bpy.ops.graph.reveal:

Show/Hide
=========

Hide Selected Curves :kbd:`H`
   Hides the selected curves.
Hide Unselected :kbd:`Shift-H`
   Show only the selected curve (and hide everything else).
Reveal Curves :kbd:`Alt-H`
   Show all previous hidden curves.


.. _bpy.ops.anim.channels_expand:
.. _bpy.ops.anim.channels_collapse:

Expand/Collapse Channels
========================

.. reference::

   :Menu:      :menuselection:`Channel --> Expand/Collapse Channels`
   :Shortcut:  :kbd:`NumpadPlus`, :kbd:`NumpadMinus`

Expands or collapses selected channels.


.. _bpy.ops.anim.channels_move:

Move
====

.. reference::

   :Menu:      :menuselection:`Channel --> Move...`

This allows you to move selected channels up/down :kbd:`PageUp`, :kbd:`PageDown`,
or directly to the top/bottom :kbd:`Shift-PageUp`, :kbd:`Shift-PageDown`.


.. _bpy.ops.anim.channels_fcurves_enable:

Revive Disabled F-Curves
========================

.. reference::

   :Menu:      :menuselection:`Channel --> Revive Disabled F-Curves`

Clears "disabled" tag from all F-Curves to get broken F-Curves working again.


.. _bpy.ops.anim.channels_view_selected:

Frame Selected Channels
=======================

.. reference::

   :Menu:      :menuselection:`Channel --> Frame Selected Channels`
   :Shortcut:  :kbd:`NumpadPeriod`

Reset viewable area to show the selected channels.
To frame the channel that is under the mouse cursor, use :kbd:`Alt-MMB`.

Include Handles
   Include handles of keyframes when calculating extents.
Use Preview Range
   Ignore frames outside of the preview range.


.. _bpy.ops.graph.keys_to_samples:

Keys to Samples
===============

.. reference::

   :Menu:      :menuselection:`Channel --> Keys to Samples`
   :Shortcut:  :kbd:`Alt-C`

This operator replaces an F-Curve with a set of sampled points at each full frame.
**It is a destructive process that removes the ability to edit the curve**.
The main use for this is to reduce the file size with large datasets. Samples are only 1/5th the size per key.
The sampled points interpolate linearly on subframes.


.. _bpy.ops.graph.samples_to_keys:

Samples to Keys
===============

.. reference::

   :Menu:      :menuselection:`Channel --> Samples to Keys`

This operator replaces a sampled F-Curve with keyframes, adding the ability to edit it.
It will not recreate the curve as it was before, instead it will place 1 key at every frame.


.. _bpy.ops.graph.sound_to_samples:

Sound to Samples
================

.. reference::

   :Menu:      :menuselection:`Channel --> Sound to Samples`

The *Sound to Samples* operator takes a sound file and uses its sound wave to create the animation data.
By default this data will not be editable, use *Samples to Keys* to get editable keyframes.

Lowest Frequency
   Cutoff frequency of a high-pass filter that is applied to the audio data.
Highest Frequency
   Cutoff frequency of a low-pass filter that is applied to the audio data.
Attack Time
   Value for the hull curve calculation that tells how fast the hull curve can rise.
   The lower the value the steeper it can rise.
Release Time
   Value for the hull curve calculation that tells how fast the hull curve can fall.
   The lower the value the steeper it can fall.
Threshold
   Minimum amplitude value needed to influence the hull curve.

Accumulate
   Only the positive differences of the hull curve amplitudes are summarized to produce the output.
Additive
   The amplitudes of the hull curve are summarized. If *Accumulate* is enabled,
   both positive and negative differences are accumulated.
Square
   Gives the output as a square curve.
   Negative values always result in -1, and positive ones in 1.

   Square Threshold
      All values lower than this threshold result in 0.


.. _bpy.ops.graph.channels_bake:

Bake Channels
=============

.. reference::

   :Menu:      :menuselection:`Channel --> Bake Channels`

The *Bake Channels* operator creates new keyframes on the F-Curves of channels that are selected in the channel box.

Range
   The range that will be baked. Defaults to the scene range or preview range.
Step
   Distance between keyframes. Can be used to bake on 2s or even bake to subframes.
Remove Existing Keys
   Boolean option that if enabled also removes keys outside the specified baking range.
Interpolation Type
   Choose which interpolation type new keys should have, e.g. Constant or Bezier.
Bake Modifiers
   If true bakes the effect of the modifier stack to keys and deletes the modifier stack.
   If false, modifiers get disabled before baking, so the resulting keys will behave as if the modifiers didn't exist.


.. _bpy.ops.graph.euler_filter:

Discontinuity (Euler) Filter
============================

.. reference::

   :Menu:      :menuselection:`Channel --> Discontinuity (Euler) Filter`

This operator cleans up Euler rotation channels that suffer from :term:`Gimbal Lock`.
The channels of all three axes of euler rotation need to be selected for the operator
to work.
