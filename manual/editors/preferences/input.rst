.. _bpy.types.PreferencesInput:

*****
Input
*****

In the Input preferences, you can customize how Blender reacts to the mouse and keyboard
as well as define your own keymap.

.. figure:: /images/editors_preferences_section_input.png


Keyboard
========

.. _bpy.types.PreferencesInput.use_emulate_numpad:

Emulate Numpad
   The Numpad keys are used quite often in Blender and are not assigned to the same action as
   the regular number keys. If you have a keyboard without a Numpad (e.g. on a laptop),
   you can tell Blender to treat the standard number keys as Numpad keys by checking *Emulate Numpad*.

.. _bpy.types.PreferencesInput.use_numeric_input_advanced:

Default to Advanced Numeric Input
   For transform mode, default to :ref:`transform-numeric-input-advanced`,
   otherwise :ref:`transform-numeric-input-simple` is used.


Mouse
=====

.. _bpy.types.PreferencesInput.use_mouse_emulate_3_button:

Emulate 3 Button Mouse
   Blender can be configured to work with pointing devices which do not have an :kbd:`MMB`.
   The functionality of the three mouse buttons by holding :kbd:`Alt-LMB`.

   Mouse/Keyboard combinations referenced in this manual
   can be expressed with the combinations shown in the table. For example:

   :kbd:`MMB` drag becomes :kbd:`Alt-LMB` drag for example.

   .. warning::

      This option prevents certain features from being accessed,
      since :kbd:`Alt-LMB` is used for some operations.

      - Modifying multiple items values at once (objects, bones... etc).
      - Deselecting edge/face rings in Edit Mode.
      - Detaching node links.
      - Moving the Compositor background image.

      Some touchpads support three-finger tap for middle mouse button,
      which may be an alternative to using this option.

   .. _bpy.types.PreferencesInput.mouse_emulate_3_button_modifier:

   Modifier
      The modifier key to press to emulate the middle mouse keybindings.
      This option is unsupported on Microsoft Windows.

      :Alt:
         Use the :kbd:`Alt` key to emulate the middle mouse button.
      :OSKey:
         Use the :kbd:`OSKey` to emulate the middle mouse button.

         This has the advantage that it doesn't conflict with existing :kbd:`Alt-MMB` shortcuts,
         noted above.

.. _bpy.types.PreferencesInput.use_mouse_continuous:

Continuous Grab
   This feature is used to prevent the problem where an action such as moving objects or panning a view,
   is limited by your screen bounds.

   This is done by warping the mouse within the view.

   .. note::

      Cursor warping is only supported by *relative* input devices (mouse, trackball, trackpad).

      Graphics tablets, however, typically use *absolute* positioning,
      this feature is disabled when a tablet is being used.

      This is detected for each action,
      so the presence of a tablet will not disable *Continuous Grab* for mouse cursor input.

.. _bpy.types.PreferencesInput.use_drag_immediately:

Release Confirms
   Dragging :kbd:`LMB` on an object will move it.
   To confirm this (and other) transform, an :kbd:`LMB` is necessary by default.
   When this option is activated, the release of :kbd:`LMB` acts as confirmation of the transform.

.. _bpy.types.PreferencesInput.mouse_double_click_time:

Double Click Speed
   The time in milliseconds to trigger a double click.

.. _bpy.types.PreferencesInput.drag_threshold_mouse:

Mouse Drag Threshold
   The number of pixels that a User Interface element has to be moved before it is recognized by Blender,
   values below this will be detected as click events.

.. _bpy.types.PreferencesInput.drag_threshold_tablet:

Tablet Drag Threshold
   The drag threshold for tablet events.

.. _bpy.types.PreferencesInput.drag_threshold:

Drag Threshold
   The drag threshold for non mouse/tablet events (keyboard or :term:`NDOF` for example).

   This affects :ref:`Pie Menu on Drag <keymap-pref-py_menu_on_drag>` keymap preference.

.. _bpy.types.PreferencesInput.move_threshold:

Motion Threshold
   The number of pixels the cursor must be moved before the movement is registered.
   This is helpful for tablet pens that are a lot more difficult to keep still,
   then this could help to reduce stuttering of the cursor position.

   .. note::

      Unlike the click/drag distinction, this is used to detect small movements
      for example, picking selection cycles through elements near the cursor.
      Once the cursor moves past this threshold, selection stops cycling and picks the closest item.


