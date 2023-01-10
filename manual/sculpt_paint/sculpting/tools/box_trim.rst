
********
Box Trim
********

.. reference::

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Box Trim`

Adds or removes geometry based on a :ref:`box selection <tool-select-box>`.
This tool is especially useful for sketching an early base mesh for further
sculpting with the :ref:`voxel remesher </sculpt_paint/sculpting/tool_settings/remesh>`.

.. add visual example of removing/adding geometry for a rough base.

New geometry is assigned to a new :ref:`Face Set <sculpting-editing-facesets>`.
When removing geometry, the new interior geometry along the selection will be assigned
a new face set instead.

.. note::
   It is not recommended to use this tool on a mesh above 100k vertices.
   This tool is using a Boolean operation so it might take a long time to process.
   For higher resolution meshes it is recommedned to instead use the
   :doc:`Line Project </sculpt_paint/sculpting/tools/line_project>` tool
   or the *Fair Positions* mode of the
   :doc:`Edit Face Set </sculpt_paint/sculpting/tools/edit_face_set>` tool.


Tool Settings
=============

Trim Mode
   Geometry can be either added or removed by choosing one of these modes.

   Difference
      Removes geometry, filling any holes that are created.
   Union
      Creates a geometry and joins any intersections with existing geometry.
   Join
      Similar to *Union* but joins the mesh as separate geometry,
      without performing any Boolean operations with existing geometry.

Use Cursor for Depth
   Use cursor location and radius for the dimensions and position of the trimming shape.
   If not set, the tool uses the full depth of the object from the camera view.
