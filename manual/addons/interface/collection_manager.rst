
******************
Collection Manager
******************

This add-on adds new functionality for the management of collections via a pop-up
and a QCD (Quick Content Display) system in the 3D Viewport. It also offers simple
display and modification of the relationship of objects with collections.

|popup| |qcd|

.. |popup| image:: /images/addons_interface_collection-manager_popup.png
   :width: 48 %

.. |qcd| image:: /images/addons_interface_collection-manager_qcd.png
   :width: 48 %


Activation
==========

- Open Blender and go to Preferences then the Add-ons tab.
- Click Interface then Collection Manager to enable the script.


Description
===========


Pop-up
------

Use :kbd:`M` to call up the main Collection Manager pop-up in the 3D View when in Object Mode.

View Layer
   Render
      Enable/disable rendering of this view layer with this checkbox.
   View Layer
      :ref:`ui-data-block` of the current view layer.

Expand All Items
   Toggle all collections expanded or collapsed. Only enabled when you have subcollections.

Renumerate QCD Slots -- *Shown only if QCD is enabled in the preferences.*
   - :kbd:`LMB` -- Renumerate QCD slots in a breadth first pattern starting from the slot designated 1.
   - :kbd:`Alt-LMB` -- Renumerate from the first top-level collection.

Filter (funnel icon)
   Choose which restriction toggles are shown in the interface.

Scene Collection
   Set Active Collection
      Sets the active collection to the Scene Collection.

   Name
      This is static and can't be edited.

   Set Object (box icon)
      - :kbd:`LMB` -- Move object(s) to collection.
      - :kbd:`Shift-LMB` -- Add/Remove object(s) to/from collection.

   Global Restrictions (checkbox, cursor, eye, screen, camera icons)
      See the Outliner page for information about :ref:`Restrictions <editors-outliner-restriction-columns>`.

      - :kbd:`LMB` -- Enable the restriction for all collections. Click again to restore the previous state.
      - :kbd:`Shift-LMB` -- Invert the restriction state on all collections.
      - :kbd:`Ctrl-LMB` -- Copy/Paste the restriction state on all collections.
      - :kbd:`Ctrl-Alt-LMB` -- Swap the restriction state on all collections with that of another restriction.
      - :kbd:`Alt-LMB` -- Discard the previous state, and anything that has been stored for Copy/Paste or Swap.

Tree View
   Shows the collections within the current selected scene.

   Expansion (small triangle icon)
      - :kbd:`LMB` -- Expand/collapse subcollections.
      - :kbd:`Shift-LMB` -- Isolate the tree.  Collapses everything but the current item, and it's parents/descendants. Click again to restore the previous state.
      - :kbd:`Ctrl-LMB` -- Expand/collapse subcollections and their descendants.

   Set Active Collection
      Click to set the active collection to this collection.

   QCD Slot -- *Shown only if QCD is enabled in the preferences.*
      Set which QCD slot the collection corresponds to.

   Name
      Double :kbd:`LMB`-click to rename the collection.

   Set Object (box icon)
      - :kbd:`LMB` -- Move object(s) to collection.
      - :kbd:`Shift-LMB` -- Add/Remove object(s) to/from collection.

   Local Restrictions (checkbox, cursor, eye, screen, camera icons)
      - :kbd:`LMB` -- Toggle the collection's restriction on/off.
      - :kbd:`Shift-LMB` -- Isolate the collection's restriction, preserving parents if need be. Click again to restore the previous state.
      - :kbd:`Shift-Ctrl-LMB` -- Isolate the collection and it's descendants' restrictions, preserving parents if need be. Click again to restore the previous state.
      - :kbd:`Ctrl-LMB` -- Toggle the restrictions of the collection and it's descendants on/off.
      - :kbd:`Alt-LMB` -- Discard the previous state.

   Remove ``X``
      Remove the collection.

   Filtering
      By Name (box icon)
         A text field to filter collections by name.

      Invert (magnifying glass icon)
         Invert filtering (inverts the collections shown in the tree view so that what is
         shown is hidden and what was hidden is shown).

      By Selected (box icon)
         Filter collections by selected objects (show only collections that contain
         the selected objects).

      By QCD Slots (Q key icon) -- *Shown only if QCD is enabled in the preferences.*
         Filter collections by those designated as QCD slots (show only collections that
         correspond to a QCD slot).

