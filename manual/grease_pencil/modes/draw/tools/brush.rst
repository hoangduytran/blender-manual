
**********
Brush Tool
**********

.. reference::

   :Mode:      Draw Mode
   :Tool:      :menuselection:`Toolbar --> Brush`


Tool to use for any of the Grease Pencil *Draw* mode brushes. Activating a brush from an asset
shelf or brush selector will also activate this tool for convenience.

See :doc:`brushes </grease_pencil/modes/draw/brushes/index>` (or the
:doc:`overview </grease_pencil/modes/draw/brushes/overview>`) for a detailed list of all brushes
and their options.


Tool Settings
=============

Eraser
------

.. _bpy.types.Paint.eraser_brush:

Default Eraser Brush
   Select a brush to use as eraser for quickly alternating with the main brush using
   :kbd:`Ctrl-LMB`.


Usage
=====

Selecting a Brush and Material
------------------------------

In the Tool Settings select the brush, material and color type to use with the tool.
The Draw tool uses *Draw Brush* types.
See :ref:`grease-pencil-draw-common-options` for more information.


Free-hand Drawing
-----------------

Click and hold :kbd:`LMB` or use the pen tip to make free-hand drawing on the viewport.

.. list-table:: Drawing free-hand strokes.

   * - .. figure:: /images/grease-pencil_modes_draw_tools_draw_free-hand-01.png
          :width: 200px

     - .. figure:: /images/grease-pencil_modes_draw_tools_draw_free-hand-02.png
          :width: 200px

     - .. figure:: /images/grease-pencil_modes_draw_tools_draw_free-hand-03.png
          :width: 200px


Stabilize Stroke
----------------

:kbd:`Shift-LMB` toggle the use of :ref:`Stabilize Stroke <bpy.types.BrushGpencilSettings.use_settings_stabilizer>`
on the brush to have more control while drawing and get smoother lines.

.. list-table:: Drawing strokes using *Stabilize Stroke*.

   * - .. figure:: /images/grease-pencil_modes_draw_tools_draw_stabilizer-01.png

     - .. figure:: /images/grease-pencil_modes_draw_tools_draw_stabilizer-02.png

     - .. figure:: /images/grease-pencil_modes_draw_tools_draw_stabilizer-03.png


Straight Lines
--------------

:kbd:`Alt-LMB` Constrains the drawing of the strokes to horizontal or vertical straight lines.


Switching to the Erase Tool
---------------------------

:kbd:`Ctrl-LMB` changes temporally to the active Erase tool.
See :doc:`Erase Tool </grease_pencil/modes/draw/tools/erase>` for more information.

You can also use :kbd:`B` to delete all the points in the selected drawing area.
