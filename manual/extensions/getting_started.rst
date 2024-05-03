.. index:: Extensions

.. Mark as "orphan" until extensions is out of beta.

:orphan:

.. Keep index link until this page is made public,
   so it's possible to navigate to other extensions pages.

:ref:`Extensions Index <extensions-index>`

************************
How to Create Extensions
************************

Creating an extension takes only a few steps:

#. Create a directory for your extension and populate it with the add-on code or theme file.
#. Add a `blender_manifest.toml <#manifest>`__  file with all the required meta-data ``(name, maintainer, ...)``.
#. Compress the directory as a ``.zip`` file.
#. :doc:`Install from Disk </editors/preferences/extensions>` to test if everything is working well.
#. `Upload the zip file <https://extensions.blender.org/submit/>`__ (this step requires Blender ID).

The extension will be held for `review <https://extensions.blender.org/approval-queue/>`__,
and published once the moderation team approves it.

Extension files
===============

An extension is shared as a ``.zip`` archive containing a manifest file and other files.
The expected files depend on the extension type.

Add-on extension
----------------

:doc:`Add-ons <addons>` need at least the manifest and an ``__init__.py`` file,
while more complex add-ons have a few different .py files or wheels together.

.. code-block:: text

   my_extension-0.0.1.zip
   ├─ __init__.py
   ├─ blender_manifest.toml
   └─ (...)

Theme extension
---------------

A theme extension only needs the manifest and the .xml theme file.

.. code-block:: text

   my_extension-0.0.1.zip
   ├─ blender_manifest.toml
   └─ theme.xml

.. note::

   Extensions can optionally have all its files inside a folder (inside the archive).
   This is a common behaviour when saving a repository as ZIP from version-control platforms.

Manifest
========

A manifest is a file with all the meta-data required for an extension to be processed.
This example is a good starting point to the ``blender_manifest.toml`` that should be inside the ``.zip``.

.. code-block:: toml

   schema_version = "1.0.0"

   # Example of manifest file for a Blender extension
   # Change the values according to your extension
   id = "my_example_extension"
   version = "1.0.0"
   name = "Test Extension"
   tagline = "This is another extension"
   maintainer = "Developer name <email@address.com>"
   # Supported types: "add-on", "theme"
   type = "add-on"

   # Optional: add-ons can list which resources they will require:
   # * "files" (for access of any filesystem operations)
   # * "network" (for internet access)
   # * "camera" (to capture photos and videos)
   # * "microphone" (to capture audio)
   # permissions = ["files", "network"]

   # Optional link to documentation, support, source files, etc
   # website = "http://extensions.blender.org/add-ons/my-example-package/"

   # Optional list defined by Blender and server, see:
   # https://docs.blender.org/manual/en/dev/extensions/tags.html
   tags = ["Animation", "Sequencer"]

   blender_version_min = "4.2.0"
   # Optional: maximum supported Blender version
   # blender_version_max = "5.1.0"

   # License conforming to https://spdx.org/licenses/ (use "SPDX: prefix)
   # https://docs.blender.org/manual/en/dev/extensions/licenses.html
   license = [
     "SPDX:GPL-2.0-or-later",
   ]
   # Optional: required by some licenses.
   # copyright = [
   #   "2002-2024 Developer Name",
   #   "1998 Company Name",
   # ]

Required values:

   :blender_version_min: Minimum supported Blender version - use at least ``4.2.0``.
   :id: Unique identifier for the extension.
   :license: List of :doc:`licenses <licenses>`, use `SPDX license identifier <https://spdx.org/licenses/>`__.
   :maintainer: Maintainer of the extension.
   :name: Complete name of the extension.
   :schema_version: Internal version of the file format - use ``1.0.0``.
   :tagline: One-line short description - cannot end with punctuation.
   :type: "add-on", "theme".
   :version: Version of the extension - must follow `semantic versioning <https://semver.org/>`__.

Optional values:

   :blender_version_max: Maximum version of Blender that can run this.
   :website: Website for the extension.
   :copyright: Some licenses require a copyright, copyrights must be "Year Name" or "Year-Year Name".
   :permissions: Add-ons can list which resources they require. The available options are
      ["files", "network", "camera", "microphone"].
   :tags: List of tags. See the :doc:`list of available tags <tags>`.

.. note::

   All the values present in the manifest file must be filled
   (i.e., cannot be empty, nor text ``""``, nor list ``[]``).

   If you don't want to set one of the optional values just exclude it from the manifest altogether.

Command-line
============

Extensions can be built, validated & installed via command-line.

.. note::

   Extension commands currently require a daily build of Blender with extensions enabled in the preferences.

To build the package defined in the current directory use the following commands:

.. code:: bash

   blender --command extension build

See :ref:`build <command-line-args-extension-build>` docs.

---

To validate the manifest without building the package:

.. code:: bash

   blender --command extension validate

You may also validate a package without having to extract it first.

.. code:: bash

   blender --command extension validate add-on-package.zip

See :ref:`validate <command-line-args-extension-validate>` docs.

.. seealso::

   :ref:`command_line-args-extensions`.



Third party extension sites
===========================

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
         "archive_url": "https://extensions.blender.org/add-ons/blender-kitsu/0.1.0/download/",
         "blender_version_min": "4.2.0",
         "maintainer": "Blender Studio",
         "tags": ["Pipeline"],
         "license": ["SPDX:GPL-3.0-or-later"],
         "website": "http://extensions.blender.org/add-ons/blender-kitsu/",
         "schema_version": "1.0.0"
      }
      ]
  }

Just like for the manifest file, the optional fields (e.g., ``blender_version_max``) are either to have a value
or should be omitted from the entries.

For the official Extensions Platform, the ``website`` value is the page of the extension in the online platform.
Even if the manifest points to the project specific website.

.. note::

   Any remote repository is expected to follow the latest `API <http://extensions.blender.org/api/swagger/>`__.
