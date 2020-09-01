
*********************
Basic Transformations
*********************

.. _bpy.ops.transform.translate:

Move
====

.. admonition:: Reference
   :class: refbox

   :Mode:      Object Mode, Edit Mode, and Pose Mode
   :Menu:      :menuselection:`Object/Mesh/Curve/Surface --> Transform --> Move`
   :Hotkey:    :kbd:`G`

In Object Mode, the move option lets you move objects.
Translation means changing location of objects. It also lets you move any elements
that make up the object within the 3D space of the active 3D Viewport.

Pressing :kbd:`G` activates "Move" transformation mode. The selected object
or element then moves freely according to the mouse pointer's location and camera.

To confirm the action, press :kbd:`LMB`.

While moving items, the amount of change along the X, Y, and Z axis is displayed in the header of the 3D Viewport.

.. figure:: /images/scene-layout_object_editing_transform_basics_grab-display-values.png

   Translation Display.

.. tip::

   Moving an object in Object Mode changes the object's origin.
   Moving the object's vertices/edges/faces in Edit Mode does not change the object's origin.

.. seealso::

   Using a combination of shortcuts gives you more control over your transformation.
   See :doc:`Transform Control </scene_layout/object/editing/transform/control/index>`.


Options
-------

Move X, Y, Z
   The amount to move the selection on the respected axis.

Orientation
   Aligns the transformation axes to a specified orientation constraint.
   See :doc:`Transform Orientations </editors/3dview/controls/orientation>` for more information.

Proportional Editing
   The extruded face will affect nearby geometry.
   See :doc:`Proportional Editing </editors/3dview/controls/proportional_editing>` for a full reference.


.. _bpy.ops.transform.rotate:

Rotate
======

.. admonition:: Reference
   :class: refbox

   :Mode:      Object and Edit Modes
   :Menu:      :menuselection:`Object/Mesh/Curve/Surface --> Transform --> Rotate`
   :Hotkey:    :kbd:`R`

Rotation is also known as a spin, twist, orbit, pivot, revolve, or roll and
involves changing the orientation of elements (vertices, edges, faces, objects, etc.)
around one or more axes or
the :doc:`Pivot Point </editors/3dview/controls/pivot_point/index>`.

The angle of rotation is displayed in the header of the 3D Viewport.

.. figure:: /images/scene-layout_object_editing_transform_basics_rotate-display-values.png

   Rotation values.

.. seealso::

   Using a combination of shortcuts gives you more control over your transformation.
   See :doc:`Transform Control </scene_layout/object/editing/transform/control/index>`.


Options
-------

Angle
   The amount of rotation.

Axis
   Used to constraint the transformation to one or more axes.

Orientation
   Aligns the transformation axes to a specified orientation constraint.
   See :doc:`Transform Orientations </editors/3dview/controls/orientation>` for more information.

Proportional Editing
   The extruded face will affect nearby geometry.
   See :doc:`Proportional Editing </editors/3dview/controls/proportional_editing>` for a full reference.


.. _view3d-transform-trackball:
.. _bpy.ops.transform.trackball:

Trackball Rotation
==================

A free rotation mode. Press :kbd:`R R` to enable Trackball rotation.


.. _bpy.ops.transform.resize:

Scale
=====

.. admonition:: Reference
   :class: refbox

   :Mode:      Object and Edit Modes
   :Menu:      :menuselection:`Object/Mesh/Curve/Surface --> Transform --> Scale`
   :Hotkey:    :kbd:`S`

Scaling means changing proportions of objects. Pressing :kbd:`S` will enter
the *Scale* transformation mode where the selected element is scaled inward or
outward according to the mouse pointer's location. The element's scale will
increase as the mouse pointer is moved away from the Pivot Point and decrease as
the pointer is moved towards it. If the mouse pointer crosses from the original side of
the :doc:`Pivot Point </editors/3dview/controls/pivot_point/index>`
to the opposite side, the scale will continue in the negative direction and flip the element.

.. figure:: /images/scene-layout_object_editing_transform_basics_scale-basic-usage.png

   Basic scale usage. From left to right, the panels show: the original object,
   a scaled down object, a scaled up object and a scale-flipped object.

The amount of scaling will be displayed in the header of the 3D Viewport.

.. figure:: /images/scene-layout_object_editing_transform_basics_scale-display-values.png

   Scale values.

.. seealso::

   Using a combination of shortcuts gives you more control over your transformation.
   See :doc:`Transform Control </scene_layout/object/editing/transform/control/index>`.


Options
-------

Scale X, Y, Z
   The amount to resize the selection on the respected axis.

Orientation
   Aligns the transformation axes to a specified orientation constraint.
   See :doc:`Transform Orientations </editors/3dview/controls/orientation>` for more information.

Proportional Editing
   The extruded face will affect nearby geometry.
   See :doc:`Proportional Editing </editors/3dview/controls/proportional_editing>` for a full reference.
