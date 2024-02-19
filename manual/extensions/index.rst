.. index:: Extensions

#############
  Extensions
#############

.. important::

   This feature is only available experimentally in `daily builds <https://builder.blender.org/download/daily/>`__ of
   `Blender 4.2 <https://projects.blender.org/blender/blender/milestone/19>`__.
   Please enable "Extensions" on the :doc:`Experimental Preferences </editors/preferences/experimental>` to help testing it.

Extensions are **add-ons** or **themes** used to extend the core functionality of Blender.
They are shared in online platforms, and can be installed and updated from within Blender.

The official extensions platform for the Blender project is `extensions.blender.org <https://extensions.blender.org>`__.
Other third party sites can also be supported, as long as they follow the Extensions Platform specification.

.. seealso::

  For the extension settings, and how to manage them, refer to the
  :doc:`User Preferences </editors/preferences/extensions>`.

How to create extensions
========================

1. Create a `blender_manifest.toml <#manifest>`__  file with all the required meta-data `(name, maintainer, ...)`.

2. Create a .zip file with the manifest file together with your `extension files <#extension-files>`__.

3. `Upload your extension <https://extensions.blender.org/submit/>`__ `(this step requires you to login to your Blender ID account)`.

The extension will be help for review, and published once the moderation team approves it.

Extension files
===============

An extension is shared as a .zip archive containing a manifest file and other files.
The expected files depend on the extension type.

Add-on extension
++++++++++++++++

Add-ons need at least the manifest and an __init__.py file, while more complex add-ons have a few different .py files or wheels together.

.. code-block:: text

  my_extension-0.0.1.zip
  ├─ __init__.py
  ├─ blender_manifest.toml
  └─ (...)

Theme extension
+++++++++++++++

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
This example is a good start point to the `blender_manifest.toml` that should be inside the .zip.

  .. code-block:: toml

    schema_version = "1.0.0"

    # Example of manifest file for a Blender extension
    # Change the values according to your extension
    id = "my_example_extension"
    version = "1.0.0"
    name = "Test Extension"
    tagline = "This is another extension."
    description = "Where to access the add-on, basic usage."
    # Supported types: "add-on", "theme"
    type = "add-on"

    # Optional: add-ons can list which resources they will require:
    # * "files" (for access of any filesystem operations)
    # * "network" (for internet access)
    permissions = ["files", "network"]

    # Optional link to documentation, support, source files, etc
    # website = "http://extensions.blender.org/add-ons/my-example-package/"

    # List defined by Blender and server, see:
    # https://docs.blender.org/manual/en/4.1/extensions/tags.html
    tags = ["Modeling", "UV", "Motion Capture"]

    blender_version_min = "4.1.0"
    # Optional: maximum supported Blender version
    # blender_version_max = "5.1.0"

    maintainer = "Developer name <email@address.com>"
    # License conforming to https://spdx.org/is suppose to dolicenses/
    # use "SPDX: prefix.
    license = [
      "SPDX:GPL-2.0-or-later",
    ]
    # Optional: required by some licenses.
    copyright = [
      "2002-2024 Developer Name",
      "1998 Company Name",
    ]

Required values:
 * ``blender_version_min``: Minimum supported Blender version.
 * ``description``: What it does, how to use, where to access it (in case of add-ons).
 * ``id``: Unique identifier for the extension.
 * ``license``: `SPDX license identifier <https://spdx.org/licenses/>`__ - note the official Blender Extensions platform only support free and open licensed extensions.
 * ``maintainer``: Maintainer of the extension.
 * ``name``: Complete name of the extension.
 * ``schema_version``: Internal version of the file format - use 1.0.0.
 * ``tagline``: One-line short description.
 * ``tags``: List of tags.
 * ``type``: "add-on", "theme".
 * ``version``: Version of the extension - must follow `semantic versioning <https://semver.org/>`__.

Optional values:
 * ``website``: Website for the extension.
 * ``copyright``: Some licenses require a copyright, copyrights must be "Year Name" or "Year-Year Name".
 * ``blender_version_max``: Maximum version of Blender that can run this.
 * ``permissions``: Add-ons can list which resources they require. The available options are ["files", "network"].

 ..
    Command-line
    ============

     There are a few tools accessible via command-line that can help the creation of extensions.

    .. code:: bash

      ./blender.exe tools.extension validate-manifest <blender_manifest.toml>
      ./blender.exe tools.extension create <folder-name-with-manifest/>


Third party extension sites
===========================

Third party sites that wish to support extensions in Blender can do so by two ways:

  1. Fork the entire `Extensions Website <https://projects.blender.org/infrastructure/extensions-website>`__ as a start point; or
  2. Host a JSON file listing all the packages of your repository.

.. To generate a valid JSON file you can use the command-line tool:

.. .. code:: bash

..   ./blender.exe tools.extension server-generate

.. This creates a listing from all the .zip packages that it can find in the specified location.
Example of how the JSON is expected to look like:

.. code:: json

  {"blender_kitsu": {
    "id": "1",
    "name": "Blender Kitsu",
    "tagline": "Pipeline management for projects collaboration",
    "version": "0.1.5-alpha+f52258de",
    "type": "add-on",
    "archive_size": 856650,
    "archive_hash": "sha256:3d2972a6f6482e3c502273434ca53eec0c5ab3dae628b55c101c95a4bc4e15b2",
    "archive_url": "http://extensions.blender.org/media/files/ed/ed656b177b01999e6fcd0e37c34ced471ef88c89db578f337e40958553dca5d2.zip",
    "blender_version_min": "4.2.0",
    "maintainer": "Blender Studio",
    "tags": ["Pipeline"],
    "license": ["SPDX:GPL-3.0-or-later"],
    "website": "http://extensions.blender.org/add-ons/blender-kitsu/",
    "schema_version": "1.0.0"
  }}

Optional fields (e.g., blender_version_max) are to be emmitted from the entries.

For the official Extensions Platform, the `website` value is the page of the extension in the online platform. Even if the manifest points to the project specific website.

.. note::

  Any remote repository is expected to follow the latest `API <http://extensions.blender.org/api/swagger/>`__.
