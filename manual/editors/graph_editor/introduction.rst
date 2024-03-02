.. index:: Editors; Graph Editor

************
Introduction
************

The Graph Editor allows users to adjust animation curves over time for any animatable property.
:doc:`F-Curves </editors/graph_editor/fcurves/introduction>`.

.. figure:: /images/editors_graph-editor_introduction_example.png

   The Graph Editor.


Main Region
===========

The curve view allows you to view and edit F-Curves.
An F-Curve has several key parts:

Curve
   The curve defines the value (Y axis) of the property over time (X axis).

   See :doc:`F-Curves </editors/graph_editor/fcurves/index>`.
Keyframes
   Keyframes are user-defined values on certain frames and are represented
   by little black squares which become orange if selected.

   See :doc:`Keyframes </animation/keyframes/index>` for more information.
Handles
   Each keyframe has a handle that helps determine the values of the curve between keyframes.
   These handles are represented by extruding lines with circular ends
   and can be selected and modified to change the shape of the curve.

   See :ref:`F-Curve Handles <editors-graph-fcurves-settings-handles>` for more information.

.. figure:: /images/editors_graph-editor_introduction_f-curve-example.png

   A simple curve.

.. seealso::

   See :doc:`F-Curves </editors/graph_editor/fcurves/introduction>` for more info.


Navigation
----------

As with most editors, you can:

Pan
   Pan the view vertically (values) or horizontally (time) with click and drag :kbd:`MMB`.
Zoom
   Zoom in and out with the mouse wheel :kbd:`Wheel`.
Scale View
   Scale the view vertically or horizontally :kbd:`Ctrl-MMB`.

In addition, you can also use the scrollbars to pan and zoom the view.

.. tip::

   You can frame an F-Curve channel from any animated property by right clicking on it and choosing `View in Graph
   Editor`. In order to bind that function to a hotkey, you need to make a hotkey manually in the e.g. User Interface
   category. Using the right click menu won't work as it would be in the wrong category.
   The operator name is `anim.view_curve_in_graph_editor`.


.. _graph_editor-2d-cursor:
.. _bpy.types.SpaceGraphEditor.cursor:

Playhead & 2D Cursor
--------------------

.. figure:: /images/editors_graph-editor_introduction_2dcursor.png
   :align: right

   Graph Editor 2D Cursor.

The current frame is represented by a blue vertical line called the *Playhead*.

As in the :doc:`Timeline </editors/timeline>`,
you can change the current frame by :kbd:`LMB`-dragging in the scrubbing area at the top of the editor.

The blue horizontal line is called the *2D Cursor*.
This can be enabled or disabled via the *View Menu* or the *View Properties* panel.

These two lines can be used as a reference for moving and scaling keyframe handles.

.. seealso:: See Graph Editor's :ref:`graph_editor-view-properties`.


View Axes
---------

For *Actions* the X axis represents time,
the Y axis represents the value to set the property.

Depending on the selected curves, the values have different meaning:
for example rotation properties are shown in degrees.


Header
======

.. _graph-view-menu:

View Menu
---------

Sidebar :kbd:`N`
   Show or hide the :ref:`Sidebar Region <ui-region-sidebar>`.
Adjust Last Operation
   Displays a pop-up panel to alter properties of the last
   completed operation. See :ref:`bpy.ops.screen.redo_last`.
Channels
   Show or hide the :ref:`Channels Region <editors-graph_editor-channels_region>`.

----------

Frame Selected :kbd:`NumpadPeriod`
   Reset viewable area to show selected keyframes.
Frame All :kbd:`Home`
   Reset viewable area to show all keyframes.
Go to Current Frame :kbd:`Numpad0`
   Centers the area to the Playhead.

----------

Realtime Updates
   When transforming keyframes, changes to the animation data are propagated to other views.
Show Sliders
   A toggle option that shows the value sliders for the channels.
   See the Fig. :ref:`fig-dope-sheet-action`.
Auto-Merge Keyframes
   Automatically merge nearby keyframes.

.. _bpy.types.SpaceGraphEditor.use_auto_lock_translation_axis:

Auto-Lock Key Axis
   Automatically locks the movement of keyframes to the dominant axis.

----------

Show Markers
   Shows the markers region. When disabled, the `Markers Menu`_ is also hidden
   and markers operators are not available in this editor.
Show Cursor
   Toggles the visibility of the `Playhead & 2D Cursor`_.
Show Seconds :kbd:`Ctrl-T`
   Show timing in seconds not frames.
Sync Visible Range
   It synchronizes the horizontal panning and scale of the current editor
   with the other editors (Graph, Dope Sheet, NLA, and Sequencer) when this option is set.
   That way you always have these editors showing the same section of frames.

----------

.. _bpy.types.SpaceGraphEditor.show_extrapolation:

Show Extrapolation
   Toggles the visibility of the :ref:`extrapolated <editors-graph-fcurves-settings-extrapolation>`
   portion of curves.
Show Handles :kbd:`Ctrl-H`
   Toggles the display of a curve's handles in the curve view.
Only Selected Keyframes Handles
   Only shows the handles for the currently selected curves.

----------

.. _graph-preview-range:

Set Preview Range :kbd:`P`
   Interactively define frame range used for playback.
   Allows you to define a temporary preview range to use for animation playback
   (this is the same thing as the *Playback Range* option of
   the :ref:`Timeline editor header <animation-editors-timeline-headercontrols>`).
Clear Preview Range :kbd:`Alt-P`
   Clears the preview range.
Set Preview Range to Selected :kbd:`Ctrl-Alt-P`
   Automatically select the preview range based on the range of keyframes.


----------

Toggle Dope Sheet
   Changes the area's editor to the :doc:`/editors/dope_sheet/index`.

----------

