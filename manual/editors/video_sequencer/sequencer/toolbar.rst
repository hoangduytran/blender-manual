
###########
  Toolbar
###########

Selection tools
   :ref:`Tweak <tool-select-tweak>`
      Select or move.
   :ref:`Select Box <tool-select-box>`
      Select strips by dragging a box.
      All strips that intersect the box will be selected.
   :ref:`Select Circle <tool-select-circle>`
      Select strips by dragging a circle. All strips that intersect the path of
      the circle will be selected.
   :ref:`Select Lasso <tool-select-lasso>`
      Select strips by drawing a lasso.

.. _tool-blade:

Blade
   Cuts a strip in two. Specifically, it first shortens the strip so it only shows the content
   up to the cut point, then adds a second strip that shows the content after the cut point.

   Splitting be done in two different ways:

   - Select the tool in the Toolbar and click a strip at the time point where you want to split it.
   - Alternatively, select one or more strips, place the Playhead at the time point where you want to
     split them, and press one of the keyboard shortcuts below.

   You can choose between the following split types:

   Soft :kbd:`K`
      After splitting, it's still possible to restore the cut content in the new strips
      by dragging their handles.

   Hard :kbd:`Shift-K`
      After splitting, it's not possible to restore the cut content by dragging handles.
      However, you can still restore it by changing the :ref:`Hold Offset <sequencer-duration-hard>`
      in the Sidebar.

.. _tool-slip:

Slip
   Moves only the content of the strip. By default, the tool only allows the content to be moved within
   strip handles. If this limit applies, the strip outline is drawn in red color. By pressing :kbd:`C`
   the limiting is toggled on or off.
