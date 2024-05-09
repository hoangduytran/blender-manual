
*************
Action Editor
*************

While the *Dope Sheet* mode lets you work with keyframes of many objects at the same time,
the *Action Editor* focuses on the keyframes inside a single :doc:`action </animation/actions>`.

.. figure:: /images/editors_dope-sheet_action-editor.png

   The Action Editor.

Put simply, an "action" is a collection of :doc:`F-curves </editors/graph_editor/fcurves/introduction>`,
where each curve describes how a certain property changes over time. An example action
could say that "the X coordinate goes from 0m on frame 1 to 5m on frame 20, and the Z rotation
goes from 0° on frame 5, to 90° on frame 50, and to 45° on frame 100."

Note that an action by itself doesn't refer to any particular object. In the example above,
it only says that "the X coordinate changes" without mentioning which object that applies to.
The same thing goes for armature bones like in the screenshot above: the action contains an
"X Location" curve for a "hair.R" bone, but it doesn't say which armature that bone belongs to.

Instead, an object references the action, opting to have the action's curves affect it.
Multiple objects can reference the same single action.

What's more, a single object can reference multiple actions;
specifically, it can reference a single "active" action and contain a stack of
:doc:`Nonlinear Animation tracks </editors/nla/tracks>`, where each track in turn
references further actions. The active action and the tracks can be seen in the NLA editor
as well as the *Animation* node in the :doc:`Outliner </editors/outliner/introduction>`.


Header
======

Previous/Next Layer (down/up arrows)
   Switches between the object's active action and its topmost NLA track, as well as between NLA tracks.

   Normally you can only edit the keyframes in the object's active action. If you want to edit
   an action that's stored in an NLA track, you'd have to select it in the NLA editor and enter the
   so-called "Tweak Mode" by pressing :kbd:`Tab`. These *Previous/Next Layer* buttons
   offer an alternative:

   - If you click *Previous Layer* while not in Tweak Mode (= editing the active action),
     you'll enter Tweak Mode for the action nearest to the Playhead in the topmost track.
   - If you click *Next Layer* while in Tweak Mode on the topmost track,
     you'll leave Tweak Mode and go back to editing the active action.
   - In other cases, you'll leave Tweak Mode for the current track,
     switch to the track below/above it, and enter Tweak Mode there.

   These buttons also transfer the "Solo" status in the NLA editor. This status lets you focus on a subset
   of the actions: unchecking the checkbox next to the object disables all its NLA tracks (leaving only its
   active action enabled), while checking the star next to a track disables all other tracks and the active action
   (leaving only the starred track enabled).

.. figure:: /images/editors_dope-sheet_action-editor_layers_1.png

   By default, the Action Editor shows the selected object's active action.

.. figure:: /images/editors_dope-sheet_action-editor_layers_2.png

   After clicking *Previous Layer*, we enter Tweak Mode for the action in the topmost NLA track.
   The NLA Editor hilights it in green, and the Action Editor lets us edit its keyframes.

Push Down (strips with down arrow icon)
   Creates a new NLA track at the top and moves the active action into it.
   This is the same as clicking *Push Down Action* next to the active action in the NLA editor.
Stash (snowflake icon)
   Creates a new *muted* NLA track at the bottom and moves the active action into it.
   In effect, this sets the action aside for later use, disabling it so it no longer
   affects the animation.

.. note::

   Both *Push Down* and *Stash* leave the object without an active action (meaning the Action Editor
   becomes empty and the action can no longer be edited). If you still want to make changes to the
   action, you need to enter Tweak Mode as described above.


.. _dopesheet-action-action:

Action
   A :ref:`data-block menu <ui-data-block>` that lets you change -- or clear --
   the object's active action.
