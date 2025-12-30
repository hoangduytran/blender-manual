
*************
Select Linked
*************

.. _bpy.ops.mesh.select_linked:

Linked
======

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Select Linked --> Linked`
   :Shortcut:  :kbd:`Ctrl-L`

Select geometry connected to already selected elements.
This is often useful when a mesh has disconnected, overlapping parts,
where isolating it any other way would be tedious.
To give more control, you can also enable delimiters in the :ref:`bpy.ops.screen.redo_last` panel,
so the selection is constrained by seams, sharp edges, materials or UV islands.

With *Pick Linked* you can also select connected geometry directly under the cursor,
using the :kbd:`L` shortcut to select or :kbd:`Shift-L` to deselect linked.
This works differently in that it uses the geometry under the cursor instead of the existing selection.


.. _bpy.ops.mesh.shortest_path_select:
.. _bpy.ops.mesh.shortest_path_pick:

Shortest Path
=============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Select Linked --> Shortest Path`
   :Shortcut:  :kbd:`Ctrl-LMB`

.. figure:: /images/modeling_meshes_selecting_linked_shortest-path.png

   Select a face or vertex path with :kbd:`Ctrl-LMB`.

Selects all geometry along the shortest path from
the active vertex, edge, or face to the one which was selected.

Edge Tag (in Edge select mode only)
   What to do with the selected edges:

   Select
      Simply select the edges.
   Tag Seam
      Mark the edges as :doc:`UV Seams </modeling/meshes/uv/unwrapping/seams>`.
   Tag Sharp
      Mark the edges as :ref:`Sharp <bpy.ops.mesh.mark_sharp>`.
   Tag Crease
      Give the edges a :ref:`Crease <modeling-edges-crease-subdivision>` value of 1.0.
   Tag Bevel
      Give the edges a :ref:`Bevel Weight <modeling-edges-bevel-weight>` of 1.0.
   Tag Freestyle Edge Mark
      Mark the edges as :ref:`Freestyle <freestyle-edge-marks>` edges.

Face Stepping
   Supports diagonal paths for vertices and faces, and
   selects edge rings with edges.
Topology Distance
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


.. _bpy.ops.mesh.faces_select_linked_flat:

Linked Flat Faces
=================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Select Linked --> Linked Flat Faces`

Selects all connected faces with a similar angle.

Sharpness
   Select connected faces with a reference angle less than the value specified.

.. figure:: /images/modeling_meshes_selecting_linked_flat-faces.png

Looking at the image above, when at least one face is selected (as seen on the left),
*Linked Flat Faces* will select all connecting faces that lie
on the same or similar plane (as shown in the middle image).
If the corners are smoothed, those faces are no longer lined up with the selected faces.
At this point, increasing the *Sharpness* value in the tool options could include the smoothed faces.
