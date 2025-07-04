.. _bpy.types.NodeGroup:

***********
Node Groups
***********

.. figure:: /images/interface_controls_nodes_groups_example.png
   :align: right

   Example of a node group.

Grouping nodes can simplify a node tree by hiding complexity and reusing common functionality.
A node group is visually identified by its green title bar.

Conceptually, node groups allow you to treat a *set* of nodes as a single unit.
They are similar to functions in programming: reusable, composable, and parameterizable.

For example, suppose you create a "Wood" material and want to use it in multiple colors.
You could duplicate the entire node setup for each color, but maintaining those duplicates
would be tedious if you later decide to change the wood grain detail.
Instead, you can move the nodes that generate the wood pattern into a node group.
Each material can then reuse this group and supply a custom color as input.
Any updates to the grain detail need to be made only once—inside the node group.

Node groups can be nested; that is, a group can contain other groups.

.. note::

   Recursive node groups are prohibited to avoid infinite recursion.
   A group cannot contain itself, directly or indirectly.

.. tip::

   Like other data-blocks, node groups with names that start with ``.`` are hidden
   from :ref:`menus and lists <ui-data-block>` and can only be accessed via search.
   This is useful for node asset authors who want to hide internal utility groups from end users.

*Group Input* and *Group Output* nodes are used to represent data flowing into and out of the group.

The *Group Input* node provides access to the group's input sockets from within the node group.
These sockets act as parameters that control the behavior of the group from the outside.
You can connect them to internal nodes to drive values such as factors, colors, or geometry inputs.

The *Group Output* node defines the data that is passed out of the node group.
Only sockets connected to this node will be available as outputs on the group itself.

.. important::

   Avoid using nodes output nodes such as Material Output or Composite inside node groups.
   These should be used on the top level node tree to improve re-usability of node groups.

   Use *Group Output* to pass data out of a node group.


Usage
=====

Managing Inputs/Outputs
-----------------------

You can add, remove, and reorder input and output sockets in the *Group* panel in the Sidebar.
New sockets can also be created directly by dragging a link to or from the hollow socket
on the *Group Input* or *Group Output* node to another socket in the node editor.


Reusing Node Groups
-------------------

.. reference::

   :Menu:      :menuselection:`Add --> Group`
   :Shortcut:  :kbd:`Shift-A`

Existing node groups can be placed again after they're initially defined, be it in the same
node tree or a different one. It's also possible to import node groups from a different blend-file
using :menuselection:`File --> Link/Append`.

.. tip::

   When appending node groups from another blend-file,
   Blender does not distinguish between types such as material or compositing groups.
   To avoid confusion, it is recommended to adopt a naming convention, like using prefixes
   (`Mat_`, `Comp_`, `Geo_`, etc.), to indicate the group's context.


Properties
==========

Group
-----

.. reference::

   :Panel:     :menuselection:`Sidebar --> Group --> Group`

.. figure:: /images/interface_controls_nodes_groups_interface-group-panel.png
   :align: right

   The *Group* panel.

This panel contains properties that relate the group node such as it's name and look.

Name
   The name of node as displayed in the :ref:`interface-nodes-parts-title`.

.. _bpy.types.NodeTree.description:

Description
   The message displayed when hovering over the :ref:`interface-nodes-parts-title` or in add menus.

.. _bpy.types.NodeTree.color_tag:

Color Tag
   Color tag of the node group which influences the header color.

.. _bpy.types.NodeTree.default_group_node_width:

Node Width
   The width for newly created group nodes.

   .. _bpy.ops.node.default_group_width_set:

   :bl-icon:`node` (Set Default Node Width)
      Set the width based on the parent group node in the current context


Usage :guilabel:`Geometry Nodes`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This panel is only visible in the :doc:`Geometry Node Editor </editors/geometry_node>`.

.. _bpy.types.GeometryNodeTree.is_modifier:

Modifier
   The node group is intended for use with the :doc:`/modeling/modifiers/generate/geometry_nodes`.

.. _bpy.types.GeometryNodeTree.is_tool:

Tool
   The node group is intended to be used as a :doc:`tool </modeling/geometry_nodes/tools>`.

The :ref:`data-block menu <ui-data-block>` in the header of the Geometry Node Editor
only lists the node groups whose Usage matches the current :ref:`bpy.types.SpaceNodeEditor.geometry_nodes_type`.

.. tip::

   If you accidentally disable both Usages, the node group will not be accessible through the
   data-block menu anymore. To make it accessible again, you can add it as a node to a different node
   group (:menuselection:`Add --> Group`), select that node, and press :kbd:`Tab` to enter it.
   From there, you can enable one of the Usages again.


.. _bpy.ops.node.tree_socket_add:
.. _bpy.ops.node.tree_socket_remove:
.. _bpy.ops.node.tree_socket_move:

Group Sockets
-------------

.. reference::

   :Panel:     :menuselection:`Sidebar --> Group --> Group Sockets`

