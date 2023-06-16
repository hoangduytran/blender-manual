
******
Sculpt
******

This page details the general hotkey operators and menu operators in sculpt mode.


Show & Hide
===========

Some very common hotkey operators to control the visibility based on face sets.
These are not part of any menu and have to be used via the shortcuts.
More visibility operators can be found in the :doc:`Face Sets Menu </sculpt_paint/sculpting/editing/face_sets>`
and the Pie Menu shortcut :kbd:`W`. (Since visibility is often toggled via face sets.)

.. _bpy.ops.sculpt.face_set_change_visibility:

Toggle Visibility :kbd:`H`
   Hide all face sets except the active one (under the cursor).
   If face sets are already hidden, then this operator will show everything.

Hide Active Face Set :kbd:`Shift-H`
   Hide the face set under the cursor. Press :kbd:`H` afterwards to show everything.

.. note::

   These two shortcuts are inverted compared to other modes, to make the operators more convenient to access.
   Toggling the Visibility is far more often used. If this behavior is undesired it's recommended
   to change the keymap in the preferences.

.. _sculpt_show_all:

.. reference::

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Sculpt`

Show All :kbd:`W`, :kbd:`Alt-H`
   Reveal all hidden faces.
Show Bounding Box
   Draw a box to reveal hidden faces.
   This works similar to the :ref:`Box Select <tool-select-box>` tool.
Hide Bounding Box
   Draw a box to hide faces of a mesh.
Hide Masked
   Hides all masked vertices.

.. seealso::

   For a more general introduction see
   :doc:`Visibility, Masking & Face Sets </sculpt_paint/sculpting/introduction/visibility_masking_face_sets>`.


.. _bpy.ops.sculpt.set_pivot_position:

Set Pivot
=========

.. reference::

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Sculpt --> Set Pivot`

Like Object and Edit Mode, Sculpt Mode also has a :term:`Pivot Point`.
This is because the basic :doc:`move, rotate and scale </sculpt_paint/sculpting/tools/transforms>`
transforms are also supported in Sculpt Mode.
But the pivot point in Sculpt Mode is unique. It always moves together with the transformed mesh
and can be both manually & automatically placed.

Origin
   Sets the pivot to the origin of the sculpt.
Unmasked
   Sets the pivot position to the average position of the unmasked vertices.
Mask Border
   Sets the pivot position to the center of the mask's border.
   This operation will automatically happen when using :ref:`bpy.ops.sculpt.expand`.
Active Vertex
   Sets the pivot position to the active vertex position.
Surface
   Sets the pivot position to the surface under the cursor.

.. tip::

   For more convenient placement of the pivot point it's recommended to assign a shortcut to either
   *Surface* or *Active Vertex*.

.. seealso::

   For a more general introduction see :doc:`Transforming </sculpt_paint/sculpting/introduction/transforming>`.


Transfer Sculpt Mode
====================

.. reference::

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Sculpt --> Transfer Sculpt Mode`
   :Shortcut:  :kbd:`Alt-Q`

Switches Sculpt Mode from the :term:`Active` object to the object under the mouse.
See :ref:`bpy.ops.object.transfer_mode` for more information.

.. seealso::

   For a more general introduction see
   :doc:`Working with Multiple Objects </sculpt_paint/sculpting/introduction/multiple_objects>`.


.. _bpy.ops.sculpt.optimize:

Rebuild BVH
===========

.. reference::

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Sculpt --> Rebuild BVH`

Recalculates the :term:`BVH` used by :doc:`/sculpt_paint/sculpting/tool_settings/dyntopo`
to improve performance, which might degrade over time while using Dyntopo.

.. seealso::

   For a more general introduction see :doc:`Adaptive Resolution </sculpt_paint/sculpting/introduction/adaptive>`.
