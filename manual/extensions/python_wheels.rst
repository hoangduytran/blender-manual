
*************
Python Wheels
*************

.. TODO:

   - Guidelines for wheel selecting the version to use.
   - Finalize a policy for how conflicting versions of a wheel are handled.


`Python wheels <https://pythonwheels.com/>`__ (``*.whl``) are the standard way of distributing Python modules.
They are supported in Blender to make self-contained Python :doc:`Extensions </extensions/index>`.


Guidelines
==========

- By convention, always locate the files under ``./wheels/``.


Requirements
============

- Wheels must be bundled unmodified from `Python's package index <https://pypi.org>`__.
- Wheels must include their dependencies.
- Wheels filenames must match Python's binary distribution specification:
  `see docs <https://packaging.python.org/en/latest/specifications/binary-distribution-format/#file-name-convention>`__.
  *Wheels downloaded from Python's package index will follow this convention.*
- Use forward slashes as path separators when listing them on the `manifest </extensions/getting_started#manifest>`.


How to Bundle Wheels
====================

Python wheels  (``*.whl``) can be bundled using the following steps.

Downloading Wheels
   Download the wheel to the directory ``./wheels/``.

   For wheels that are platform independent this example downloads ``jsmin``:

   .. code-block:: console

      pip wheel jsmin -w ./wheels


   For wheels that contain binary compiled files, wheels for all supported platforms should be included:

   This example downloads ``pillow`` - the popular image manipulation module.

   .. code-block:: console

      pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64
      pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_28_x86_64
      pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64

   The available platform identifiers are listed on
   `pillow's download page <https://pypi.org/project/pillow/#files>`__.

Update the Manifest
   In ``blender_manifest.toml`` include the wheels as a list of paths, e.g.

   .. code-block:: toml

      wheels = [
         "./wheels/pillow-10.3.0-cp311-cp311-macosx_11_0_arm64.whl",
         "./wheels/pillow-10.3.0-cp311-cp311-manylinux_2_28_x86_64.whl",
         "./wheels/pillow-10.3.0-cp311-cp311-win_amd64.whl",
      ]

   Now installing the package will extract the wheel into the extensions own ``site-packages`` directory.

Running
   Once the extension has been installed you can check the module is being loaded by importing it in the
   Python console and printing it's location:

   .. code-block:: python

      import PIL
      print(PIL.__file__)
