
***************
Selecting Nodes
***************

Nodes in the editor can be selected and manipulated.
Selections determine which nodes can be moved, duplicated, or connected.
The active node (last selected) is highlighted with a lighter outline.
It serves as the reference for certain operations, such as grouping or linking,
and also determines which properties are displayed in the *Sidebar* and *Properties Editor*.

Nodes are selected with :kbd:`LMB`.
Multiple nodes can be selected by holding :kbd:`Shift-LMB`.

Blender also provides a variety of selection tools and shortcuts for quickly choosing nodes
based on their type, connections, or layout.


.. _bpy.ops.node.select_all:

All
===

.. reference::

   :Menu:      :menuselection:`Select --> All`
   :Shortcut:  :kbd:`A`

Selects all nodes.


None
====

.. reference::

   :Menu:      :menuselection:`Select --> None`
   :Shortcut:  :kbd:`Alt-A`

Deselects all nodes.


Invert
======

.. reference::

   :Menu:      :menuselection:`Select --> Invert`
   :Shortcut:  :kbd:`Ctrl-I`

Inverts the current selection, selecting all unselected nodes and deselecting the currently selected ones.


Box Select
==========

.. reference::

   :Menu:      :menuselection:`Select --> Box Select`
   :Shortcut:  :kbd:`B`

Click and drag to select nodes within a rectangular region.
See :ref:`Box Select <bpy.ops.*.select_box>` for more details.


Circle Select
=============

.. reference::

   :Menu:      :menuselection:`Select --> Circle Select`
   :Shortcut:  :kbd:`C`

Click and drag with a circular brush to select nodes.
See :ref:`Circle Select <bpy.ops.*.select_circle>`.


Lasso Select
============

.. reference::

   :Menu:      :menuselection:`Select --> Lasso Select`

Draw a freeform lasso to select nodes within the region.
See :ref:`Lasso Select <bpy.ops.*.select_lasso>`.


.. _bpy.ops.node.select_linked_from:

Select Linked From
==================

.. reference::

   :Menu:      :menuselection:`Select --> Select Linked From`
   :Shortcut:  :kbd:`L`

Expands the selection to all nodes connected to the inputs of the selected nodes.


.. _bpy.ops.node.select_linked_to:

Select Linked To
================

.. reference::

   :Menu:      :menuselection:`Select --> Select Linked To`
   :Shortcut:  :kbd:`Shift-L`

Expands the selection to all nodes connected from the outputs of the selected nodes.


.. _bpy.ops.node.select_grouped:

Select Grouped
==============

.. reference::

   :Menu:      :menuselection:`Select --> Select Grouped`
   :Shortcut:  :kbd:`Shift-G`

Selects nodes that share similar properties with the active node.

- **Type**: Select all nodes of the same type (e.g. all *Math* nodes).
- **Color**: Select nodes with the same custom :ref:`color <bpy.types.Node.color>`.
  (This refers to user-assigned editor colors, not the color data processed by nodes.)
- **Prefix/Suffix**: Select nodes whose names match the same starting or ending text.


.. _bpy.ops.node.select_same_type_step:

Activate Same Type Previous/Next
================================

.. reference::

   :Menu:      :menuselection:`Select --> Activate Same Type Previous/Next`
   :Shortcut:  :kbd:`Shift-]` / :kbd:`Shift-[`

Cycles through nodes of the same type, activating the previous or next node in the node tree
and centering it in the view.


.. _bpy.ops.node.find_node:

Find Node
=========

.. reference::

   :Menu:      :menuselection:`Select --> Find Node`
   :Shortcut:  :kbd:`Ctrl-F`

Opens a search pop-up to quickly find and select a node by name.
The view automatically pans to the selected node.
