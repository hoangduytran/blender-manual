.. index:: Editors; NLA Editor

************
Introduction
************

The NLA editor, short for NonLinear Animation, can manipulate and repurpose :doc:`/animation/actions`,
without the tedium of handling keyframes. It is often used to make broad,
significant changes to a scene's animation, with relative ease.
It can also repurpose, chain together a sequence of motions, and "layered" actions, which make it easier to organize,
and version-control your animation.


Header
======

View Menu
---------

Adjust Last Operation
   Displays a pop-up panel to alter properties of the last
   completed operation. See :ref:`bpy.ops.screen.redo_last`.
Realtime Updates
   When transforming NLA-strips, the changes to the animation are propagated to other views.
Show Control F-Curves
   Overlays a graph of the NLA-strip's influence on top of the strip.
Show Markers
   Shows the markers region. When disabled, the `Markers Menu`_ is also hidden
   and markers operators are not available in this editor.
Show Local Markers
   Shows action-local markers on the strip, this is useful when synchronizing time across strips.

   .. figure:: /images/editors_nla_tracks_local_markers.png

      Local markers shown on a strip.

Set Preview Range :kbd:`P`
   Selecting a preview range by dragging in the NLA Editor.
Clear Preview Range :kbd:`Alt-P`
   Unset the preview range
Auto Select Preview Range :kbd:`Ctrl-Alt-P`
   Automatically select the preview range based on the range of keyframes.

.. seealso:: See Timeline's :ref:`timeline-view-menu`.


Select Menu
-----------

All :kbd:`A`
   Select all NLA-strips.
None :kbd:`Alt-A`
   Deselect all NLA-strips.
Invert :kbd:`Ctrl-I`
   Invert the current selection of NLA-strips.
Box Select :kbd:`B`
   Select NLA-strips by drawing a box. All NLA-strips that intersects the box
   will be added to the current selection.
Border Axis Range :kbd:`Alt-B`
   Select NLA-strips by drawing a box. All NLA-strips that intersects the frames
   of the drawn box will be added to the current selection.
Before Current Frame :kbd:`[`
   Select all NLA-strips before the current frame.
After Current Frame :kbd:`]`
   Select all NLA-strips after the current frame.


Markers Menu
------------

:doc:`Markers </animation/markers>` are used to denote frames with key points or significant events
within an animation. Like with most animation editors, markers are shown at the bottom of the editor.

.. figure:: /images/editors_graph-editor_introduction_markers.png

   Markers in animation editor.

For descriptions of the different marker tools, see :ref:`Editing Markers <animation-markers-editing>`.


Edit Menu
---------

Contains tools for working with NLA strips.
For descriptions of the different editing tools, see :doc:`Editing Strips </editors/nla/editing>`.


Add
---

Add Action Strip :kbd:`Shift-A`
   Add an NLA-strip referencing an Action to the active track.
Add Transition :kbd:`Shift-T`
   Add an NLA-strip to create a transition between a selection of two adjacent NLA-strips.
Add Sound Strip :kbd:`Shift-K`
   Add an NLA-strip controlling when the speaker object plays its sound clip.

Add Meta-Strip :kbd:`Ctrl-G`
   Group selected NLA-strips into a meta strip.
   A meta strip will group the selected NLA-strips of the same NLA-track.
Remove Meta-Strip :kbd:`Ctrl-Alt-G`
   Ungroup selected Meta strips.

.. _bpy.ops.nla.tracks_add:

Add Tracks
   Add a new NLA-Track on top of the selected object.
Add Track Above Selected
   Add a new NLA-Track just above the selected NLA-track.

.. _bpy.ops.nla.selected_objects_add:

Include Selected Objects
   Let the selected objects appear in the NLA Editor. This is done by adding
   an empty animation data object to the selected object.


Transform Controls
------------------

Snap
   Activates automatic snapping when you moving keys.

   Snap To
      Type of element to snap to.

      :Frame: Snap to frame.
      :Second: Snap to seconds.
      :Nearest Marker: Snap to nearest :doc:`Marker </animation/markers>`.

   Absolute Time Snap
      Absolute time alignment when transforming keyframes
