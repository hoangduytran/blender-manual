.. _bpy.ops.uv.select:

*********
Selecting
*********

Selection tools are available in the *Select Menu* in the header,
and the shortcuts listed below:


Menu
====

Box Select :kbd:`B`
   Click and drag to box select UV coordinates.
   Alternatively, use :kbd:`B` to start :ref:`box selection <tool-select-box>`.
Box Select Pinned :kbd:`Ctrl-B`
   Use the box lasso to select only pinned UV coordinates.
Circle Select
   See :ref:`tool-select-circle`.
Select All :kbd:`A`
   Selects all UV coordinates.
Select None :kbd:`Alt-A`
   Deselects all UV coordinate.
Inverse :kbd:`Ctrl-I`
   Inverts the current selection.
More/Less :kbd:`Ctrl-NumpadPlus`, :kbd:`Ctrl-NumpadMinus`
   Expands/Contracts the selection to/from the adjacent elements of the selection type.
Select Pinned :kbd:`Shift-P`
   Selects all :ref:`pinned <bpy.ops.uv.pin>` UVs.
Select Linked
   Linked :kbd:`Ctrl-L`
      This operator selects all UVs that are connected to currently selected UVs.
      This works similarly to the tools in 3D Viewport.
   Shortest Path
      Path between two selected elements.
Select Split :kbd:`Y`
   Cuts apart the selected UVs from the map. Only those UVs which belong to
   fully selected faces remain selected. As the name implies, this is particularly useful to
   unlink faces and move them elsewhere. The hotkey is analogous to the mesh Split tool.
Select Overlap
   Selects any UVs that are extended over other UVs while also selecting any underlying UVs.


.. _bpy.ops.uv.shortest_path_select:

Shortest Path
=============

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Select Linked --> Shortest Path`
   :Hotkey:    :kbd:`Ctrl-LMB`

Selects all UV components along the shortest path from
the active component to the one which was selected.

Face Stepping
   Supports diagonal paths for vertices and faces, and
   selects edge rings with edges.
Topological Distance
   Only takes into account the number of edges of the path and
   not the length of the edges to calculate the distances.
Fill Region :kbd:`Shift-Ctrl-LMB`
   Selects all elements in the shortest paths from the active selection to the clicked area.
Checker Deselect Options
   Allows to quickly select alternate elements in a path.

   Deselected
      The number of deselected elements in the repetitive sequence.
   Selected
      The number of selected elements in the repetitive sequence.
   Offset
      Offset from the starting point.


Header
======

Sync Selection
   Turning on the *Sync Selection* button causes selection of components
   in the 3D Viewport to sync with their corresponding elements in the UV editor.
   If off only the selected faces are displayed in the UV editor.
   These two modes have very different results when transforming components in the UV editor.


Selection Modes
---------------

Select Modes dependent on the Sync Selection.


Sync Selection Off
^^^^^^^^^^^^^^^^^^

Vertex
   Select individual vertices.
Edge
   Select edges.
Face
   Select faces.
Island
   Select contiguous groups of faces.

Sticky Selection Mode
   This selector lets you enable automatic additional selection.

   Shared Vertex
      Selects UVs that share a mesh vertex, even if they are in different UV locations.
   Shared Location
      Selects UVs that are in the same UV location and share a mesh vertex.
   Disabled
      Disables Sticky Selection.
      When you move a UV in this mode, each face owns its own UVs, allowing them to be separated.


Sync Selection On
^^^^^^^^^^^^^^^^^

When selecting UVs or Edges, it behaves like *Shared Vertex* mode above.
When selecting Faces, it behaves as in *Disabled Stick Selection* above.

- Vertex
- Edge
- Face
