.. _bpy.ops.mesh.rip_move:
.. _tool-mesh-rip_region:

************
Rip Vertices
************

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Rip Vertices`
   :Shortcut:  :kbd:`V`

Rip creates a "hole" in the mesh by making a copy of selected vertices and edges,
still linked to the neighboring non-selected vertices,
so that the new edges are borders of the faces on one side, and the old ones,
borders of the faces on the other side of the rip.


Examples
========

.. list-table::

   * - .. figure:: /images/modeling_meshes_editing_vertex_rip-vertices_before.png
          :width: 260px

          Selected vertex.

     - .. figure:: /images/modeling_meshes_editing_vertex_rip-vertices_after.png
          :width: 260px

          Hole created after using rip on vertex.

   * - .. figure:: /images/modeling_meshes_editing_vertex_rip-vertices_edges-before.png
          :width: 260px

          Edges selected.

     - .. figure:: /images/modeling_meshes_editing_vertex_rip-vertices_edges-after.png
          :width: 260px

          Result of rip with edge selection.

   * - .. figure:: /images/modeling_meshes_editing_vertex_rip-vertices_complexselection-before.png
          :width: 260px

          A complex selection of vertices.

     - .. figure:: /images/modeling_meshes_editing_vertex_rip-vertices_complexselection-after.png
          :width: 260px

          Result of rip operation.


Limitations
===========

The following selections are not supported by the rip operator and will give an error message:

- Face(s), including when selecting vertices or edges that form up a face.
- Edges or vertices that are not "between" two faces (non :term:`Manifold`).
- Two vertices that aren't connected to each other.
