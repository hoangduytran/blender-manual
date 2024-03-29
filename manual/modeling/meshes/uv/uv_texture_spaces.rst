
*******************
UVs & Texture Space
*******************

.. _uv-maps-panel:

UV Maps
=======

.. reference::

   :Mode:      All Modes
   :Panel:     :menuselection:`Properties --> Data --> UV Maps`

.. figure:: /images/modeling_meshes_uv_uv-texture-spaces_uv-maps.png

   The UV Maps panel in the Data tab.

If you have a mesh object selected, you'll find its UV maps in the Data tab of the
:doc:`Properties editor </editors/properties_editor>`. After selecting a map,
you can view and edit it in the :doc:`UV editor </editors/uv/introduction>`.

One mesh can have multiple UV maps (e.g. one map per texture), although it's
also possible to reuse a UV map for multiple textures.

Active Render
   Click the camera icon to make a certain UV map the default one for rendering.
   This will be the map that's used by the *UV* output of the
   :doc:`/render/shader_nodes/input/texture_coordinate`.
   You can use the :doc:`/render/shader_nodes/input/uv_map` to access any other maps.

Add ``+``
   Duplicates the selected UV map, or creates a new one if the list is empty.

Remove ``-``
   Removes the selected UV map.


.. _bpy.types.*texspace:
.. _bpy.types.Mesh.texture_mesh:
.. _bpy.ops.curve.match_texture_space:
.. _properties-texture-space:

Texture Space
=============

.. reference::

   :Mode:      All Modes
   :Panel:     :menuselection:`Properties --> Data --> Texture Space`

This panel lets you configure the object's :term:`Texture Space`, which is a 3D box
used for generating texture coordinates without the use of a UV map.
You can visualize the texture space using the option in the
:doc:`/scene_layout/object/properties/display` panel.

Auto Texture Space
   Calculates the texture space automatically.

   Location, Size
      Lets you define the texture space manually, relative to the object.
      Note that you can also edit it in the 3D Viewport -- see `Editing`_ below.

Texture Mesh :guilabel:`Mesh objects`
   Use another mesh for texture indices. The vertices of the two objects must be perfectly aligned
   or the UV map will be distorted.

Match Texture Space :guilabel:`Curve objects`
   Modifies the *Location* and *Size* to match the object's bounding box.
   This disables Auto Texture Space.

   .. is Match Texture Space the same thing as Auto Texture Space?


.. _properties-texture-space-editing:

Editing
-------

.. reference::

   :Mode:      Object Mode and Edit Mode
   :Menu:      :menuselection:`Object --> Transform --> Move/Scale Texture Space`

Click one of these menu items, then move the mouse to adjust the texture space
and press :kbd:`LMB` to confirm. While transforming, you can use keyboard shortcuts to lock
certain axes; see the status bar.


Accessing
---------

When setting up a material shader, you can use the *Generated* output of the
:doc:`/render/shader_nodes/input/texture_coordinate` to read the 3D coordinate
inside the object's texture space. You can then pass this coordinate to a texture
node.

.. tip::

   Texture spaces do not have rotation support. You can use a
   :doc:`/render/shader_nodes/vector/mapping` to manually rotate the coordinate
   in the material shader instead.