Touchpad
========

.. note::

   This panel is available on Windows, macOS, and Linux with Wayland.

.. _bpy.types.PreferencesInput.use_multitouch_gestures:

Multi-touch Gestures
   Use multi-touch gestures for navigation with touchpad, instead of scroll wheel emulation.
   For more detail on supported gestures,
   see :doc:`Configuring Peripherals </getting_started/configuration/hardware>`.

.. _bpy.types.PreferencesInput.touchpad_scroll_direction:

Scroll Direction
   The direction scrolling responds to the scroll gestures.

   Only available on Linux using Wayland.

   :Traditional: Scrolls content down when gestures move up.
   :Natural: Scrolls content up when gestures move up.


Tablet
======

.. _bpy.types.PreferencesInput.tablet_api:

Tablet API (Windows only)
   Select the native Windows Ink or older Wintab system for pressure sensitivity.
   Blender automatically selects the API for your operating system and tablet,
   however in case of problems this can be set manually.
   You may need to restart Blender for changes to take affect.

.. _bpy.types.PreferencesInput.pressure_threshold_max:

Max Threshold
   Amount of pressure required to achieve full intensity.

.. _bpy.types.PreferencesInput.pressure_softness:

Softness
   Controls how the softness of the low pressure response onset using a gamma curve.


.. _editors_preferences_input_ndof:

NDOF
====

These preferences control how an :ref:`NDOF device <hardware-ndof>` interacts with the 3D Viewport.
These preferences can also be accessed using the :kbd:`NDOFMenu` button on the NDOF device
to open a pop-up menu to adjust the settings directly from the 3D Viewport.

.. _bpy.types.PreferencesInput.ndof_sensitivity:

Pan Sensitivity
   The overall sensitivity for panning in the 3D Viewport.

.. _bpy.types.PreferencesInput.ndof_orbit_sensitivity:

Orbit Sensitivity
   The overall sensitivity for orbiting in the 3D Viewport.

.. _bpy.types.PreferencesInput.ndof_deadzone:

Deadzone
   The threshold for the amount of movement needed from
   the device's rest position for Blender to interrupt that movement.

.. _bpy.types.PreferencesInput.ndof_view_navigate_method:

Navigation
   Navigation style for the viewport.

   :Free: Uses the full 6-degrees of freedom.
   :Orbit: Orbit about the view center.

.. _bpy.types.PreferencesInput.ndof_view_rotate_method:

Rotation
   Rotation style for the viewport.

   :Turntable: Rotates the view keeping the horizon horizontal.
   :Trackball: Is less restrictive, allowing any orientation.

.. _bpy.types.PreferencesInput.ndof_show_guide:

Show Navigation Guide
   Display the pivot point and axis during rotation.

.. _bpy.types.PreferencesInput.ndof_zoom_invert:

Invert Zoom
   Zoom using opposite direction.

.. _bpy.types.PreferencesInput.ndof_lock_camera_pan_zoom:

Lock Camera Pan/Zoom
   Pan/zoom the camera view instead of leaving the camera view when orbiting.

.. _bpy.types.PreferencesInput.ndof_pan_yz_swap_axis:

Pan -- Swap Y and Z Axes
   Pan using up/down on the NDOF devices instead of forward/backwards.

.. _bpy.types.PreferencesInput.ndof_panx_invert_axis:

Invert Axis Pan
   Reverses the panning axis on the selected axes.

.. _bpy.types.PreferencesInput.ndof_rotx_invert_axis:

Orbit
   Reverses the orbit axis on the selected axes.

Fly/Walk
   Settings to control how the NDOF device is used while using :ref:`Walk/Fly Navigation <3dview-fly-walk>`.

   .. _bpy.types.PreferencesInput.ndof_lock_horizon:

   Lock Horizon
      Keeps the horizontal axis level while flying.

   .. _bpy.types.PreferencesInput.ndof_fly_helicopter:

   Helicopter Mode
      Moves the 3D Viewport up or down when moving the NDOF device up/down.
