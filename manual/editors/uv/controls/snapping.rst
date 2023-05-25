
********
Snapping
********

Snapping lets you easily align UV elements to others.
It can be toggled by clicking the magnet icon in the UV Editor's header,
or more temporarily by holding :kbd:`Ctrl`.

This page is about the Snap header button; for the Snap menu,
see :ref:`UV Editing <bpy.ops.uv.snap_selected>`.

.. _bpy.types.ToolSettings.snap_uv_element:

Snap To
=======

.. reference::

   :Header:    :menuselection:`Snapping --> Snap To`
   :Shortcut:  :kbd:`Shift-Ctrl-Tab`

Increment
   Snaps to grid points.

   .. note::

      By default, this option won't snap to the grid that's displayed in the editor,
      but an imaginary grid with the same resolution that starts at the selection's
      original location. In other words, it lets you move the selection in "increments" of the
      grid cell size.

      If you want to snap to the viewport grid instead, you can enable *Absolute Grid Snap*
      (see below).

Vertex
   Snaps to the vertex that's closest to the mouse cursor.


Additional Options
==================

.. _bpy.types.ToolSettings.use_snap_uv_grid_absolute:

Absolute Grid Snap :guilabel:`Increment`
   Snaps to the grid, instead of snapping in increments relative to the current location.

Target :guilabel:`Vertex`
   See :ref:`3D Viewport Snapping <bpy.types.ToolSettings.snap_target>` for more information.


Affect
======

Specifies which transformations are affected by snapping.
By default, snapping only happens while moving something,
but you can also enable it for rotating and scaling.
