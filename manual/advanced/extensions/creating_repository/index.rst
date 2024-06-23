*********************************
Creating an Extensions Repository
*********************************

Third party sites that wish to support extensions in Blender can do so in two ways:

#. Fork the entire `Extensions Website <https://projects.blender.org/infrastructure/extensions-website>`__
   as a start point; or
#. Host a :doc:`JSON file <static_repository>` listing all the packages of your repository; or
#. Serve the JSON file :doc:`dynamically <dynamic_repository>`.

Repository Types
================

.. toctree::
   :maxdepth: 1

   Static Repository <static_repository.rst>
   Dynamic Repository <dynamic_repository.rst>

Tags and Translations
=====================

If you are planning to use a different set of :doc:`tags <../tags>` than the ones used by Blender Extensions Platform,
remember to submit a pull request to
`tags.py <https://projects.blender.org/blender/blender/src/scripts/modules/_bpy_internal/extensions/tags.py>`__.

This way they can be shown translated within Blender.
