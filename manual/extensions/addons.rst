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

For example, now instead of ``kitsu`` the module name would be ``bl_ext.RemoteRepository.kitsu`` instead.

This has a few implications for preferences and module imports.

User Preferences and ``__package__``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   :before: ``bpy.context.preferences.addons["kitsu"]``
   :now: ``bpy.context.preferences.addons[__package__]``


Add-ons can define their own preferences, and can access them using the complete module name. This is done by using
``__package__``.

This was already supported in the legacy add-ons, but not reinforced. As such this can break backward compatibility.

Relative Imports
^^^^^^^^^^^^^^^^

   :before: ``from kitsu import utils``
   :now: ``from . import utils``

Importing packages within the add-on module need to use relative paths.
This is a standard Python feature and only applicable for add-ons that have multiple folders.

This was already supported in the legacy add-ons, but not reinforced. As such this can break backward compatibility.

Wheels
------

Extensions are supposed to be self-contained, and as such must come with all its dependencies. When relying on
external modules they should be bundled together by using `wheels <https://pythonwheels.com/>`__.

Wheels themselves can lead to version conflicts, since different add-ons could require different versions of the same
library.

Luckily there is an alternative way of loading wheels that doesn't affect ``sys.modules`` or ``sys.path``.
This way an add-on can load its own version of an external library from its bundled wheel file,
without no other add-on having access to it.

See Flamenco add-on for an `implementation example
<https://projects.blender.org/studio/flamenco/src/branch/main/addon/flamenco/wheels/__init__.py>`__.
