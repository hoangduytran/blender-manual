.. index:: Editors; Properties
.. _bpy.types.SpaceProperties:

*****************
Properties Editor
*****************

.. figure:: /images/editors_properties-editor_interface.png
   :align: right

   The Properties editor.

The Properties editor shows, and lets you edit, the properties of the active scene, object, material, and so on.


Tabs
====

The properties are grouped into tabs (the vertical list of icons on the left) which are described below.

.. _properties-tool-tab:

Active Tool and Workspace Settings
----------------------------------

This first tab contains settings for the active :doc:`tool </editors/3dview/toolbar/index>` (in the 3D Viewport)
and the current :doc:`workspace </interface/window_system/workspaces>`.


Scene
-----

These tabs contain settings for the active scene.

.. _properties-render-tab:

- Render: :doc:`EEVEE </render/eevee/index>`,
  :doc:`Cycles </render/cycles/render_settings/index>` or
  :doc:`Workbench </render/workbench/index>` settings
- :doc:`Output </render/output/index>`
- :doc:`View Layer </scene_layout/view_layers/index>`
- :doc:`Scene </scene_layout/scene/properties>`
- :doc:`World </render/lights/world>`


Collection
----------

This tab contains settings for the active :ref:`Collection <scene-layout_collections_collections_tab>`.


.. _properties-data-tabs:

Object
------

These tabs are related to the active object. Some of them are only visible for certain types of objects.

- :doc:`Object </scene_layout/object/properties/index>`
- :doc:`Modifiers </modeling/modifiers/index>` (or :doc:`Grease Pencil Modifiers </grease_pencil/modifiers/index>`)
- :doc:`Effects </grease_pencil/visual_effects/index>`
- :doc:`Particles </physics/particles/index>`
- :doc:`Physics </physics/index>`
- :doc:`Object Constraints </animation/constraints/index>`


Object Data
-----------

The main tab of this category (often the only one) always has the same name, *Object Data*,
but its icon will change based on the type of the object.


.. rubric:: Geometry Objects:

- :doc:`Mesh </modeling/meshes/properties/object_data>`
- :doc:`Curve </modeling/curves/properties/index>`
- :doc:`Surface </modeling/surfaces/properties/index>`
- :doc:`Text </modeling/texts/properties>`
- :doc:`Metaball </modeling/metas/properties>`
- :doc:`Grease Pencil </grease_pencil/properties/index>`


.. rubric:: Rigging and Deformation Objects:

- :doc:`Armature </animation/armatures/properties/index>`

  - :doc:`Bone </animation/armatures/bones/properties/index>`
  - :doc:`Bone Constraints </animation/armatures/posing/bone_constraints/index>`

- :doc:`Lattice </animation/lattice>`


.. rubric:: Other Types of Objects:

- :doc:`Empty </modeling/empties>`
- :doc:`Speaker </render/output/audio/speaker>`
- :doc:`Camera </render/cameras>`
- :doc:`Light </render/lights/light_object>`
- :doc:`Light Probe </render/eevee/light_probes/index>`


Object Shading
--------------

Tabs related to the appearance of the active object. Only visible for certain types of objects.

- :doc:`Material </render/materials/index>`
- :doc:`Texture </render/materials/legacy_textures/index>`


Header
======

.. figure:: /images/editors_properties-editor_top.png

   The header of the Properties editor.

.. _bpy.types.SpaceProperties.search_filter:

Display Filter :kbd:`Ctrl-F`
   Lets you search for a property by typing its name. The editor jumps to the first result and grays out
   all the properties and tabs that don't match the search term.

   You can start a search with :kbd:`Ctrl-F` and clear it with :kbd:`Alt-F`.

Data Context
   Below the filter textbox, the editor shows the icon and name of the item whose properties it's displaying.
   In the example above, it's displaying the properties of the material "Black" which is used by the object "Suzanne".

.. _bpy.ops.buttons.toggle_pin:

Toggle Pin ID
   You can click the pin icon to "lock in" the current item and keep displaying its properties regardless
   of the selection in the 3D Viewport/Outliner. Click again to unlock.


Options
-------

These options are accessible through the dropdown button in the top right corner of the editor.

.. _bpy.types.SpaceProperties.outliner_sync:

Sync with Outliner
   Whether to switch to the relevant tab when clicking an icon (not a name) in the
   :doc:`Outliner </editors/outliner/introduction>`.


.. _bpy.types.SpaceProperties.show_properties:

Visible Tabs
   Allows hiding specific tabs in the Properties editor.

   This is especially useful for tailoring the editor to specific workflows. For example:
   - In the *Video Editing* workspace, you may hide object and shading tabs to reduce clutter.
   - In the *Modeling* workspace, you may hide strip-related tabs that are not relevant.

   Hidden tabs can be restored at any time using this filter list.
