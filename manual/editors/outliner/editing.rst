
*******
Editing
*******

.. _editors-outliner-editing-context_menu:

Context Menu
============

Show the context menu for a data-block with :kbd:`RMB` on the icon or name.
Depending on the type of the preselected data-block(s), you will have all or part of the following options:

Copy/Paste
   Copy/pastes selected data-blocks.
Delete
   Deletes the selected data-block.
Select, Select Hierarchy, Deselect
   Add object to current selection without making it the active one.


.. _editors-outliner-editing-collections:

Collections
-----------

Collections are a way Blender uses to organize scenes.
Collections contain objects and everything else in a scene.
They can include collections themselves and are fully recursive.

.. seealso::

   Read more about :doc:`Collections </scene_layout/collections/index>`.

New
   Creates a new collection.
Duplicate Collections
   Recursively duplicates the collection including all child collections, objects, and object data.
Duplicate Linked
   Duplicate entire hierarchy keeping content linked with original.
Delete Hierarchy
   Deletes the collection and removes all its child objects or collections.
   It is important to note that this only deletes the collection,
   if child objects are part of another collection they will stay in the scene collection
   and their data-blocks will not be deleted from the blend-file.
Instance to Scene
   Creates a new :doc:`collection instance </scene_layout/object/properties/instancing/collection>`.
Visibility
   Isolate
      Hides all collections except the selected collection and any parent collections (if any exist).
   Show/Hide
      Shows/Hides the selected collection from the :doc:`View Layer </scene_layout/view_layers/index>`.
   Show/Hide Inside
      Shows/Hides all items that are a member of the selected collection, include child collections,
      from the :doc:`View Layer </scene_layout/view_layers/index>`.
   Enable/Disable in Viewports
      Enables/disables drawing in the :doc:`View Layer </scene_layout/view_layers/index>`.
   Enable/Disable in Renders
      Enables/disables visibility of the collection in renders.
View Layer
   Disable/Enable in View Layer
      Disables/Enables the collection from the view layer.


.. _bpy.ops.outliner.id_operation:

ID Data Menu
------------

Unlink
   To unlink a data-block from its "owner" (e.g. a material from its mesh).
Make Local
   To create a "local" duplicate of this data-block.
Make Single User
   This feature is not yet implemented.
Delete
   Deletes the selected data-block.
Add Library Override
   Add a local :doc:`override </files/linked_libraries/library_overrides>` of this linked data-block.
Add Library Override Hierarchy
   Add a local :doc:`override </files/linked_libraries/library_overrides>` of this linked data-block,
   and its hierarchy of dependencies.
Reset Library Override
   Reset this local :doc:`override </files/linked_libraries/library_overrides>` to its linked values.
Reset Library Override Hierarchy
   Reset this local :doc:`override </files/linked_libraries/library_overrides>` to its linked values,
   as well as its hierarchy of dependencies.
Remap Users
   Remap Users of a data-block to another one (of same type of course).
   This means you can e.g. replace all usages of a material or texture by another one.
Copy/Paste
   Copy/pastes selected data-blocks.
Add Fake User, Clear Fake User
   Adds a "dummy" (fake) user so that the selected data-block always gets saved even if it has no users.
   The fake user can be removed with *Clear Fake User*.
Rename :kbd:`F2`
   Renames the selected data-block.
Select Linked
   Selects the linked data, see :ref:`bpy.ops.object.select_linked` for more information.


View Menu
---------

The view menu is part of the context menu and supported in all the Outliner elements.

Show Active :kbd:`Period`
   Centers the Tree View to selected object.
Show Hierarchy :kbd:`Home`
   To collapse all levels of the tree.
Show/Hide One Level :kbd:`NumpadPlus`/ :kbd:`NumpadMinus`
   Expand one level down in the tree or collapse one level using the keyboard shortcuts.

.. note::

   Some data-block types will not have a context menu at all!
