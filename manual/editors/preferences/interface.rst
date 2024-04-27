.. _bpy.types.PreferencesView:

*********
Interface
*********

Interface configuration lets you change how UI elements are displayed and how they react.

.. figure:: /images/editors_preferences_section_interface.png


Display
=======

.. _bpy.types.PreferencesView.ui_scale:

Resolution Scale
   Adjusts the size of fonts and buttons relative to the automatically detected DPI.
   During typical usage, you may prefer to use zoom which is available in many parts of Blender interface.

.. _bpy.types.PreferencesView.ui_line_width:

Line Width
   Scale of lines and points in the interface e.g. button outlines, edges and vertex points in the 3D Viewport.

   Thin, Default, Thick

.. _bpy.types.PreferencesView.show_splash:

Splash Screen
   Display the :ref:`splash` when starting Blender.

.. _bpy.types.PreferencesView.show_developer_ui:

Developer Extras
   Show settings and menu items which are intended to help developers, this includes:

   - :doc:`Operator Search </interface/controls/templates/operator_search>`
   - :doc:`Sequencer Cache Settings </editors/video_sequencer/sequencer/sidebar/cache>`

   Button Context Menu
      Online Python Reference
         To open the Python reference manual.
      Copy Python Command
         To copy the expression used when pressing the button.
      Edit Source
         To edit Python source code that defines the button.
      Edit Translation
         The option to edit UI translations
         (only available when the *Manage UI translations* add-on is also enabled).
   3D Viewport
      Show Indices
         The option to show mesh vertex/edge/face indices in the overlay popover.
   Preferences
      Experimental Tab
         Work in progress features can be enabled here which are currently being tested.

.. _bpy.types.PreferencesView.show_tooltips:

Tooltips
   User Tooltips
      When enabled, a tooltip will appear when your mouse pointer is over a control.
      This tip explains the function of what is under the pointer,
      shows the associated hotkey (if any).

   .. _bpy.types.PreferencesView.show_tooltips_python:

   Python Tooltips
      Displays a property's Python information below the tooltip.

.. _bpy.types.Preferences.use_recent_searches:

Search -- Sort by Most Recent
   Show most recently selected items at the top of search results,
   otherwise search results are sorted alphabetically.


Editors
=======

.. _bpy.types.PreferencesSystem.use_region_overlap:

Region Overlap
   This makes regions overlap the viewport. It means that the *Toolbar* and *Sidebar* regions,
   will be displayed overlapping the main area.

.. _bpy.types.PreferencesView.show_navigate_ui:

Navigation Controls
   Show navigation controls at top right of the area.
   This impacts the 3D Viewport as well as image spaces.

   .. note::

      If you are familiar with navigation key shortcuts, this can be disabled.

.. _bpy.types.PreferencesView.color_picker_type:

Color Picker Type
   Choose which type of :term:`Color Space` you prefer. It will show when clicking :kbd:`LMB` on any color field.

   See the different color picker types at the :doc:`Color picker </interface/controls/templates/color_picker>` page.

.. _bpy.types.PreferencesView.header_align:

Header Position
   The default header position when opening a new editor.

   :Keep Existing:
      Uses top for most editor types and the positions saved in the start-up file.
   :Top/Bottom:
      Always positions the header at the top or the bottom of the editor.

.. _bpy.types.PreferencesView.factor_display_type:

Factor Display Type
   How factor value types are displayed in the user interface.

   :Factor: Values are displayed as float numbers between 0.0 and 1.0.
   :Percentage: Values are expressed as a percentage between 0 and 100.


Temporary Editors
-----------------

When performing certain operations, Blender will open a new window.
The behavior of these operations can be configured here.

.. _bpy.types.PreferencesView.render_display_type:

Render In
   When rendering, the user interface can do any of:

   :Keep User Interface: The user interface does not change and the render is computed in the background.
   :Maximize Area: A new Image editor is opened as a temporary window in full screen mode.
   :Image Editor: The area that is the largest on screen is replaced placed by a temporary Image editor.
   :New Window: A new Image editor is opened as a regularly sized temporary window.

.. _bpy.types.PreferencesView.filebrowser_display_type:

File Browser
   When opening files from the computer, the user interface can do any of:

   :Maximize Area: A new File Browser editor is opened as a temporary window in full screen mode.
   :New Window: A new File Browser editor is opened as a regularly sized temporary window.


.. _prefs-interface-translation:

Language
========

.. _bpy.types.PreferencesView.language:

Language
   The language used for translating the user interface (UI).
   The list is broken up into categories determining how complete the translations are.

.. _bpy.types.PreferencesView.use_translate:

Translate
   Tooltips
      Translates the descriptions when hovering over UI elements.
   Interface
      Translates all labels in menus, buttons, and panels.
   New Data
      Translates the names of new data-blocks.


Text Rendering
==============

.. _bpy.types.PreferencesView.use_text_antialiasing:

Anti-Aliasing
   Enable interface text :term:`Anti-Aliasing`.
   When disabled, texts are rendered using straight text rendering (filling only absolute pixels).

.. _bpy.types.PreferencesView.use_text_render_subpixelaa:

Subpixel Anti-Aliasing
   Render text for optimal horizontal placement.

.. _bpy.types.PreferencesView.text_hinting:

Hinting
   Adjust `font hinting <https://en.wikipedia.org/wiki/Font_hinting>`__,
   controls the spacing and crispness of text display.

.. _bpy.types.PreferencesView.font_path_ui:

Interface Font
   Replacement for the default user interface font.

.. _bpy.types.PreferencesView.font_path_ui_mono:

Mono-space Font
   Replacement for the default mono-space interface font
   *(used in the Text editor and Python Console)*.


Menus
=====

.. _bpy.types.PreferencesView.use_mouse_over_open:

Open on Mouse Over
------------------

Select this to have the menu open by placing the mouse pointer over the entry instead of clicking on it.

.. _bpy.types.PreferencesView.open_toplevel_delay:

Top Level
   Time delay in 1/10 second before a menu opens (*Open on Mouse Over* needs to be enabled).

.. _bpy.types.PreferencesView.open_sublevel_delay:

Sub Level
   Same as above for sub menus (for example: :menuselection:`File --> Open Recent`).


.. _prefs-pie-menu:

Pie Menus
---------

.. _bpy.types.PreferencesView.pie_animation_timeout:

Animation Timeout
   Length of animation when opening Pie Menus.

.. _bpy.types.PreferencesView.pie_tap_timeout:

Tap Key Timeout
   Keystrokes held longer than this will dismiss the menu on release (in 1/100ths of a second).

.. _bpy.types.PreferencesView.pie_initial_timeout:

Recenter Timeout
   The window system tries to keep the pie menu within the window borders.
   Pie menus will use the initial mouse position as center for this amount of time, measured in 1/100ths of a second.
   This allows for fast dragged selections.

.. _bpy.types.PreferencesView.pie_menu_radius:

Radius
   The size of the Pie Menu set with the distance (in pixels) of the menu items from the center of the pie menu.

.. _bpy.types.PreferencesView.pie_menu_threshold:

Threshold
   Distance from center before a selection can be made.

.. _bpy.types.PreferencesView.pie_menu_confirm:

Confirm Threshold
   Distance threshold after which selection is made (zero disables).
