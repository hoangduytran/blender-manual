.. Mark as "orphan" until extensions is out of beta.

:orphan:

.. index:: Add-ons Extensions
.. index:: Add-ons
.. .. _bpy.types.Addon:
.. .. _bpy.ops.wm.addon:
.. .. _bpy.types.WindowManager.addon:

.. Keep index link until this page is made public,
   so it's possible to navigate to other extensions pages.

:ref:`Extensions Index <extensions-index>`

*******
Add-ons
*******

.. important::

   This page is part of :doc:`Extensions <index>`, and is only available experimentally in
   `daily builds <https://builder.blender.org/download/daily/>`__ of
   `Blender 4.2 <https://projects.blender.org/blender/blender/milestone/19>`__.
   Please enable "Extensions" on the :doc:`Experimental Preferences </editors/preferences/experimental>`
   to help testing it.

   For the deprecated information about individual add-ons bundled with Blender visit :doc:`Add-ons </addons/index>`.

*Add-ons* let you extend Blender's functionality using Python.
Most of the time you can get add-ons as part of the :doc:`Extensions <index>` system.

.. tip::

   If the Add-on does not activate when enabled,
   check the :doc:`Console window </advanced/command_line/introduction>`
   for any errors that may have occurred.

User-Defined Add-on Path
========================

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

Legacy vs Extension Add-ons
===========================

With the introduction of Extensions in Blender 4.2, the old way of creating add-ons is considered deprecated.
While the changes are rather small they impact existing add-ons.

In order to allow a smooth transition process, the so-called legacy add-ons will continue to be supported by Blender.
They can be installed via :doc:`Install legacy Add-on </editors/preferences/extensions>` button in the User
Preferences.

All add-on maintainers are urged to convert the add-ons they want to share, so they are future proof and can support
features like updating from the extensions platform.

Converting a Legacy Add-on into an Extension
--------------------------------------------

#. Create a :doc:`manifest file <getting_started>`.
#. Remove the ``bl_info`` information (this is now in the manifest).
#. Replace all references to the module name to ``__package__``.
#. Make all module imports to use relative import.
#. Use `wheels <https://pythonwheels.com/>`__ to pack your external Python dependencies.
#. Remember to test it throughly.

.. note::

   For testing it is import to :doc:`install the extension from disk </editors/preferences/extensions>` and check if
   everything is working well. This will get you as close to the final experience as possible.

Extensions and Namespace
------------------------

The legacy add-ons would use their module name to access the preferences. This could lead to a name clash when
extensions with the same name (from different repositories) would be installed.
To prevent this conflict, the repository name is now part of the namespace.

For example, now instead of ``kitsu`` the module name would be ``bl_ext.{repository_module_name}.kitsu`` instead.

This has a few implications for preferences and module imports.

User Preferences and ``__package__``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add-ons can define their own preferences which use the package name as an identifier.
This can be accessed using ``__package__``.

This was already supported in the legacy add-ons, but not reinforced.
As such this can break backward compatibility.

Before:

   .. code-block:: python

      class KitsuPreferences(bpy.types.AddonPreferences):
          bl_idname = "kitsu"
          # ... snip ...

      # Access with:
      addon_prefs = bpy.context.preferences.addons["kitsu"]

Now:

   .. code-block:: python

      class KitsuPreferences(bpy.types.AddonPreferences):
          bl_idname = __package__
          # ... snip ...

      # Access with:
      addon_prefs = bpy.context.preferences.addons[__package__]

Sub-packages
   An add-on that defines sub-packages (sub-directories with their own ``__init__.py`` file)
   that needs to use this identifier will have to import the top-level package using a relative import.

   .. code-block:: python

      from .. import __package__ as base_package

   Then ``base_package`` can be used instead of ``__package__``.
   The ``..`` imports relative to the packages parent, sub-sub-packages must use ``...`` and so on.

.. note::

   - The value of ``__package__`` will vary between systems so it should never be replaced with a literal string.
   - Extensions must not manipulate the value of ``__package__`` as this may cause unexpected behavior or errors.


Relative Imports
^^^^^^^^^^^^^^^^

   :before: ``from kitsu import utils``
   :now: ``from . import utils``

Importing packages within the add-on module need to use relative paths.
This is a standard Python feature and only applicable for add-ons that have multiple folders.

This was already supported in the legacy add-ons, but not reinforced. As such this can break backward compatibility.


3rd Party Python Modules
------------------------

Extensions must be self-contained, and as such must come with all its dependencies.

Currently there is no general solution for this although
`support is planned <https://projects.blender.org/blender/blender/issues/119681>`__ using Python
`wheels <https://pythonwheels.com/>`__.

Some options are listed here:

Bundle with `Vendorize <https://pypi.org/project/vendorize>`__
   This can be used as a way to bundle a pure Python dependencies as a sub-module.

   This has the advantage of avoiding version conflicts although it requires some work to setup each package.

.. _extensions-addons-wheels:

Bundle Wheels (``*.whl``)
   Wheels can be bundled using the following steps.

   Downloading Wheels
      Download the wheel to the directory ``./wheels/``.

      For wheels that are platform independent this example downloads ``jsmin``:

      .. code-block:: shell

         pip wheel jsmin -w ./wheels


      For wheels that contain binary compiled files, wheels for all supported platforms should be included:

      This example downloads ``pillow`` - the popular image manipulation module.

      .. code-block:: shell

         pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64
         pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_28_x86_64
         pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64

      To the available platform identifiers are listed on the download page. https://pypi.org/project/pillow/#files

   Update the Manifest
      In ``blender_manifest.toml`` include the wheels as a list of paths, e.g.

      .. code-block:: toml

         wheels = [
            "./wheels/pillow-10.3.0-cp311-cp311-macosx_11_0_arm64.whl",
            "./wheels/pillow-10.3.0-cp311-cp311-manylinux_2_28_x86_64.whl",
            "./wheels/pillow-10.3.0-cp311-cp311-win_amd64.whl",
         ]

   Now installing the package will extract the wheel into the extensions own ``site-packages`` directory.

   Once the extension has been installed you can check the module is being loaded
   by importing it in the Python console and printing it's location, e.g.

   .. code-block:: python

      import PIL
      print(PIL.__file__)
