.. index:: Nodes; Separate Bundle
.. _bpy.types.NodeSeparateBundle:

.. --- copy below this line ---

********************
Separate Bundle Node
********************

.. figure:: /images/node-types_NodeSeparateBundle.webp
   :align: right
   :alt: Separate Bundle Node

The *Separate Bundle* node extracts individual values from a
:doc:`Bundle </interface/controls/nodes/types/bundles/index>`.
Each output corresponds to an element in the bundle, identified by its socket name.

This node is the counterpart of the
:doc:`Combine Bundle </interface/controls/nodes/types/bundles/combine_bundle>`
node and is typically used to retrieve structured data that was previously grouped together.


Inputs
======

Bundle
   The input bundle that contains all grouped values.


Properties
==========

Properties are available in the *Node* tab of the Sidebar.

Sync Sockets
   Update matching :doc:`Separate Bundle </interface/controls/nodes/types/bundles/separate_bundle>`
   nodes in the same node tree to reflect name and type changes. Use this after renaming or
   retargeting item types so downstream nodes stay in sync.

Define Signature
   Locks the current item list and types to stabilize interfaces when publishing node groups.
   When enabled, adding/removing items is disabled until the option is turned off.


Bundle Items
------------

List of bundle items
   Displays one entry per element in the bundle.
   Double-click to rename.

   Add Item
      Add a new socket to the bundle.
   Remove Item
      Delete the selected socket.

Type
   The data type for the selected item (e.g. Float, Vector, Geometry, Object, Bundle).
   For value types, a default value control is shown and used when the socket is unlinked.


Outputs
=======

This node has a dynamic set of output sockets. Each socket outputs the value of the corresponding
bundle item, using the item's name and type as defined in the bundle.
