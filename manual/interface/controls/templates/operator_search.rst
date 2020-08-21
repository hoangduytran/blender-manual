.. _bpy.ops.wm.search:

******
Search
******

.. _bpy.ops.wm.search_menu:

Menu Search
===========

.. admonition:: Reference
   :class: refbox

   :Mode:      All Modes
   :Menu:      :menuselection:`Edit --> Menu Search`
   :Hotkey:    :kbd:`F3`

The menu search pop-up searches Blender's interface for a desired tool and allows you to execute that tool.
The menu returns a list of matches and shows which menu the tool was found in.
To use, simply start typing the name of the tool you want to refine the list.
When the list is sufficiently narrowed, :kbd:`LMB` on the desired tool or
navigate with :kbd:`Down` and :kbd:`Up`, activate it by pressing :kbd:`Return`.

.. figure:: /images/interface_controls_templates_operator-search_pop-up.png
   :align: center

   The menu search menu.

.. seealso::

   The :ref:`Spacebar Action <keymap-blender_default-spacebar_action>`
   option in the Preferences.


.. _bpy.ops.wm.search_operator:

Operator Search
===============

.. admonition:: Reference
   :class: refbox

   :Mode:      All Modes
   :Menu:      :menuselection:`Edit --> Menu Search`

When :ref:`Developer Extras <prefs-interface-dev-extras>`
the Operator Search can be accessed from the Edit menu in the Topbar.
This search menu search all operators within Blender even if they are not exposed in a menu.
This is useful for Python developers for testing purposes.
Blender might also include a few advanced operators that are not
exposed in a menu and can only be accessed via this search menu.
