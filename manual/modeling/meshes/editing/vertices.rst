
************
Vertex Tools
************

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex`
   :Hotkey:    :kbd:`Ctrl-V`

This page covers many of the tools in the *Vertex* menu.
These are tools that work primarily on vertex selections
but some also work with edge or face selections.


Extrude Vertices
================

Todo.


Bevel Vertices
==============

Todo.


New Edge/Face from Vertices
===========================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> New Edge/Face from Vertices`
   :Hotkey:    :kbd:`F`

It will create an edge or some faces, depending on your selection.

See also :doc:`Creating Geometry </modeling/meshes/editing/basics/make_face_edge>`.


Connect Vertex Path
===================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Mesh --> Vertices --> Connect Vertex Path`
   :Hotkey:    :kbd:`J`

This tool connects vertices in the order they are selected, splitting the faces between them.

When there are only two vertices selected, a cut will be made across unselected faces,
a little like the Knife tool; however, this is limited to straight cuts across connected faces.

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_pair-before.png

          Two disconnected vertices.

     - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_pair-after.png

          Result of connecting.

Running a second time will connect the first/last endpoints.

When many vertices are selected, faces will be split by their selected vertices.

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_multi-before.png

          Before.

     - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_multi-after.png

          After.

Vertices not connected to any faces will create edges,
so this can be used as a way to quickly connect isolated vertices too.


Connect Vertices Pairs
======================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Mesh --> Vertices --> Connect Vertices`

This tool connects selected vertices by creating edges between them and splitting the face.

This tool can be used on many faces at once.

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_before.png
          :width: 180px

          Vertices before connecting.

     - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_after.png
          :width: 180px

          After connecting vertices.

     - .. figure:: /images/modeling_meshes_editing_subdividing_vertex-connect_after-faces.png
          :width: 180px

          Resulting face pair.

The main difference between this tool and `Connect Vertex Path`_
is this tool ignores selection order and connects all selected vertices that share a face.


.. _tool-mesh-rip_region:

Rip Vertices
============

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Rip Vertices`
   :Hotkey:    :kbd:`V`

Rip creates a "hole" in the mesh by making a copy of selected vertices and edges,
still linked to the neighboring non-selected vertices,
so that the new edges are borders of the faces on one side, and the old ones,
borders of the faces on the other side of the rip.


Examples
--------

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_vertices_rip-before.png
          :width: 260px

          Selected vertex.

     - .. figure:: /images/modeling_meshes_editing_vertices_rip-after.png
          :width: 260px

          Hole created after using rip on vertex.

   * - .. figure:: /images/modeling_meshes_editing_vertices_rip-edges-before.png
          :width: 260px

          Edges selected.

     - .. figure:: /images/modeling_meshes_editing_vertices_rip-edges-after.png
          :width: 260px

          Result of rip with edge selection.

   * - .. figure:: /images/modeling_meshes_editing_vertices_rip-complexselection-before.png
          :width: 260px

          A complex selection of vertices.

     - .. figure:: /images/modeling_meshes_editing_vertices_rip-complexselection-after.png
          :width: 260px

          Result of rip operation.


Limitations
-----------

Rip will only work when edges and/or vertices are selected.
Using the tool when a face is selected (explicitly or implicitly), will return an error
message *"Cannot perform ripping with faces selected this way"*.
If your selection includes some edges or vertices that are not "between" two faces :term:`manifold`,
it will also fail with the message *"No proper selection or faces include"*.


Rip Vertices and Fill
=====================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Rip Vertices and Fill`
   :Hotkey:    :kbd:`Alt-V`

Rip fill works the same as the Rip tool above, but instead of leaving a hole,
it fills in the gap with geometry.

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_vertices_rip-edges-before.png
          :width: 260px

          Edges selected.

     - .. figure:: /images/modeling_meshes_editing_vertices_rip-fill-result.png
          :width: 260px

          Result of rip fill.


.. _tool-mesh-rip_edge:

Rip Vertices and Extend
=======================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Rip Vertices and Extend`
   :Hotkey:    :kbd:`Alt-D`

This tool takes any number of selected vertices and duplicate-drags them along the closest edge to the mouse,
When extending an edge loop, it extends the vertices at the endpoints of the loop.
The behavior is similar to the *Extrude* tool, but it creates an n-gon.

It helps to easily add details to existing edges.


.. _bpy.ops.transform.vert_slide:
.. _tool-mesh-vertex-slide:

Slide Vertices
==============

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Slide Vertices`
   :Hotkey:    :kbd:`Shift-V`

Vertex Slide will transform a vertex along one of its adjacent edges.
Use :kbd:`Shift-V` to activate tool.
The nearest selected vertex to the mouse cursor will be the control one.
Move the mouse along the direction of the desired edge to specify the vertex position.
Then press :kbd:`LMB` to confirm the transformation.

