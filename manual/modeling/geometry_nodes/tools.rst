.. index:: Geometry Nodes; Tools
.. _bpy.types.GeometryNodeTree:

****************
Node-Based Tools
****************

Geometry Nodes can be used to expand the core functionality of Blender via node-group-defined tools.
They can be shared as any regular node group assets.

.. figure:: /images/modeling_geometry-nodes_tools.png
   :align: center

   Node group tools integrated in the Selection menu.


.. _tool_context:

Tool Context
============

The way to create Node-based tools is by switching the Geometry Nodes editor
:ref:`context <bpy.types.SpaceNodeEditor.geometry_nodes_type>` to *Tool*.

New node groups created in the tool context will be enabled as
:ref:`Tool <bpy.types.GeometryNodeTree.is_tool>` by default,
although users still need to set them as Assets if they want to share them (see below).

.. note::

   The :doc:`Inspection </modeling/geometry_nodes/inspection>`
   features are not supported in the *Tool* context: Viewer Node and Socket Inspection.


Asset
=====

For a node group to be shared as a tool, it has to be an :doc:`Asset </editors/asset_browser>` first. The asset
catalog is used to determine on which menus the node group will show, similar to the regular node group assets.
If the catalog name matches an existing menu, the tool will be added to the end of it.
Assets that have no catalog assigned to them, or local tools are exposed in the "Unassigned" menu.

The asset options need to be set on the :doc:`Asset Browser </editors/asset_browser>`.


Tool Settings
=============

The node group inputs will be exposed as in the :doc:`Adjust Last Operation </interface/undo_redo>` panel.


.. _modeling-geometry_nodes-tools_contexts:

Supported Modes & Data-Types
============================

Node groups must specify which modes and object types they support.
This helps to determine where the tool is available in the user interface.
These properties can be configured in popover menus in the
:ref:`Geometry Node editor <editors-geometry_nodes-tool_context>` when in the *Tool* context.

Currently only Object, Edit, and Sculpting modes are supported, and only for the Mesh and Hair Curves object types.

.. important::

   For mesh objects, :doc:`/animation/shape_keys/index` are not supported.
   Operating a node tool on a mesh with shape keys will remove the shape key data.


Tool-specific Nodes
===================

The following nodes are only supported in the *Tool* context:

- :doc:`/modeling/geometry_nodes/input/scene/3d_cursor`
- :doc:`/modeling/geometry_nodes/mesh/read/face_set`
- :doc:`/modeling/geometry_nodes/geometry/read/selection`
- :doc:`/modeling/geometry_nodes/mesh/write/set_face_set`
- :doc:`/modeling/geometry_nodes/geometry/write/set_selection`

.. note::

   The :doc:`Self Object </modeling/geometry_nodes/input/scene/self_object>`
   node returns the Active object when inside a *Tool* node group.


Non-supported Nodes
===================

These nodes are only supported in the *Modifier* context:

- :doc:`/modeling/geometry_nodes/simulation/simulation_zone`
- :doc:`/modeling/geometry_nodes/output/viewer`
