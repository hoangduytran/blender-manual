.. _extensions-create_repo-static:

***************************************
Creating a Static Extensions Repository
***************************************

To host your own extensions and leverage Blender update system all that is required is a static JSON file on a server,
pointing towards download links for the extensions.


JSON
====

To generate a valid JSON file you can use the command-line tool:

.. code:: bash

   blender --command extension server-generate --repo-dir=/path/to/packages

This creates an ``index.json`` listing from all the packages found in the specified location.

See :ref:`server-generate <command-line-args-extension-server-generate>` docs.

The generated JSON is aligned with the `API <https://developer.blender.org/docs/features/extensions/api_listing/>`__.


Testing
-------

To test the generated repository, create a new "Remote" repository from the user preferences:

- **Extensions -> Repositories -> [+] -> Add Remote Repository**
- In the **URL** paste the location of the generated JSON.
  So the example ``/path/to/packages`` would use the:

  - ``file:///path/to/packages/index.json`` on Linux/macOS.
  - ``file:///C:/path/to/packages/index.json`` on MS-Windows.
  - ``file://HOST/share/path/to/packages/index.json`` network shares on MS-Windows.

  You may wish to use a web browser to navigate to the file-system location and copy that URL into Blender.


HTML
====

The ``server-generate`` command can optionally create a simple website using the ``--html`` argument.
which can be used
to view extensions online, the links can dropped into Blender for installation.


For a sample of the HTML code you can use to list all the extensions in the repository, use the ``html`` option
when generating the server.

.. code:: bash

   blender --command extension server-generate --repo-dir=/path/to/packages --html

This creates an ``index.html`` file with all the extra URLs parameters ready to use.


Download Links
--------------

In order to support drag and drop for installing from a remote repository,
there are a few optional ways to prepare the URLs.

The only strict requirement is that the download URL must end in ``.zip``.

You can pass different arguments to the URL to give more clues to Blender about what to do with the dragged URL.

   :repository:
      Link to the JSON file to be used to install the repository on Blender.
      It supports relative URLs.
   :platforms:
      Comma-separated list of supported platforms.
      If omitted, the extension will be available in all operating systems.
   :blender_version_min:
      Minimum supported Blender version.
   :blender_version_max:
      Blender version that the extension does not support, earlier versions are supported.


.. tip::

   The more details you provide, the better the user experience.

With the exception of the ``repository``, all the other parameters can be extracted from the extensions manifest.
Those arguments are to be encoded as part of the URL.

Expected format:
   ``<URL>.zip?repository=<repository>&blender_version_min=<version_min>&blender_max=
   <version_max_exclusive>&platforms=<platform1,platform2,...>``

Example:
   ``https://extensions.blender.org/add-ons/amaranth-toolset/1.0.23/download/add-on-amaranth-toolset-v1.0.23.zip?repository=%2Fapi%2Fv1%2Fextensions%2F&blender_version_min=4.2.0&platforms=linux-x64%2Cmacos-x64``

   .. note::

      ``%2F`` and ``%2C`` are simply the url-encoded equivalent of ``/`` and ``,`` respectively.
