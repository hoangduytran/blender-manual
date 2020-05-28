
**********
Status Bar
**********

The Status Bar is located at the bottom of the Blender window and displays contextual information such as
keyboard shortcuts, result or warning message and statistical information.
The Status Bar can be hidden by disabling *Show Status Bar* in Window menu or by dragging from the top edge down.

.. figure:: /images/interface_window-system_status-bar_ui.png

   Status Bar.


Keymap Information
==================

The left side of the Status Bar displays mouse button shortcuts and the keymap of the active tool.
In editors with a Toolbar, pressing :kbd:`Alt` shows the hotkeys to change to a desired tool.

.. figure:: /images/interface_window-system_status-bar_ui-left.png
   :align: center


Status Messages
===============

The middle of the Status Bar displays information about in progress operations.

.. figure:: /images/interface_window-system_status-bar_ui-center.png
   :align: center

Running Task
   The progress of the currently running task is show when a computation is being performed
   for example rendering, baking or playback.
   Hovering the mouse pointer over the progress bar will display a time estimate.
   The task can be aborted by clicking the cancel button (``X`` icon).
Report Message
   Blender operation results or warnings, such as after saving a file.
   They disappears after a short time.
   Click this label to show the full message in the :doc:`Info Editor </editors/info_editor>`.


Resource Information
====================

The right side of the Status Bar displays information about the Blender instance.

.. figure:: /images/interface_window-system_status-bar_ui-right.png
   :align: center

Collection
   Name of the active :doc:`Collection </scene_layout/collections/index>`.
Active Object
   Name of the active selected object.
Geometry
   Displays information about the current scene depending on the mode and object type.
   This can be the number of vertices, faces, triangles (Tris) or bones.
Objects
   Number of the selected objects and the total count.
Memory
   The "Mem" label shows an estimate of Blender's RAM consumption.
   In a single-instance single-machine scenario, this estimate provides a measurement against
   the hardware limit of the machine.
Blender version
   The version of Blender that is currently run.