Add Collection, Add Subcollection
   Self-explanatory.

Phantom Mode
   All visibility changes made in this mode will be discarded when it's disabled.

   Enabling Phantom Mode saves the current state of your restrictions and
   allows you to edit them without fear of losing your current state.
   When finished, disabling Phantom Mode will restore the saved state.

   Note: You will be unable to edit anything other than the collections' restrictions while in Phantom Mode.


QCD
------

Like the old layers system of 2.79, the Quick Content Display system provides a way to
rapidly interact with collections by allowing you to designate up to 20 collections
as QCD slots.  You can then interact with these slots by using hotkeys or the GUI
to view or move objects to them.

3D View Header Widget
^^^^^^^^^^^^^^^^^^^^^
   **Layout**
      The header widget is composed of 20 buttons in two groups arranged like this::

         01 02 03 04 05   06 07 08 09 10
         11 12 13 14 15   16 17 18 19 20

   **Indicators**
      Each of the slots will show their state by using a combination of the below indicators.

      - ``X`` -- Unassigned slot.
      - ``non-highlighted`` -- non-visible slot.
      - ``highlighted`` -- visible slot.
      - ``no icon`` -- no objects in the slot.
      - ``horizontal line icon`` -- objects are present in this slot.
      - ``circle icon`` -- one or more objects in this slot are selected.
      - ``dot icon`` -- the active object is in this slot.

   **Hotkeys**
      - :kbd:`LMB` -- View slot. Excludes all others.
      - :kbd:`Shift-LMB` -- Add/Remove slot to/from view.
      - :kbd:`Ctrl-LMB` -- Move selected objects to slot.
      - :kbd:`Ctrl-Shift-LMB` -- Add/Remove selected objects to/from slot.


Move Widget
^^^^^^^^^^^
   | Use :kbd:`V` to call up the Move widget in the 3D View when in Object Mode.
   | The Move Widget shares its layout and indicators with the 3D View Header Widget.

   **Hotkeys**
      - :kbd:`LMB` -- Move selected objects to slot.
      - :kbd:`Shift-LMB` -- Add/Remove selected objects to/from slot.
      - :kbd:`0-9` -- Move selected objects to slot #1-10 (0 = 10).
      - :kbd:`Alt+0-9` -- Move selected objects to slot #11-20 (0 = 20).
      - :kbd:`Shift+0-9` -- Add/Remove selected objects to/from slot #1-10 (0 = 10).
      - :kbd:`Shift+Alt+0-9` -- Add/Remove selected objects to/from slot #11-20 (0 = 20).


3D View Hotkeys
^^^^^^^^^^^^^^^
   Object Mode
      - :kbd:`0-9` -- View slot #1-10 (0 = 10). Excludes all others.
      - :kbd:`Alt+0-9` -- View slot #11-20 (0 = 20). Excludes all others.
      - :kbd:`Shift+0-9` -- Add/Remove slot #1-10 (0 = 10) to/from view.
      - :kbd:`Shift+Alt+0-9` -- Add/Remove slot #11-20 (0 = 20) to/from view.

   Edit Mode (Only available if enabled in the preferences.)
      All object mode hotkeys.

      - :kbd:`Backtick (\`)` -- Mesh Select Mode menu.

.. note:: Slots with objects not in object mode can not be excluded.


Preferences
===========
   Checkboxes
      - QCD -- Enable the QCD system.
      - QCD Hotkeys -- Enable 3D View hotkeys for Object Mode.
      - QCD Edit Mode Hotkeys -- Enable 3D View hotkeys for Edit Mode.

   Theme Overrides for the QCD Move Widget.
      Enable overrides in this section to change the color of individual elements
      in the QCD Move Widget (colors default to the current theme).

      Icon Alpha
         | Opacity of the icons for selected (but not active) objects and unselected objects.
         | 0 = fully transparent, 1 = fully opaque.

         .. note:: The values for icon alpha are not overrides and always affect the QCD Move Widget.

.. admonition:: Reference
   :class: refbox

   :Category:  Interface
   :Description: Collection management system.
   :Location: 3D Viewport
   :File: object_collection_manager folder
   :Author: Imaginer (Ryan Inch)
   :Maintainer: Imaginer
   :License: GPL
   :Support Level: Community
   :Note: This add-on is bundled with Blender.
