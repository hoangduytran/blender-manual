.. _bpy.types.ToolSettings.use_snap:
.. _transform-snap:

********
Snapping
********

.. reference::

   :Mode:      Object, Edit, and Pose Mode
   :Header:    :menuselection:`Snap`
   :Shortcut:  :kbd:`Shift-Tab`

Snapping lets you easily align objects and mesh elements to others.
It can be toggled by clicking the magnet icon in the 3D Viewport's header,
or more temporarily by holding :kbd:`Ctrl`.

.. figure:: /images/editors_3dview_controls_snapping_header-magnet-icon.png

   Magnet icon in the 3D Viewport header (blue when enabled).

.. figure:: /images/editors_3dview_controls_snapping_element-menu.png

   Snap menu.


.. _bpy.types.ToolSettings.snap_target:

Snap With
=========

.. reference::

   :Mode:      Object, Edit, and Pose Mode
   :Header:    :menuselection:`Snapping --> Snap with`
   :Shortcut:  :kbd:`Shift-Ctrl-Tab`

Determines what part of the selection will coincide with the target.
(The rest of the selection will follow along.)

Active
   Snaps using the origin (in Object Mode) or center (in Edit Mode) of the active element.
Median
   Snaps using the median of the selection.
Center
   Snaps using the current transformation center
   (another word for the :doc:`pivot point </editors/3dview/controls/pivot_point/index>`).
   This option is especially useful in combination with the
   :doc:`3D Cursor </editors/3dview/3d_cursor>` for choosing the snapping
   point completely manually.
Closest
   Snaps using the vertex that's closest to the target.

.. list-table::

   * - .. figure:: /images/editors_3dview_controls_snapping_target-closest.png

          Closest.

     - .. figure:: /images/editors_3dview_controls_snapping_target-active.png

          Active.

     - .. figure:: /images/editors_3dview_controls_snapping_target-median.png

          Median.


.. _bpy.types.ToolSettings.snap_elements_base:

Snap To
=======

.. reference::

   :Mode:      Object, Edit, and Pose Mode
   :Header:    :menuselection:`Snapping --> Snap To`
   :Shortcut:  :kbd:`Shift-Ctrl-Tab`

Determines the target which the selection will be snapped to.

Increment
   Snaps to grid points. When in Orthographic view, the snapping increment changes depending on the zoom level.

   .. note::

      By default, this option won't snap to the grid that's displayed in the viewport,
      but an imaginary grid with the same resolution that starts at the selection's
      original location. In other words, it lets you move the selection in "increments" of the
      grid cell size.

      If you want to snap to the viewport grid instead, you can enable *Absolute Grid Snap*
      (see below).
Vertex
   Snaps to the vertex that's closest to the mouse cursor.
Edge
   Snaps to the edge that's closest to the mouse cursor.
Volume
   Snaps the selection to a depth that's centered *inside* the object under the cursor.
   This is useful for positioning an :doc:`Armature </animation/armatures/introduction>`
   bone so it's centered inside a character's arm, for example; the other snapping options
   would place it on the arm's surface instead.

   While Blender also has :doc:`Volume objects </modeling/volumes/introduction>`, this option
   is not related to those.
Edge Center
   Snaps to the centerpoint of the edge that's closest to the mouse cursor.
Edge Perpendicular
   Snaps to a specific point on the edge so that the line from the selection's original location
   (indicated by a white cross) to its new location is perpendicular to that edge.

.. tip::

   Multiple snapping modes can be enabled at once using :kbd:`Shift-LMB`.


.. _bpy.types.ToolSettings.snap_elements_individual:

Snap Individual Elements To
===========================

.. reference::

   :Mode:      Object, Edit, and Pose Mode
   :Header:    :menuselection:`Snapping --> Snap Individual Elements To`
   :Shortcut:  :kbd:`Shift-Ctrl-Tab`

Type of element for individual transformed elements to snap to.

Face Project
   Snaps to the face that's under the mouse cursor.

   This can be used for bending a flat sheet so it snugly fits against a curved
   surface, for example.

   .. seealso::

      :doc:`/modeling/modifiers/deform/shrinkwrap`

Face Nearest
   Individually snaps each object (in Object Mode) or vertex (in Edit Mode) to the face that's closest
   to its new location. This makes it possible to snap to occluded geometry.


Target Selection
================

Sets more detailed snapping options. The available options depend on the mode
(Object/Edit) as well as the Snap To selection.

.. _bpy.types.ToolSettings.use_snap_self:

Include Active :guilabel:`Edit Mode`
   Snap to other mesh elements of the active object.

   This checkbox is ignored if
   :doc:`Proportional Editing </editors/3dview/controls/proportional_editing>`
   is enabled.

.. _bpy.types.ToolSettings.use_snap_edit:

Include Edited :guilabel:`Edit Mode`
   Snap to other objects that are also in Edit Mode.

.. _bpy.types.ToolSettings.use_snap_nonedit:

Include Non-Edited :guilabel:`Edit Mode`
   Snap to other objects that are not in Edit Mode.

.. _bpy.types.ToolSettings.use_snap_selectable:

Exclude Non-Selectable
   Snap only to objects that are selectable.

.. _bpy.types.ToolSettings.use_snap_grid_absolute:

Absolute Grid Snap :guilabel:`Increment`
   Snaps to the grid, instead of snapping in increments relative to the current location.

.. _bpy.types.ToolSettings.use_snap_align_rotation:

Align Rotation to Target
   Rotates the selection so that its Z axis gets aligned to the normal of the target.

.. _bpy.types.ToolSettings.use_snap_backface_culling:

Backface Culling
   Exclude back-facing geometry from snapping.

.. _bpy.types.ToolSettings.use_snap_to_same_target:

Snap to Same Target :guilabel:`Face Nearest`
   Snap only to the object which the selection was nearest to before starting
   the transformation.

.. _bpy.types.ToolSettings.snap_face_nearest_steps:

Face Nearest Steps :guilabel:`Face Nearest` :guilabel:`Edit Mode`
   Breaks the overall transformation into multiple steps, performing a snap each time.
   This can give better results in certain cases.

.. _bpy.types.ToolSettings.use_snap_peel_object:

Snap Peel Object :guilabel:`Volume`
   If the target object is composed of several disconnected mesh islands that
   intersect each other, "Snap To Volume" will normally snap to the island which the
   mouse is hovering over, ignoring the other islands. By enabling "Snap Peel Object,"
   you can instead treat the target object as one connected whole.


.. _bpy.types.ToolSettings.use_snap_translate:
.. _bpy.types.ToolSettings.use_snap_rotate:
.. _bpy.types.ToolSettings.use_snap_scale:

Affect
======

Specifies which transformations are affected by snapping.
By default, snapping only happens while moving something,
but you can also enable it for rotating and scaling.


Multiple Snap Targets
---------------------

While you're transforming a selection with snapping enabled,
you can press :kbd:`A` whenever there's a highlighted snap target to
mark it. With multiple such targets marked, the selection will
then be snapped to their average location.

Marking a target more than once will give it more weight.

.. figure:: /images/editors_3dview_controls_snapping_target-multiple.png

   Multiple snapping targets.
