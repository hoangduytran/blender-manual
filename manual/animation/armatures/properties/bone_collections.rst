.. _bpy.types.BoneGroups:
.. _bpy.types.BoneCollection:

****************
Bone Collections
****************

.. note::

   Bone Collections were introduced in Blender 4.0 as replacement of Armature
   Layers and Bone Groups. :ref:`Bone colors <bpy.types.Bone.color>` are now
   managed directly on the bone.


.. reference::

   :Mode:      Pose & Armature Edit Modes
   :Panel:     :menuselection:`Properties --> Armature --> Bone Collections`
   :Menu:      :menuselection:`Pose --> Bone Collections --> ...`

.. figure:: /images/animation_armatures_properties_bonecollections_panel.png

   The Bone Collections panel in the Armature properties.

This panel contains the Bone Collection :ref:`List view <ui-list-view>`, which
allows the creation, deletion, and editing of Bone Collections.

.. tip::

   The Bone Properties panel gives a slightly different view on the bone's collections. See
   :doc:`Bone Relations </animation/armatures/bones/properties/relations>`.

Assign & Select
===============

.. _bpy.ops.armature.collection_assign:

Assign
   Assigns the selected bones to the active bone collection.

.. _bpy.ops.armature.collection_unassign:

Remove
   Removes the selected bones from the active bone collection.

.. _bpy.ops.armature.collection_select:

Select
   Selects the bones in the active bone collection.

.. _bpy.ops.armature.collection_deselect:

Deselect
   Deselects the bones in the active bone collection.

.. note::

   Individual bones can als be unassigned from their collections via the
   :ref:`Bone Relations panel <bpy.types.PoseBone.collections>`.

.. tip::

   For setting up custom selection sets of bones, take a look at the *Selection
   Sets* add-on. It is bundled with Blender.

.. _moving_bones_between_collections:

Moving Bones between Collections
================================

Blender should be in *Edit Mode* or *Pose Mode* to move bones between collections.
Note that as with objects, bones can be assigned to in several collections at once.

Move to Collection
   Shows a list of the Armature's *editable* bone collections. Choosing a bone
   collection unassign the selected bones from all other bone collections, then
   assigns them to the chosen one.

   Available as :menuselection:`Pose --> Move to Collection` (*Pose Mode*)
   :menuselection:`Armature --> Move to Collection` (*Edit Mode*), and :kbd:`M` (either mode).

Bone Collections
   Shows a list of the Armature's *editable* bone collections. The collections
   that the active bone is assigned to are prefixed with a `-`, and choosing
   those will unassign all selected bones from that collection. Similarly,
   choosing a bone collection prefixed with a `+` will assign all selected bones
   to that collection.

   Available as :menuselection:`Pose --> Bone Collections` (*Pose Mode*)
   :menuselection:`Armature --> Bone Collections` (*Edit Mode*), and :kbd:`Shift+M` (either mode).

.. note::

   The above operators will only show the *editable* bone collections. When the
   Armature is linked, its bone collections will be *read-only*. New bone
   collections can still be added via library overrides; only those will be
   editable.

   See :ref:`Library Overrides of Bone Collections <bone_collections_library_overrides>`.
