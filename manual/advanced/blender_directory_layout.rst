.. _blender-directory-layout:

**************************
Blender's Directory Layout
**************************

This page documents the different directories used by Blender.

This can be helpful for troubleshooting, automation and customization.


User Directories
================

User directories store preferences, startup file, installed extensions,
presets and more. By default these use the standard configuration folders
for each operating system.

Linux
-----

.. parsed-literal:: $HOME/.config/blender/|BLENDER_VERSION|/

If the ``$XDG_CONFIG`` environment variable is set:

.. parsed-literal:: $XDG_CONFIG_HOME/blender/|BLENDER_VERSION|/

macOS
-----

.. parsed-literal:: /Users/$USER/Library/Application Support/Blender/|BLENDER_VERSION|/

Windows
-------

.. parsed-literal:: %USERPROFILE%\\AppData\\Roaming\\Blender Foundation\\Blender\\\ |BLENDER_VERSION|\\

.. _portable-installation:

Portable Installation
---------------------

When running Blender from a portable drive, it's possible to keep the configuration
files on the same drive to take with you.

To enable this, create a folder named ``portable`` at the following locations:

* Windows: Next to the Blender executable, in the unzipped folder
* Linux: Next to the Blender executable, in the unzipped folder
* macOS: Inside the application bundle at ``Blender.app/Contents/Resources``

This folder will then store preferences, startup file, installed extensions
and presets.

Environment Variables
---------------------

``BLENDER_USER`` :ref:`command-line-args-environment-variables` can be used to store
some or all configuration files in other directories.

This may be used for example when using a different configuration for a specific
project, without affecting the regular user configuration.


System Directories
==================

System directories store files that come bundled with Blender and
are required for it to function. This includes scripts, presets, essential
assets and more. 

Linux
-----

Archive downloaded from blender.org:

.. parsed-literal:: ./|BLENDER_VERSION|/

Linux distribution packages:

.. parsed-literal:: /usr/share/blender/|BLENDER_VERSION|/

macOS
-----

.. parsed-literal:: ./Blender.app/Contents/Resources/|BLENDER_VERSION|/

Windows
-------

Zip file downloaded from blender.org:

.. parsed-literal:: ./|BLENDER_VERSION|/

Installer downloaded from blender.org:

.. parsed-literal:: %ProgramFiles%\\Blender Foundation\\Blender\\\ |BLENDER_VERSION|\\

Microsoft Store installation:

.. parsed-literal:: %ProgramFiles%\\WindowsApps\\BlenderFoundation.Blender<HASH>\\Blender\\\ |BLENDER_VERSION|\\


Environment Variables
---------------------

``BLENDER_SYSTEM`` :ref:`command-line-args-environment-variables`
can be used to bundle additional scripts and extensions, that are not part of the
regular Blender installation.

This can be used for example to deploy Blender in an animation studio, with
additional add-ons available to all users.


Path Layout
===========

This is the path layout which is used within the directories described above.

Configuration files are only stored in user directories, while scripts and data
files can exist in both user and system directories.

Where ``./config/startup.blend`` could be ``~/.blender/|BLENDER_VERSION|/config/startup.blend`` for example.

``./autosave/ ...``
   Autosave blend-file location. (Windows only, temp directory used for other systems.)

   Search order: ``LOCAL, USER``.

``./config/ ...``
   Defaults & session info.

   Search order: ``LOCAL, USER``.

``./config/startup.blend``
   Default file to load on startup.

``./config/userpref.blend``
   Default preferences to load on startup.

``./config/bookmarks.txt``
   File Browser bookmarks.

``./config/recent-files.txt``
   Recent file menu list.

``./datafiles/ ...``
   Runtime files.

   Search order: ``LOCAL, USER, SYSTEM``.

``./datafiles/locale/{language}/``
   Static precompiled language files for UI translation.

``./scripts/ ...``
   Python scripts for the user interface and tools.

   Search order: ``LOCAL, USER, SYSTEM``.

``./scripts/addons/*.py``
   Python add-ons which may be enabled in the Preferences include import/export format support,
   render engine integration and many handy utilities.

``./scripts/addons/modules/*.py``
   Modules for add-ons to use
   (added to Python's ``sys.path``).

``./scripts/addons_core/*.py``
   The add-ons directory which is used for bundled add-ons.

``./scripts/addons_core/modules/*.py``
   Modules for ``addons_core`` to use (added to Python's ``sys.path`` when it found).

``./scripts/modules/*.py``
   Python modules containing our core API and utility functions for other scripts to import
   (added to Python's ``sys.path``).

``./scripts/startup/*.py``
   Scripts which are automatically imported on startup.

``./scripts/presets/{preset}/*.py``
   Presets used for storing user-defined settings for cloth, render formats, etc.

``./scripts/templates_py/*.py``
   Example scripts which can be accessed from :menuselection:`Text Editor --> Templates --> Python`.

``./scripts/templates_osl/*.osl``
   Example OSL shaders which can be accessed from
   :menuselection:`Text Editor --> Templates --> Open Shading Language`.

``./python/ ...``
   Bundled Python distribution.

   Search order: ``LOCAL, SYSTEM``.


.. _local-cache-dir:

Local Cache Directory
=====================

The cache directory is used to store persistent caches locally. Currently it is only used for the indexing of
:ref:`Asset Libraries <what-is-asset-library>`. The operating system is not expected to clear this automatically.

The following path will be used:

- :Linux: ``$XDG_CACHE_HOME/blender/`` if ``$XDG_CACHE_HOME`` is set, otherwise ``$HOME/.cache/blender/``
- :macOS: ``/Library/Caches/Blender/``
- :Windows: ``%USERPROFILE%\AppData\Local\Blender Foundation\Blender\Cache\``


.. _temp-dir:

Temporary Directory
===================

The temporary directory is used to store various files at run-time
(including render layers, physics cache, copy-paste buffer and crash logs).

The temporary directory is selected based on the following priority:

- User Preference (see :ref:`prefs-file-paths`).
- Environment variables (``TEMP`` on Windows, ``TMP`` & ``TMP_DIR`` on other platforms).
- The ``/tmp/`` directory.
