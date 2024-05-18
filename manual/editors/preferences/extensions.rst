.. _bpy.types.Addon:
.. _bpy.ops.wm.addon:
.. _bpy.types.WindowManager.addon:
.. _bpy.ops.preferences.addon:

**********
Extensions
**********

The *Extensions* section lets you manage the extensions preferences.

.. figure:: /images/editors_preferences_section_extensions.png

   Blender Preferences Extensions section.

.. seealso::

   To learn about extensions and how to create them refer to the :doc:`Extensions </extensions/index>` page.

Install
=======

They are different ways to install an extension:

- **Install from the Website**: Drag the installation URL into Blender.
- **Install from Blender**: From Blender search for the extension name and click on Install.
- **Install from Disk**: For packages saved locally (advanced option, from the Settings menu).

Any installed extension can be removed. This is a permanent change though.
To stop an extension temporarily it is better to Disable it instead.

.. note::

   You can *Install from Disk* by drag and dropping an extension ``.zip`` package into Blender.


Install Legacy Add-on
---------------------

To install legacy addons, use the *Install...* button and
use the File Browser to select the ``.zip`` or ``.py`` add-on file.

Now the add-on will be installed, however not automatically enabled.
The search field will be set to the add-on's name (to avoid having to look for it),
Enable the add-on by checking the enable checkbox.

Refresh
   Scans the :doc:`Add-on Directory </advanced/blender_directory_layout>` for new add-ons.

.. tip:: User-Defined Add-on Path

   You can also create a personal directory containing new add-ons and configure your files path in
   the *File Paths* section of the *Preferences*. To create a personal script directory:

   #. Create an empty directory in a location of your choice (e.g. ``my_scripts``).
   #. Add a subdirectory under ``my_scripts`` called ``addons``
      (it *must* have this name for Blender to recognize it).
   #. Open the *File Paths* section of the *Preferences*.
   #. Set the *Scripts* file path to point to your script directory (e.g. ``my_scripts``).
   #. Save the preferences and restart Blender for it to recognize the new add-on location.

   Now when you install add-ons you can select the *Target Path* when installing 3rd party scripts.
   Blender will copy newly installed add-ons under the directory selected in your Preferences.


Update
======

You need to manually check for available updates.
Once an update is found, Blender will let you update any of the available extensions.

The current available version of an extension on the repository will always be considered the latest version.

Enable/Disable
==============

Once an extension is installed it can be disabled (or re-enabled) as part of the user preferences.
Some extension types do not support this, and will always be shown as enabled.

.. tip::

   If the Add-on does not activate when enabled,
   check the :doc:`Console window </advanced/command_line/introduction>`
   for any errors that may have occurred.


Settings
========

- **Check for Updates**: Manually check the online repositories for available updates.
- **Update All**: Update all the extensions that have an update available.
- **Install from Disk**: Install an extension from a ``.zip`` package.
  This is installed to a Local Repository and no updates will be available.
- **Install Legacy Add-on**: Add-ons are effectively replaced by extensions.
  However to keep old add-ons working for now, they can still be installed independently of the new system.


.. _bpy.types.AddonPreferences:

Add-on Preferences
------------------

Some add-ons may have their own preferences which can be found
in the *Preferences* section of the add-on information box.

Some add-ons use this section for example to enable/disable
certain functions of the add-on. Sometimes these might even all default to off.
So it is important to check if the enabled add-on has any particular preferences.


Filter
======

The available filtering options are:

- Enabled Extensions
- Installed Extensions
- Legacy Add-ons

Filter by Type
==============

- **All**: Show all the extension types combined.

Or show only extensions of a single type:

- **Add-ons**
- **Themes**

Repositories
============

By default Blender has a Local Repository and a Remote Repository pointing towards the
`Official Blender Extensions Platform <https://extensions.blender.org>`__.

In the cases where more repositories are needed (e.g., to access third party extension platforms),
new repositories can be added.

.. figure:: /images/editor_preferences_section_extensions_repositories.png

   Repositories.

To add new repositories click on the :menuselection:`+` icon:

- **Add Remote Repository**: Add a repository from a URL.
- **Add Local Repository**: Add a repository which will be managed by the user (to be used with Install from Disk).

To remove repositories click on the :menuselection:`-` icon:

- **Remove Repository**: Remove an extension repository.
- **Remove Repository & Files**: Remove a repository and delete all associated files when removing.

These changes are permanent and cannot be reversed.
