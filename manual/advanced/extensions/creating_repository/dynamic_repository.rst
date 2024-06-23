****************************************
Creating a Dynamic Extensions Repository
****************************************

If you plan to setup a dynamic extensions repository, read first about :doc:`static repositories <static_repository>`.
The expected format for how to list all the packages is the same, and should be used as a starting point.

Multiple Versions
=================

When Blender fetches the extensions listing it passes the following arguments to make sure only
compatible extensions are listed:

- ``platform``
- ``blender_version``

This means that servers have the chance to handle these arguments to output a single entry per-extension on the listing.

These arguments are passed as parameters to the server via a query URL:

   :URL: ``https://extensions.blender.org/api/v1/extensions/``
   :query URL: ``https://extensions.blender.org/api/v1/extensions/?blender_version=4.2.0&platform=linux-x64``


Access Token
============

Some repositories may require authentication. The user can specify an ``access token`` for a repository,
which is passed along with the API request from Blender.

This is passed to the servers via an Authorization header:

.. code-block:: sh

  curl -i https://extensions.blender.org/api/v1/extensions/ \
    -H "Accept: application/json" \
    -H "Authorization: Bearer abc29832befb92983423abcaef93001"
