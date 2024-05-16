
*************
Action Editor
*************

While the *Dope Sheet* mode lets you work with keyframes of many objects at the same time,
the *Action Editor* mode focuses on the keyframes inside a single :doc:`action </animation/actions>`.

.. figure:: /images/editors_dope-sheet_action-editor.png

   The Action Editor.

An action is a reusable animation segment -- a collection of
:doc:`F-curves </editors/graph_editor/fcurves/introduction>`, where each curve describes how
a certain property changes over time. Objects can reference one action as their *active action*
and additional ones through :doc:`Nonlinear Animation tracks </editors/nla/tracks>`.


Header
======

Previous/Next Layer (down/up arrows)
   Switches to editing the action in the track below/above the current one,
   automatically entering or leaving Tweak Mode as necessary. Also transfers
   the *Disable NLA stack* setting to the *Solo* setting and vice versa
   (see :doc:`NLA tracks </editors/nla/tracks>`).

.. figure:: /images/editors_dope-sheet_action-editor_layers_1.png

   By default, the Action Editor shows the selected object's active action,
   which is stored in the Action Track at the top.

.. figure:: /images/editors_dope-sheet_action-editor_layers_2.png

   After clicking *Previous Layer*, we enter Tweak Mode for the action in the second track.
   The NLA Editor hilights it in green, and the Action Editor lets us edit its keyframes.

Push Down (strips with down arrow icon)
   Creates a new NLA track below the Action Track and moves the active action into it.
   This is the same as clicking :ref:`Push Down Action <bpy.ops.nla.action_pushdown>`
   in the NLA editor.
Stash (snowflake icon)
   Creates a new *muted* NLA track at the bottom and moves the active action into it.
   In effect, this sets the action aside for later use, disabling it so it no longer
   affects the animation. Later, you can choose to either unmute it again or delete it.

   If you click *New Action* in the data-block menu for an object that already has an
   active action, that previous action will be stashed automatically.

.. note::

   Both *Push Down* and *Stash* leave the object without an active action (meaning the Action Editor
   becomes empty and the action can no longer be edited). If you still want to make changes to the
   action, you can select it in the NLA editor and press :kbd:`Tab` to enter Tweak Mode,
   or use the Previous/Next Layer buttons as described above.


.. _dopesheet-action-action:

Action
   A :ref:`data-block menu <ui-data-block>` that lets you change -- or clear --
   the object's active action.
