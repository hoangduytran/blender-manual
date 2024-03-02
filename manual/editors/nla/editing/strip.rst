
*******
Editing
*******

Transform
=========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Transform`

Move
   Move the selected NLA-strips in time or to different NLA-track.
Extend :kbd:`E`
   Extend the selected NLA-strips.
Scale :kbd:`S`
   Scale the selected NLA-strips.


.. _bpy.ops.nla.swap:

Swap
----

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Transform --> Swap`
   :Shortcut:  :kbd:`Alt-F`

Swap the order of the selected NLA-strips in their NLA-track.


.. _bpy.ops.nla.move_up:

Move Up
-------

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Transform --> Move Up`
   :Shortcut:  :kbd:`PageUp`

Move selected NLA-strips up a track if there is room.


.. _bpy.ops.nla.move_down:

Move Down
---------

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Transform --> Move Down`
   :Shortcut:  :kbd:`PageDown`

Move selected NLA-strips down a track if there is room.


.. _bpy.ops.nla.snap:

Snap
====

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Snap`

Selection to Current Frame
   Move the start of selected NLA-strips to the current frame.
Selection to Nearest Frame
   Move the start of the selected NLA-strips to the nearest frame.
Selection to Nearest Second
   Move the start of the selected NLA-strips to the nearest second.
Selection to Nearest Marker
   Move the start of the selected NLA-strips to the nearest marker.


.. _bpy.ops.nla.split:

Split
=====

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Split`
   :Shortcut:  :kbd:`Y`

NLA-Split the selected strips into two NLA-strips. The split happens at the current frame.


.. _bpy.ops.nla.duplicate:

Duplicate
=========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Duplicate`
   :Shortcut:  :kbd:`Alt-D`

Creates a new instance of the selected strips with a copy of the action.


.. _bpy.ops.nla.duplicate_linked_move:

Linked Duplicate
================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Linked Duplicate`
   :Shortcut:  :kbd:`Shift-D`

The contents of one Action strip can be instanced multiple times. To instance another strip,
select a strip, go to :menuselection:`Strip --> Linked Duplicate`.
It will uses the same action as the selected strips.

Now, when any strip is tweaked, the others will change too.
If a strip other than the original is tweaked, the original will turn to red.

.. figure:: /images/editors_nla_editing_linked-strip-edit.png

   Linked duplicated strip being edited.


.. _bpy.ops.nla.delete:

Delete
======

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Delete`
   :Shortcut:  :kbd:`X`

Delete selected NLA-Strips.


.. _bpy.ops.nla.meta_add:

Make Meta
=========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Add --> Make Meta`
   :Shortcut:  :kbd:`Ctrl-G`

Group selected NLA-strips into a meta strip.
A meta strip will group the selected NLA-strips of the same NLA-track.


.. list-table::

   * - .. figure:: /images/editors_nla_strips_meta1.png
          :width: 320px

          Select two or more strips.

     - .. figure:: /images/editors_nla_strips_meta2.png
          :width: 320px

          Combine them into a meta strip.


.. _bpy.ops.nla.meta_remove:

Remove Meta
===========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Remove Meta`
   :Shortcut:  :kbd:`Ctrl-Alt-G`

A Meta strip still contains the underlying strips. You can ungroup a Meta strip.


.. _bpy.ops.nla.mute_toggle:

Toggle Muting
=============

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Toggle Muting`
   :Shortcut:  :kbd:`H`

Mute or unmute the selected NLA-strips. Muted NLA-strips will not influence the animation.


.. _bpy.ops.nla.bake:

