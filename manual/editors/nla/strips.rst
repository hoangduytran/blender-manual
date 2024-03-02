.. _bpy.types.NlaStrip:

******
Strips
******

There are four kinds of strips: Action, Transition, Sound clip and Meta.


.. _bpy.ops.nla.actionclip_add:

Action Strips
=============

Action Strips are a container of keyframe data of an action.
Any action used by the NLA first must be turned into an Action strip.
This is done so by clicking the :ref:`Push Down Action <bpy.ops.nla.action_pushdown>` button see above.
Alternatively, you can go to :menuselection:`Add --> Action Strip`.

.. note::

   Action Strips only playback the keyframe data that fits into the length of the strip.
   This includes any :doc:`modifiers </editors/graph_editor/fcurves/modifiers>`
   that might extend keyframe data.


.. _bpy.ops.nla.transition_add:

Transition Strips
=================

Transitions interpolate between Actions. They must be placed in between other strips.
Select two or more strips on the same track,
and go to :menuselection:`Add --> Transition`.

.. figure:: /images/editors_nla_strips_basics-transition.png

   Transition Strip.


.. _bpy.ops.nla.soundclip_add:

Sound Clip Strips
=================

Controls when a speaker plays a sound clip.
:menuselection:`Add --> Sound Clip`.


Meta Strips
===========

Meta strips group strips together as a whole, so you can move them as one.
If you find yourself moving a lot of strips together, you can group them into a Meta strip.
A Meta strip can be moved and duplicated like a normal strip.
