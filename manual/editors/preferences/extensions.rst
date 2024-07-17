.. _bpy.types.Addon:
.. _bpy.ops.wm.addon:
.. _bpy.types.WindowManager.addon:
.. _bpy.ops.preferences.addon:
.. _prefs-extensions:

**********
Extensions
**********

The *Extensions* section lets you manage the extensions preferences.

.. figure:: /images/editors_preferences_section_extensions.png

   Blender Preferences Extensions section.

.. seealso::

   To learn about extensions and how to create them, refer to the :ref:`Extensions <extensions-index>` page.


.. _prefs-extensions-install:

Install
=======

There are different ways to install an extension:

Install from the Website
   Drag the installation URL into Blender.
Install from Blender
   Search for the extension name and click on Install.
Install from Disk
   Use the drop-down menu in the top right,
   or drag-and-drop an extension ``.zip`` package into Blender.

Any installed extension can be removed. This is a permanent change, though.
To stop an extension temporarily, it is better to Disable it instead.


.. _prefs-extensions-install_legacy_addon:

Install Legacy Add-on
---------------------

To install legacy add-ons, click the *Install from Disk* menu item and select the addon's
``.py`` file (if it has only one such file) or its ``.zip`` file.

The add-on will not be automatically enabled after installation; click the checkbox to do that.

Refresh
   Scans the :ref:`Add-on Directory <blender-directory-layout>` for new add-ons.

.. tip::

   While this screen doesn't allow installing a folder-based addon with loose ``.py`` files,
   you can still do so by adding it as a :ref:`Script Directory <bpy.types.ScriptDirectory>`:

   #. Create an empty directory in a location of your choice (e.g. ``my_scripts``).
   #. Add a subdirectory under ``my_scripts`` called ``addons``
      (it *must* have this name for Blender to recognize it).
   #. Place your addon folder inside this ``addons`` folder.
   #. Open the *File Paths* section of the *Preferences*.
   #. Add a *Script Directories* entry pointing to your script folder (e.g. ``my_scripts``).
   #. Save the preferences and restart Blender for it to recognize the new add-on location.

   The add-ons in this folder will automatically become available; all you need to
   do is enable them.


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
   check the :doc:`Console window </advanced/command_line/index>`
   for any errors that may have occurred.


Settings
========

Check for Updates
   Manually check the online repositories for available updates.
Update All
   Update all the extensions that have an update available.
Install from Disk
   Install an extension from a ``.zip`` package.
   This is installed to a Local Repository and no updates will be available.
Install Legacy Add-on
   Add-ons are effectively replaced by extensions.
   However to keep old add-ons working for now, they can still be installed independently of the new system.


.. _bpy.types.AddonPreferences:

Add-on Preferences
------------------

Some add-ons may have their own preferences which can be found
in the *Preferences* section of the add-on information box.

Some add-ons use this section for example to enable/disable
certain functions of the add-on. Sometimes these might even all default to off.
So it is important to check if the enabled add-on has any particular preferences.


Filter by Type
==============

Or show only extensions of a single type:

:Add-ons:
:Themes:


Repositories
============

By default Blender has a Remote Repository pointing towards the
`Official Blender Extensions Platform <https://extensions.blender.org>`__ and two Local Repositories.

In the cases where more repositories are needed (e.g., to access third party extension platforms),
new repositories can be added.

.. figure:: /images/editor_preferences_section_extensions_repositories.png
   :width: 450px

   Repositories.

To add new repositories click on the :menuselection:`+` icon:

Add Remote Repository
   Add a repository from a URL.
Add Local Repository
   Add a repository which will be managed by the user (to be used with Install from Disk).

To remove repositories click on the :menuselection:`-` icon:

Remove Repository
   Remove an extension repository.
Remove Repository & Files
   Remove a repository and delete all associated files when removing.

These changes are permanent and cannot be reversed.


Remote Repository
-----------------

Remote repository with support for listing and updating extensions.

Options:

Check for Updates on Startup
   Allows Blender to check for updates upon launch.
   When updates are available a notification will be visible on the status bar.
Access Token
   Personal access token, may be required by some repositories.


Local Repository
----------------

A repository managed manually by the users.

There are two types of local repositories. By default new local repositories are added as User repositories.
This is what you want most of the time.

After creating a repository they can be changed in the Advanced options to have a source System.
These repositories are intended to :ref:`bundle extensions <deploying-blender-bundling>`
with Blender, to make it portable.
