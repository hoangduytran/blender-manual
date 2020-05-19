
**********
Status Bar
**********

The Status Bar is located at the bottom of the Blender window and displays contextual information such as
keyboard shortcuts, result or warning message and statistic information.
The Status Bar can be hidden by disabling *Show Status Bar* in Window menu or by dragging from the top edge down.

.. figure:: /images/interface_window-system_status-bar_ui.png

   Status Bar.


Keymap Information
==================

The left of the Status Bar displays tool keymaps and mouse button functions.
In editors with a toolbar, pressing :kbd:`Alt` shows the hotkey to change to a desired tool.

.. figure:: /images/interface_window-system_status-bar_ui_left.png
   :align: center


Status Messages
===============

The middle of the Status Bar displays information about in progress operations.

.. figure:: /images/interface_window-system_status-bar_ui_center.png
   :align: center

Running Task
   The currently running task progress is showh when a computation is being performed.
   For example, when rendering or baking,
   hovering the mouse pointer over this region will display time estimate.
   When a cross 'X' is shown, you can cancel the computation by clicking it.
Report Message
   Blender operation results or warnings.
   Click this text label to show the full message in the
   :doc:`Info Editor </editors/info_editor>`.
   Examples are video playback and saving file.


Resource Information
====================

The right of the Status Bar displays information about the Blender instance.

.. figure:: /images/interface_window-system_status-bar_ui_right.png
   :align: center

Collection
   Name of the active :doc:`Collection </scene_layout/collections/index>`.
Active Object
   Name of the active selected object.
Geometry
   Displays information about the current loaded scene depending on the mode and object type
   This can be the number of vertices, faces, triangles (Tris) or bones.
Objects
   Number of objects presented in this format "Objects m/n" reads "m objects are selected from a total of n".
Mem
   Estimated Blender RAM consumption. On a single-instance single-machine scenario,
   this RAM estimate provides a measure against hardware limit of the machine.
Blender version
   The version of Blender that is currently in execution context.
