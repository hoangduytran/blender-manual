.. _ui-tree-view:

*********
Tree View
*********

.. figure:: /images/interface_controls_templates_tree_view.png
   :align: right
   :figwidth: 268px

   Example of a Tree View with expanded items.

The Tree View is used to display hierarchical data in a structured,
expandable layout. Unlike the :ref:`List View <ui-list-view>`,
items can contain child items that can be expanded or collapsed.

This control is commonly used to organize nested elements such as
node trees, collections, or grouped settings.


Expand / Collapse
=================

Items that contain children display a disclosure triangle.
Click :kbd:`LMB` on the triangle to expand or collapse the item.

Expanded items show their child entries indented beneath them.
Collapsed items hide their contents.


Select
======

Click :kbd:`LMB` on an item to select it.

Selection behavior may vary depending on the context.
Some Tree Views allow multi-selection.


Rename
======

If supported, items can be renamed by double-clicking them
or by pressing :kbd:`F2`.


Hierarchy
=========

Child items are visually indented to reflect their relationship
to parent items.

Depending on the context, items may support:

- Drag-and-drop reordering.
- Moving items between parent entries.
- Reorganizing nested structures.


Context Menu
============

Right-click (:kbd:`RMB`) on an item to open a context menu
with operators specific to that entry.


Filtering and Sorting
=====================

Some Tree Views support filtering and sorting options,
similar to the :ref:`List View <ui-list-view>`.
Availability depends on the specific implementation.


Modification Buttons
====================

Depending on the context, buttons may appear alongside the Tree View
to add, remove, or reorder items.

These behave similarly to the modification buttons in the
:ref:`List View <ui-list-view>`.