Bake Action
===========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Bake Action`

.. reference::

   :Editor:    3D Viewport
   :Mode:      Object and Pose Modes
   :Menu:      :menuselection:`Header --> Object --> Animation --> Bake Action...`

The final motion of objects or bones depends not only on the keyframed animation,
but also on any active F-Curve modifiers, drivers, and constraints.
On each frame of all the scene's frames, the *Bake Action* operator computes
the final animation of the selected objects or bones with all those
modifiers, drivers, and constraints applied, and keyframes the result.

This can be useful for adding deviation to a cyclic action like a :term:`Walk Cycle`,
or to create a keyframe animation created from drivers or constraints.

Start Frame
   Start frame for baking.
End Frame
   End frame for baking.
Frame Step
   Number of frames to skip forward while baking each frame.
Only Selected Bones
   Only key selected bones (Pose baking only).
Visual Keying
   Keyframe from the final transformations (with constraints applied).
Clear Constraints
   Remove all constraints from keyed object/bones, and do 'visual' keying.
Clear Parents
   Bake animation onto the object then clear parents (objects only).
Overwrite Current Action
   Bake animation into current action, instead of creating a new one
   (useful for baking only part of bones in an armature).
Clean Curves
   After baking curves, remove redundant keys.
Bake Data
   Which data's transformations to bake

   :Pose: Bake bones transformations.
   :Object: Bake object transformations.
Channels
   Which channels to bake.

   :Location: Bake location channels.
   :Rotation: Bake rotation channels.
   :Scale: Bake scale channels.
   :B-Bone: Bake B-Bone channels.
   :Custom Properties: Bake custom properties.


.. _bpy.ops.nla.apply_scale:

Apply Scale
===========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Apply Scale`
   :Shortcut:  :kbd:`Ctrl-A`

Apply the scale of the selected NLA-strips to their referenced Actions.


.. _bpy.ops.nla.clear_scale:

Clear Scale
===========

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Clear Scale`
   :Shortcut:  :kbd:`Alt-S`

Reset the scaling of the selected NLA-strips.


.. _bpy.ops.nla.action_sync_length:

Sync Action Length
==================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Sync Action Length`

Synchronize the length of the action to the length used in the NLA-strip.


.. _bpy.ops.nla.make_single_user:

Make Single User
================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Make Single User`
   :Shortcut:  :kbd:`U`

This tool ensures that none of the selected strips use an action which is also used by any other strips.

.. note::

   This does not recursively go inside meta strips.


.. _bpy.ops.nla.tweakmode_enter:

Start Editing Stashed Action
============================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Start Editing Stashed Action`
   :Shortcut:  :kbd:`Shift-Tab`

It will enter and exit Tweak Mode as usual, but will also make sure that the action can be edited in isolation
(by flagging the NLA track that the action strip comes from as being "solo").
This is useful for editing stashed actions, without the rest of the NLA Stack interfering.

When you finished editing the strip, simply go to :menuselection:`Strip --> Stop Editing Stashed Action`
or press :kbd:`Shift-Tab`.

.. list-table::

   * - .. figure:: /images/editors_nla_editing_nla-mode.png
          :width: 320px

          Strip in NLA mode.

     - .. figure:: /images/editors_nla_editing_edit-mode.png
          :width: 320px

          Strip in Tweak mode.


Start Tweaking Strips Actions (Full Stack)
==========================================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Start Tweaking Strips Actions (Full Stack)`
   :Shortcut:  :kbd:`Tab`

Allows you to edit the contents of the strip without disabling all the tracks above the tweaked strip.
This allows keyframing to work as expected, and preserves the pose that you visually keyed.

When you finished editing the strip, simply go to :menuselection:`Strip --> Stop Tweaking Strips Actions`
or press :kbd:`Tab`.

.. note::

   For transitions above the tweaked strip, keyframe remapping will fail
   for channel values that are affected by the transition.
   A work around is to tweak the active strip without evaluating the upper NLA stack.


Start Tweaking Strips Actions (Lower Stack)
===========================================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Strip --> Start Tweaking Strips Actions (Lower Stack)`

The contents of Action strips can be edited, but you must be in *Tweak Mode* to do so.
The keyframes of the action can then be edited in the Dope Sheet.

When you finished editing the strip, simply go to :menuselection:`Strip --> Stop Tweaking Strips Actions`