Even :kbd:`E`
   By default, the offset value of the vertices is a percentage of the edges length along which they move.
   When Even mode is active, the vertices are shifted by an absolute value.
Flipped :kbd:`F`
   When Flipped is active, vertices move the same distance from adjacent vertices,
   instead of moving from their original position.
Clamp :kbd:`Alt` or :kbd:`C`
   Toggle clamping the slide within the edge extents.

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_vertices_vertex-slide1.png
          :width: 200px

          Selected vertex.

     - .. figure:: /images/modeling_meshes_editing_vertices_vertex-slide2.png
          :width: 200px

          Positioning vertex interactively.

     - .. figure:: /images/modeling_meshes_editing_vertices_vertex-slide3.png
          :width: 200px

          Repositioned vertex.


Smooth Vertices
===============

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Smooth Vertices`,
               :menuselection:`Context Menu --> Smooth`

This will apply the :doc:`Smooth Tool </modeling/meshes/editing/transform/smooth>` once.


.. _modeling-meshes-editing-vertices-shape-keys:

Blend From Shape
================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Blend From Shape` and
               :menuselection:`Vertex --> Shape Propagate`

These are options regarding :doc:`shape keys </animation/shape_keys/index>`.

Blend From Shape
   Blend in the shape from a shape key.


Propagate to Shapes
===================

Shape Propagate
   Apply selected vertex locations to all other shape keys.


.. _vertex-merging:

Merge Vertices
==============

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Merge...`,
               :menuselection:`Context Menu --> Merge`
   :Hotkey:    :kbd:`Alt-M`

This tool allows you to merge all selected vertices to a unique one, dissolving all others.
You can choose the location of the surviving vertex in the menu this tool pops up before
executing:

At First
   Only available in *Vertex* select mode,
   it will place the remaining vertex at the location of the first one selected.
At Last
   Only available in *Vertex* select mode,
   it will place the remaining vertex at the location of the last one selected (the active one).
At Center
   Available in all select modes,
   it will place the remaining vertex at the center of the selection.
At Cursor
   Available in all select modes,
   it will place the remaining vertex at the 3D Cursor.
Collapse
   Every island of selected vertices (connected by selected edges) will merge on its own median center,
   leaving one vertex per island.
   It is also available *via* the :menuselection:`Mesh --> Edges --> Collapse` menu option...

Merging vertices of course also deletes some edges and faces. But Blender will do everything
it can to preserve edges and faces only partly involved in the reunion.

.. note::

   *At First* and *At Last* depend on that the selection order is saved:
   the order is lost, for instance, after changing selection mode.

UVs
   If *UVs* is ticked in the :ref:`ui-undo-redo-adjust-last-operation` panel, the UV mapping coordinates,
   if existing, will be corrected to avoid image distortion.


By Distance
-----------

Todo.


Vertex Groups
=============

Todo.


.. _bpy.ops.object.hook_add_selob:

Hooks
=====

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Hooks`
   :Hotkey:    :kbd:`Ctrl-H`

Adds a :doc:`Hook Modifier </modeling/modifiers/deform/hooks>`
(using either a new empty, or the current selected object) linked to the selection.
Note that even if it appears in the history menu,
this action cannot be undone in *Edit Mode* -- because it involves other objects...

When the current object has no hooks associated, only the 2 first options will appear on the menu.

Hook to New Object
   Creates a new Hook Modifier for the active object and assigns it to the selected vertices;
   it also creates an empty at the center of those vertices, which are hooked to it.
Hook to Selected Object
   Does the same as *Hook to New Object*, but instead of hooking the vertices to a new empty,
   it hooks them to the selected object (if it exists).
   There should be only one selected object (besides the mesh being edited).
Hook to Selected Object Bone
   Does the same as *Hook to New Object*,
   but it sets the last selected bone in the also selected armature as a target.
Assign to Hook
   The selected vertices are assigned to the chosen hook. For that to happen,
   a list of the hooks associated to the object is displayed.
   All the unselected vertices are removed from it (if they were assigned to that particular hook).
   One vertex can be assigned to more than one hook.
Remove Hook
   Removes the chosen hook (from the displayed list) from the object:
   the specific Hook Modifier is removed from the modifier stack.
Select Hook
   Selects all vertices assigned to the chosen hook (from the hook list).
Reset Hook
   It's equivalent to the *Reset* button of the specific Hook Modifier (chosen from the hook list).
Recenter Hook
   It's equivalent to the *Recenter* button of the specific Hook Modifier (chosen from the hook list).


Make Vertex Parent
==================

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Make Vertex Parent`
   :Hotkey:    :kbd:`Ctrl-P`

This will parent the other selected object(s) to the vertices/edges/faces selected,
as described :doc:`here </scene_layout/object/properties/relations/parents>`.