Area
   Area controls, see the :doc:`user interface </interface/window_system/areas>`
   documentation for more information.

.. seealso::

   - See Graph Editor's :ref:`graph_editor-view-properties`.
   - See Timeline's :ref:`timeline-view-menu`.


Select Menu
-----------

.. _bpy.ops.graph.select_all:

All :kbd:`A`
   Selects all keyframes and handles.
None :kbd:`Alt-A`
   Clears all selected items.
Invert
   Selects all unselected items and unselects any currently selected items.

.. _bpy.ops.graph.select_box:

Box Select :kbd:`B`
   Selects items inside the defined box.
Box Select (Axis Range)
   Todo.
Box Select (Include Handles)
   Selects keyframes and their handles inside the defined box.
Circle Select :kbd:`C`
   Selects keyframe points using circle selection.
Lasso Select
   Selects keyframe points using lasso selection.

.. _bpy.ops.graph.select_column:

Columns on Selected Keys :kbd:`K`
   Selects all other keyframes that are on the same frame as the selected keyframes.
Column on Current Frame :kbd:`Ctrl-K`
   Selects all other keyframes that are on the same frame as the current frame.
Columns on Selected Markers :kbd:`Shift-K`
   Selects all other keyframes that are on the same frame as the selected :doc:`/animation/markers`.
Between Selected Markers :kbd:`Alt-K`
   Selects all keyframes that are between the first and last :doc:`/animation/markers` as they fall in the timeline.

.. _bpy.ops.graph.select_leftright:

Before Current Frame
   Select keyframes to the left of the current frame.
After Current Frame
   Select keyframes to the right of the current frame.

.. _bpy.ops.graph.select_key_handles:

Select Handles
   Selects the associated handles to the currently selected keyframes.
Select Keys
   Selects the associated keyframes to the currently selected handles.

.. _bpy.ops.graph.select_more:
.. _bpy.ops.graph.select_less:

Select More/Less
   Selects/deselects keyframes in close proximity to currently selected keyframes.

.. _bpy.ops.graph.select_linked:

Select Linked
   Select keyframes occurring in the same F-Curves as selected ones.


Markers Menu
------------

:doc:`Markers </animation/markers>` are used to denote frames with key points or significant events
within an animation. Like with most animation editors, markers are shown at the bottom of the editor.

.. figure:: /images/editors_graph-editor_introduction_markers.png

   Markers in animation editor.

For descriptions of the different marker tools see :ref:`Editing Markers <animation-markers-editing>`.


View Controls
-------------

.. figure:: /images/editors_graph-editor_introduction_header-view.png

   View controls.

Show Only Selected
   Only include curves related to the selected objects and data.
Show Hidden
   Include curves from objects/bones that are not visible.
Show Only Errors
   Only include curves and drivers that are disabled or have errors.
   Useful for debugging.

Filter (funnel icon)
   Only include curves with keywords contained in the search field.

   Type Filter
      Filter curves by property type.

   Filtering Collection
      Select a collection to only show keyframes from objects contained in that collection.

   Sort Data-Blocks
      Objects data-blocks appear in alphabetical order, so that it is easier to find where they occur
      (as well as helping to keep the animation of related objects together in the NLA for instance).

      If you find that your playback speed suffers from this being enabled
      (it should only really be an issue when working with lots of objects in the scene),
      you can turn this off.

Normalize
   Normalize curves so the maximum or minimum point equals 1.0 or -1.0.
   When enabled, the view scales to fit the normalized curves and the outer range is darkened.

   If a preview range is defined, keyframes within the range are normalized, while the rest is scaled proportionally.

   Auto
      Automatically recalculate curve normalization on every curve edit.
      This is useful to prevent curves from jumping after tweaking it.

Create Ghost Curves (framed F-Curve icon)
   Creates a picture with the current shape of the curves.


Transform Controls
------------------

.. figure:: /images/editors_graph-editor_introduction_header-edit.png

   Transform controls.

Pivot Point
   Pivot point for rotation.

   :Bounding Box Center: Center of the selected keyframes.
   :2D Cursor: Center of the *2D Cursor*. *Playhead* + *Cursor*.
   :Individual Centers: Rotate the selected keyframe *Bézier* handles.

.. _bpy.types.ToolSettings.use_snap_anim:

Snap
   Activates automatic snapping when you moving keys.

   .. _bpy.types.ToolSettings.snap_anim_element:

   Snap To
      Type of element to snap to.

      :Frame: Snap to frame.
      :Second: Snap to seconds.
      :Nearest Marker: Snap to nearest :doc:`Marker </animation/markers>`.

   .. _bpy.types.ToolSettings.use_snap_time_absolute:

   Absolute Time Snap
      Absolute time alignment when transforming keyframes

Proportional Editing :kbd:`O`
   See :doc:`Proportional Editing </editors/3dview/controls/proportional_editing>`.


Sidebar Region
==============

The panels in the *Sidebar region*.


.. _bpy.types.SpaceGraphEditor.show_cursor:
.. _graph_editor-view-properties:

View Tab
--------

.. figure:: /images/editors_graph-editor_introduction_view-panel.png
   :align: right

   View Tab.

Show Cursor
   Toggles the visibility of the :ref:`2D Cursor <graph_editor-2d-cursor>`.
Cursor X, Y
   Moves the cursor to the specified frame (X value) and value (Y value).
Cursor to Selection
   Places the *2D Cursor* at the midpoint of the selected keyframes.

.. seealso::

   Graph Editor's :ref:`graph-view-menu`.


Further Tabs
------------

F-Curve Tab
   See :doc:`F-Curve </editors/graph_editor/fcurves/properties>`.
Modifiers Tab
   See :doc:`F-Curve Modifiers </editors/graph_editor/fcurves/modifiers>`.