.. figure:: /images/interface_controls_nodes_groups_interface-group_sockets_panel.png
   :align: right

   The *Group Sockets* panel.

This panel is used to add, remove, reorder, and edit the input/output sockets of the node group.

Input values that do not affect the output will be greyed out.

You can also add panels to organize sockets within a node group,
structuring and categorizing inputs for improved clarity and usability.
This is particularly helpful in complex node setups.

Note, panels are always at the bottom of nodes.
Panels can be nested by dragging a panel in the UI list on top of another panel.

.. _bpy.types.NodeTreeInterfaceSocket.name:

Socket List
   A :ref:`ui-list-view` of all inputs, outputs, and panels.

   Here you can name the socket which is displayed in the node's interface.

.. _bpy.types.NodeTreeInterfaceSocket.description:

Description
   The message displayed when hovering over socket properties.

.. _bpy.types.NodeTreeInterfacePanel.default_closed:

Closed by Default :guilabel:`Panels`
   Panel is closed by default on new nodes.

.. _bpy.types.NodeTreeInterfaceSocket*.default_value:

Default
   The value to use when nothing is connected to the socket.

.. _bpy.types.NodeTreeInterfaceSocket*.min_value:
.. _bpy.types.NodeTreeInterfaceSocket*.max_value:

Min, Max
   The minimum and maximum value for the UI button shown in the node interface.
   Note, this is not a minimum or maximum for the data that can pass through the node.
   If a socket passes a higher value than the maximum, it will still pass into the node unchanged.

.. rubric:: Geometry Nodes

.. _bpy.types.NodeTreeInterfaceSocket.default_input:

Default Input
   Input to use when the socket is unconnected.
   Requires *Hide Value* to be enabled.

.. _bpy.types.NodeTreeInterfaceSocket.hide_value:

Hide Value
   Hide the socket value even when the socket is not connected.

.. _bpy.types.NodeTreeInterfaceSocket.hide_in_modifier:

Hide in Modifier
   Don't show the input value in the geometry nodes modifier interface.
   This allows the input to be used in the context of a node group but not as a modifier input.

   This option is only available for geometry nodes and only for input sockets.

.. _bpy.types.NodeTreeInterfaceSocket.force_non_field:

Single Value
   Only allow single value inputs rather than :doc:`/modeling/geometry_nodes/fields`.


.. _node-group-properties-animation:

Animation
---------

Controls animation data for node group properties, including active :doc:`Actions </animation/actions>`
and their assigned :ref:`Slot <animation-actions-slots>`.

See :ref:`animation-actions-slots-manual-assign` for more information.


.. _bpy.ops.node.group_make:

Make Group
==========

.. reference::

   :Menu:      :menuselection:`Node --> Make Group`
   :Shortcut:  :kbd:`Ctrl-G`

Creates a new node group that contains all selected nodes.

*Group Input* and *Group Output* nodes will be created to represent connections to unselected nodes outside the group.
Inputs will be routed to *Group Input*  and outputs routed to the *Group Output*.

Default naming for the node group is "NodeGroup", "NodeGroup.001", etc.
You can rename the group using the name field at the top of the group node or in the Sidebar.


.. _bpy.ops.node.group_insert:

Insert Into Group
=================

.. reference::

   :Menu:      :menuselection:`Node --> Insert Into Group`

Moves the selected nodes into the :term:`active <Active>` group node.
To use, select a set of nodes, ending with the destination group node,
then, running the operation will move those nodes into that group.
The moved nodes are collected into a group of their own to preserve their connection context,
having their own group input and output nodes.
The group's existing input and output nodes are updated with new sockets, if any, from the new nodes.
The node group must be edited to contain a single *Group Input* and a single *Group Output* node.


.. _bpy.ops.node.tree_path_parent:
.. _bpy.ops.node.group_edit:

Edit Group
==========

.. reference::

   :Menu:      :menuselection:`Node --> Edit Group`
   :Header:    :menuselection:`Go to Parent Node Tree`
   :Shortcut:  :kbd:`Tab`, :kbd:`Ctrl-Tab`

With a node group selected, press :kbd:`Tab` to move into it and see its content.
Press :kbd:`Tab` again (or :kbd:`Ctrl-Tab`) to leave the group and go back to
its parent, which could be the top-level node tree or another node group.
You can refer to the breadcrumbs in the top left corner of the node editor
to see where you are in the hierarchy.

.. figure:: /images/render_cycles_optimizations_reducing-noise_glass-group.png
   :width: 620px

   Example of an expanded node group.


.. _bpy.ops.node.group_ungroup:

Ungroup
=======

.. reference::

   :Menu:      :menuselection:`Node --> Ungroup`
   :Shortcut:  :kbd:`Ctrl-Alt-G`

Removes the group and places the individual nodes into your editor workspace.
No internal connections are lost, and now you can link internal nodes to other nodes in your workspace.

Separate :kbd:`P`
   Separate selected nodes from the node group.

   Copy
      Copy to parent node tree, keep group intact.
   Move
      Move to parent node tree, remove from group.
