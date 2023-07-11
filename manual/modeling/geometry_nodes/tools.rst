.. index:: Geometry Nodes; Tools
.. _bpy.types.GeometryNode:

################
Node-based Tools
################

Geometry Nodes can be used to expand the core functionality of Blender via node group defined tools.
They can be shared as any regular node group assets.

.. figure:: /images/modeling_geometry-nodes_tools.png
   :align: center

   Node group tools integrated in the Selection menu.

Tool Context
============

The way to create Node-based tools is by switching the Geometry Nodes editor context to `Tool`.

New node groups created there will be enabled as Tool by default, although users still need to set
them as Assets if they want to share them.

.. note::

   The :doc:`Inspection </modeling/geometry_nodes/inspection>` features are not supported on this context: Viewer Node and Socket Inspection.

Asset
=====

For a node group to be shared as a tool, it has to be an :doc:`Asset </editors/asset_browser>` first. The asset catalog is used
to determine on which menus the node group will show, similar to the regular node group assets.

The asset options need to be set on the :doc:`Asset Browser </editors/asset_browser>`.

The catalog is used to determined in which menu the tool is available. Assets that have no catalog assigned to them, or local tools
are exposed in the Unassigned menu.

Tool Settings
=============

The node group inputs will be exposed as in the :doc:`Adjust Last Operation </interface/undo_redo>` panel.

Supported Modes and Data-Types
==============================

Tools are only possible for Edit and Sculpting mode, for Mesh and Curve objects.

Tool-specific Nodes
===================

The following nodes are only supported in the tool context:

   - 3D Cursor
   - Face Set
   - Selection
   - Set Face Set
   - Set Selection

.. note::

   The :doc:`Self Object </modeling/geometry_nodes/input/scene/self_object>` node returns the Active object
   when inside a Tool node group.

Non-supported Nodes
===================

These nodes are only supported in the modifier context:

  - Simulation Zone
  - Viewer Node
