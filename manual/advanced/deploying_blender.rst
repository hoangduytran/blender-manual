.. _deploying-blender:

*******************************
Deploying Blender in Production
*******************************

It is possible to deploy Blender in environments that are more
restricted, use automation or have other special requirements.
For example in an animation studio or for school courses.

This page contains tips setting up Blender in such environments.

Installing Blender
==================

Blender downloads can be extracted to any directory on the system, as
a self contained installation. Multiple Blender versions can easily
co-exist on the same system, and deployment can be automated using
standard file management tools.

New Blender versions may add, remove or changes functionality that
change the results of production files. For a given project, it is
advisable to use a single :abbr:`LTS (Long-Term-Support)` version
of Blender. LTS versions receive bug fixes for two years.

Working Offline
===============

For security or other reasons, workstation may not have internet access.

By default Blender does not access the internet, however this can be
enabled in the System preferences with the Online Access option.

Working offline can be enforced by running with the ``--offline-mode``
:ref:`command line argument <command-line-args-network-options>`. Users
will then be unable to enable online access in the preferences.

.. _deploying-blender-bundling:

Bundling Extensions
===================

When working offline or in a more controlled environment, it may be useful
to provide a set of extensions to all users. These can be served from a
read-only system repository. This repository could exist on a network drive
or in a system directory.

The location of this system extension repository can be manually configured
in the Extensions preferences.

The ``$BLENDER_SYSTEM_EXTENSIONS``
:ref:`environment variable <command-line-args-environment-variables>`
can also set the default location. This is a directory, within which a
``system`` directory should exist. Then extract extension packages there,
with a resulting path like this:

.. code-block:: bash

    $BLENDER_SYSTEM_EXTENSIONS/system/my-addon/blender_manifest.toml

Bundling Scripts
================

Besides extensions, it's possible to bundle scripts for presets,
application templates, legacy add-ons, as well as scripts run on startup.

Script directories can be manually added in the File Paths preferences.
The ``$BLENDER_SYSTEM_SCRIPTS`` can also be used to add a script directory
without modifying the preferences.

These script directories are expected to contain specific directories
like ``presets``, ``addons`` and ``startup`` for different types of
scripts. See :ref:`blender-directory-path-layout` for a complete list.

Startup Scripts
---------------

The Blender Python API can be used to customize Blender. This includes
changing preferences, changing the startup file and adding UI elements.

For example, a script can enable add-ons for every user.

.. code-block:: bash

    $BLENDER_SYSTEM_SCRIPTS/startup/enable_addons.py

.. code-block:: python

   def register():
       import addon_utils
       addon_utils.enable("my-addon")

   def unregister():
       pass

   if __name__ == "__main__":
       register()

VFX Platform
============

Blender follows the `VFX reference platform <https://vfxplatform.com>`_,
which means it is able to run on the same systems as other VFX software
and exchange image, volume and scene files with them.

Python Version
--------------

Blender and the `by module <https://pypi.org/project/bpy/>`_ are only compatible
with a single Python version. This makes it possible for add-ons and VFX software
in general to only have to target a single Python version.

Blender bundles a complete Python installation and does not interact with the
system Python by default. This can be changed with the ``--python-use-system-env``
:ref:`command line argument <command-line-args-python-options>`, if care is
taken to set up a compatible Python version.
