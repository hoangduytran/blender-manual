.. _bpy.types.UserAssetLibrary:

***************
Asset Libraries
***************

Name and on-drive directory paths of asset libraries.
To make Blender aware of an asset library, add it to this list.
The name is for your reference only, and will appear in asset library selectors.
The path should point to the location of the asset library.

.. figure:: /images/asset_browser-asset_library_preferences.png

   Name and Location of asset libraries in the Preferences.

To create a new asset library, just create an empty directory and add it to the :ref:`ui-list-view`.
Any asset from any blend-file contained in that directory
(or subdirectories thereof) will appear in the :doc:`/editors/asset_browser`.

.. _bpy.types.UserAssetLibrary.import_method:

Import Method
   Determines how data is managed when an asset is imported,
   unless overridden by the :ref:`Asset Browser <bpy.types.FileAssetSelectParams.import_method>`.

   :ref:`Link <bpy.ops.wm.link>`
      The asset will be linked to the current blend-file, and thus be read-only.
      Later changes to the asset file will be reflected in all files that link it in.

      *Note, *Link* is not supported for online asset libraries.*
   :ref:`Append <bpy.ops.wm.append>`
      The asset and all its dependencies will be appended to the current file.
      Dragging a material into the scene three times will result in three independent copies.
      Dragging an object into the scene three times will also result in three independent copies.

      "Dependencies" in this case means everything the asset refers to.
      For an object, this can be its mesh and materials, but also other objects
      used by modifiers, constraints, or drivers.

      Since the file now has its own copy of the asset, later changes to
      the asset file will not be reflected in the file it's appended to.
   Append (Reuse Data)
      *Specific to the Asset Browser*.

      The first time an asset is used, it will be appended, including its dependencies,
      just like described previously. However, Blender will keep track of where it originated,
      and the next time the asset is used, as much data as possible will be reused.
      Dragging a material into the scene three times will only load it once,
      and just assign the same material three times.
      Dragging an object into the scene three times will create three copies of the object,
      but all copies will share their mesh data, materials, etc.

      Since the file now has its own copy of the asset, later changes to
      the asset file will not be reflected in the file it's appended to.
   Pack
      Imports the asset as *linked* data and immediately packs it into the current blend-file.
      This ensures that the asset remains available even if the original library data is modified
      or becomes unavailable.

      Useful for maintaining self-contained files that do not rely on external asset library paths.

.. _bpy.types.UserAssetLibrary.use_relative_path:

Relative Path
   Use relative path when linking assets from this asset library.
