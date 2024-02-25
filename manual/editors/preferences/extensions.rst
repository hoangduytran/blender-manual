
.. Mark as "orphan" until extensions is out of beta.

:orphan:

**********
Extensions
**********

.. important::

   This feature is only available experimentally in `daily builds <https://builder.blender.org/download/daily/>`__ of
   `Blender 4.2 <https://projects.blender.org/blender/blender/milestone/19>`__.
   Please enable "Extensions" on the
   :doc:`Experimental Preferences </editors/preferences/experimental>` to help testing it.

The *Extensions* section lets you manage the extensions preferences.

.. figure:: /images/editors_preferences_section_extensions.png

   Blender Preferences Extensions section.

.. seealso::

   To learn about extensions and how to create them refer to the :doc:`Extensions </extensions/index>` page.

Install
=======

They are different ways to install an extension:

- **Install from the Website**: Drag the installation URL into Blender.
- **Install from Clipboard**: Copy the URL from the download link on the website.
- **Install from Blender**: From Blender search for the extension name and click on Install.
- **Install from Disk**: For packages saved locally (advanced option, from the Settings menu).

Any installed extension can be removed. This is a permanent change though.
To stop an extension temporarily it is better to Disable it instead.

Update
======

You need to manually check for available updates.
Once an update is found, Blender will let you update any of the available extensions.

The current available version of an extension on the repository will always be considered the latest version.

Enable/Disable
==============

Once an extension is installed it can be disabled (or re-enabled) as part of the user preferences.
Some extension types do not support this, and will always be shown as enabled.

Settings
========

- **Check for Updates**: Manually check the online repositories for available updates.
- **Update All**: Update all the extensions that have an update available.
- **Install from Disk**: Install an extension from a ``.zip`` package.
  This is installed to a Local Repository and no updates will be available.
- **Install Legacy Add-on**: Add-ons are effectively replaced by extensions.
  However to keep old add-ons working for now, they can still be installed independently of the new system.

Filter
======

The available filtering options are:

- Enabled Extensions Only
- Installed Extensions Only

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
