
************
Introduction
************

.. _editors-graph_editor-channels_region:

Channels Region
===============

.. figure:: /images/editors_graph-editor_channels_region.png

   The Channels region.

The channels region is used to select and manage the curves for all Animation Editors.
This part shows the objects and their animation data hierarchy each as headers.
Each level can be expanded/collapsed by the small arrow to the left of its header.

- Scenes, Objects (dark blue)
- :doc:`Actions </animation/actions>`, :doc:`Shape keys </animation/shape_keys/index>`, etc. (light blue)
- Channel Groups (green)
- Channels (gray)

.. _bpy.types.DopeSheet.use_filter_invert:
.. _bpy.types.DopeSheet.filter_text:

Name Filter :kbd:`Ctrl-F`
   Only display channels that match the search text.
   Pressing the invert button displays all channels except the channels that match the search text.


Controls
--------

On the headers, there are toggles to control channel's setting:

Pin (pin icon)
   Make the channel always visible regardless of the current selection.
Hide (eye icon)
   Hides the channel(s)/curve (Graph editor only).
Modifiers (wrench icon)
   Deactivates the F-Curve modifiers of the selected curve or all curves in the channel.
Mute (checkbox)
   Deactivates the channel/curve.
Lock :kbd:`Tab` (padlock icon)
   Toggle channel/curve from being editable.
   Selected channels can be locked by pressing :kbd:`Tab`.

   .. note::

      This also works in the Nonlinear Animation Editor, but note that it
      does not prevent edition of the underlying F-Curve, only the NLA strips of
      the NLA track.


Selection
---------

- Select header: :kbd:`LMB`
- Add/Remove from selection: :kbd:`Ctrl-LMB`
- Select Range: :kbd:`Shift-LMB`
- Select All: :kbd:`A`
- Deselect All: :kbd:`Alt-A` or double :kbd:`A`
- Box Select: (:kbd:`LMB` drag) or :kbd:`B` (:kbd:`LMB` drag)
- Box Deselect: (:kbd:`Ctrl-LMB` drag) or :kbd:`B` (:kbd:`Shift-LMB` drag)
- Select all keyframes in the Channel: double :kbd:`LMB` on a Channel Header.


Editing
-------

- Rename (Anything but a Channel): double :kbd:`LMB`
- Delete selected: :kbd:`X` or :kbd:`Delete`
- Lock selected: :kbd:`Tab`
- Enable Channel Setting: :kbd:`Shift-Ctrl-W`
- Disable Channel Setting: :kbd:`Alt-W`
- Toggle Channel Setting: :kbd:`Shift-W`


Sliders
^^^^^^^

.. figure:: /images/editors_dope-sheet_introduction_action-editor-sliders.png

   The Action editor showing sliders.

On channel headers, you can have another column with number fields or sliders,
allowing you to change the value on the current keyframes, or to add new keyframes.
See :ref:`graph-view-menu` for how to show these sliders.
