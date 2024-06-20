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
