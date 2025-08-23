
**************************
Industry Compatible Keymap
**************************

While this is not a comprehensive list,
this page shows common keys used in the industry compatible keymap.


General
=======

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`1` - :kbd:`3`
     - Switch :doc:`Selection mode </modeling/meshes/selecting/introduction>`
   * - :kbd:`4`
     - Object Mode
   * - :kbd:`5`
     - :doc:`Modes </editors/3dview/modes>` Pie Menu
   * - :kbd:`RMB`
     - Context menu
   * - :kbd:`Tab`
     - :ref:`Menu Search <bpy.ops.wm.search_menu>`
   * - :kbd:`Shift-Tab`
     - Quick access (favorites)
   * - :kbd:`Return`
     - Rename
   * - :kbd:`Ctrl-Return`
     - Render
   * - :kbd:`Ctrl-[`
     - Toggle Toolbar
   * - :kbd:`Ctrl-]`
     - Toggle Sidebar


Hovering
========

The following shortcuts can be pressed while hovering the mouse cursor
over an editable field.


.. _keymap-common-properties:

Properties
----------

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Ctrl-C`
     - Copy the (single) value of the field.
   * - :kbd:`Ctrl-V`
     - Paste the (single) value of the field.
   * - :kbd:`Ctrl-Alt-C`
     - Copy the entire vector or color of the field.
   * - :kbd:`Ctrl-Alt-V`
     - Paste the entire vector or color of the field.
   * - :kbd:`RMB`
     - Open the context menu.
   * - :kbd:`Backspace`
     - Reset the value to its default.
   * - :kbd:`Minus`
     - Invert the value's sign (multiply by -1.0).
   * - :kbd:`Ctrl-Wheel`
     - Change the value in incremental steps.

       For fields with a pop-up list of values, this cycles the value.
   * - :kbd:`Return`
     - Activates menus and toggles checkboxes.
   * - :kbd:`Alt`
     - Hold while editing values to apply the change to all selected items
       (objects, bones, sequence-strips).

       This can be used for number fields and toggles.


Dragging
========

The following shortcuts can be used while moving/rotating/scaling an object in the 3D Viewport,
dragging the slider of a value, and so on. Note that they should be pressed after starting
the drag, not before.

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Ctrl`
     - Snap to coarse increments, making it easier to (say) rotate an object by exactly 90°.
   * - :kbd:`Shift`
     - Make the value change more slowly in response to mouse movement, giving you more precision.
   * - :kbd:`Shift-Ctrl`
     - Snap to fine increments.


.. _ui-text-editing:

Text Editing
============

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Home`
     - Go to the start of the line.
   * - :kbd:`End`
     - Go to the end of the line.
   * - :kbd:`Left`, :kbd:`Right`
     - Move the cursor a single character.
   * - :kbd:`Ctrl-Left`, :kbd:`Ctrl-Right`
     - Move the cursor an entire word.
   * - :kbd:`Backspace`, :kbd:`Delete`
     - Delete characters.
   * - :kbd:`Ctrl-Backspace`, :kbd:`Ctrl-Delete`
     - Delete words.
   * - :kbd:`Shift`
     - Select while holding the key and moving the cursor.
   * - :kbd:`Ctrl-A`
     - Select all text.
   * - :kbd:`Ctrl-C`
     - Copy the selected text.
   * - :kbd:`Ctrl-X`
     - Cut the selected text.
   * - :kbd:`Ctrl-V`
     - Paste text at the cursor position.


Common Editing Keys
===================

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Backspace`
     - Delete the selected item with a confirmation dialog
   * - :kbd:`Delete`
     - Delete the selected item without a confirmation dialog
   * - :kbd:`Ctrl-D`
     - Duplicate
   * - :kbd:`P`
     - Set Parent
   * - :kbd:`B`
     - :doc:`/editors/3dview/controls/proportional_editing` (a.k.a. Soft Selection)


Viewport
========

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Alt-LMB`
     - Orbit View
   * - :kbd:`Alt-MMB`
     - Pan View
   * - :kbd:`Alt-RMB`
     - Zoom View
   * - :kbd:`F1` - :kbd:`F4`
     - Front/Side/Top/Camera Viewpoints
   * - :kbd:`F`
     - Frame Selected
   * - :kbd:`Shift F`
     - Center View to Mouse
   * - :kbd:`A`
     - Frame All


Selection
=========

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`LMB`
     - Select
   * - :kbd:`Ctrl-A`
     - Select All
   * - :kbd:`Shift-Ctrl-A`
     - Deselect All
   * - :kbd:`Ctrl-I`
     - Select Inverse
   * - :kbd:`Up`
     - Select More
   * - :kbd:`Down`
     - Select Less
   * - Double :kbd:`LMB`
     - Select Loop
   * - Double :kbd:`Alt-LMB`
     - Select Ring
   * - :kbd:`Ctrl L`
     - Select Linked


Tools
=====

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`W`, :kbd:`E`, :kbd:`R`
     - Move, Rotate, Scale
   * - :kbd:`Q`
     - :doc:`Selection Tools </interface/selecting>`
   * - :kbd:`D`
     - :doc:`Annotate Tool </interface/annotate_tool>`
   * - :kbd:`C`
     - :doc:`Cursor Tool </editors/3dview/3d_cursor>`


Edit Mode Tools
===============

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Ctrl-E`
     - :doc:`Extrude </modeling/meshes/editing/mesh/extrude>`
   * - :kbd:`Ctrl-B`
     - :doc:`Bevel </modeling/meshes/editing/edge/bevel>`
   * - :kbd:`I`
     - :doc:`Inset </modeling/meshes/editing/face/inset_faces>`
   * - :kbd:`K`
     - :doc:`Knife </modeling/meshes/editing/mesh/knife_topology_tool>`
   * - :kbd:`Alt-C`
     - :doc:`Loop Cut </modeling/meshes/editing/edge/loopcut_slide>`


Animation
=========

.. list-table::
   :align: left
   :width: 95%
   :widths: 20 80

   * - :kbd:`Spacebar`
     - Play/Pause
   * - :kbd:`S`
     - Set Location + Rotation + Scale keyframe
   * - :kbd:`Shift-S`
     - Insert Keyframe menu
   * - :kbd:`Shift-W`
     - Set Location Key
   * - :kbd:`Shift-E`
     - Set Rotation Key
   * - :kbd:`Shift-R`
     - Set Scale Key


Platform Specific Keys
======================

macOS
-----

The :kbd:`Cmd` key can be used instead of :kbd:`Ctrl` on macOS
for all but a few exceptions which conflict with the operating system.
