*********************************
Creating an Extensions Repository
*********************************

Third party sites that wish to support extensions in Blender can do so in two ways:

#. Fork the entire `Extensions Website <https://projects.blender.org/infrastructure/extensions-website>`__
   as a start point; or
#. Host a JSON file listing all the packages of your repository.

To generate a valid JSON file you can use the command-line tool:

.. code:: bash

   blender --command extension server-generate --repo-dir=/path/to/packages

This creates a listing from all the packages found in the specified location.

See :ref:`server-generate <command-line-args-extension-server-generate>` docs.

Example of what the JSON is expected to look like:

.. code:: json

   {
     "version": "v1",
     "blocklist": [],
     "data": [
      {
         "id": "blender_kitsu",
         "name": "Blender Kitsu",
         "tagline": "Pipeline management for projects collaboration",
         "version": "0.1.5-alpha+f52258de",
         "type": "add-on",
         "archive_size": 856650,
         "archive_hash": "sha256:3d2972a6f6482e3c502273434ca53eec0c5ab3dae628b55c101c95a4bc4e15b2",
         "archive_url": "https://extensions.blender.org/add-ons/blender-kitsu/0.1.5-alpha+f52258de/download/",
         "blender_version_min": "4.2.0",
         "maintainer": "Blender Studio",
         "tags": ["Pipeline"],
         "license": ["SPDX:GPL-3.0-or-later"],
         "website": "https://extensions.blender.org/add-ons/blender-kitsu/",
         "schema_version": "1.0.0"
      }
      ]
  }

Just like for the manifest file, the optional fields (e.g., ``blender_version_max``) are either to have a value
or should be omitted from the entries.

For the official Extensions Platform, the ``website`` value is the page of the extension in the online platform.
Even if the manifest points to the project specific website.

.. note::

   Any remote repository is expected to follow the latest `API <https://extensions.blender.org/api/swagger/>`__.


Multiple Versions
=================

When Blender fetches the extensions listing it passes the following arguments to make sure only compatible extensions are listed:

* ``platform``
* ``blender_version``

This means that servers which can handle these arguments will have a single entry per-extension on the listing.

For static generated JSONs this is not supported. Instead, the JSON generated with the
:ref:`server-generate <command-line-args-extension-server-generate>` command will display all
available versions for all the unique combinations of platforms.


Download Links
==============

In order to support drag and drop for installing from a remote repository, there are a few optional ways to prepare the URLs.

The only strict requirement is that the download URL must end in ``.zip``.

You can pass different arguments to the URL to give more clues to Blender about what to do with the dragged URL.

   :repository: Link to the JSON file to be used to install the repository on Blender. It supports relative URLs.
   :platforms: Comma-separated list of supported platforms. If omitted, the extension will be available in all operating systems.
   :blender_version_min: Minimum supported Blender version.
   :blender_version_max: Blender version that the extension does not support, earlier versions are supported.


.. tip::

   The more details you provide, the better the user experience.

With the exception of the ``repository``, all the other parameters can be extracted from the extensions manifest.
Those arguments are to be encoded as part of the URL.

Expected format:
   ``<URL>.zip?repository=<repository>&blender_version_min=<version_min>&blender_max=<version_max_exclusive>&platforms=<platform1,platform2,...>``

Example:
   ``https://extensions.blender.org/add-ons/amaranth-toolset/1.0.23/download/add-on-amaranth-toolset-v1.0.23.zip?repository=/api/v1/extensions/&blender_version_min=4.2.0&platforms=linux-x64,macos-x64``


HTML Example
------------

For a sample of the HTML code you can use to list all the extensions in the repository, use the ``html`` option
when generating the server.

.. code:: bash

   blender --command extension server-generate --repo-dir=/path/to/packages --html

This creates a ``download.html`` file with all the extra URLs parameters ready to use.

Tags and Translations
=====================

If you are planning to use a different set of :doc:`tags <tags>` than the ones used by Blender Extensions Platform,
remember to submit a pull request to `tags.py <https://projects.blender.org/blender/blender/src/scripts/modules/_bpy_internal/extensions/tags.py>`__.

This way they can be shown translated within Blender.