.. index:: Nodes; Combine Bundle Node
.. _bpy.types.NodeCombineBundle:

.. --- copy below this line ---

*******************
Combine Bundle Node
*******************

.. figure:: /images/node-types_NodeCombineBundle.webp
   :align: right
   :alt: Combine Bundle Node

The *Combine Bundle* node creates a new :doc:`Bundle </interface/controls/nodes/types/utilities/bundles/index>`
from multiple input values.
Each input becomes an element of the bundle, identified by its socket name.
Values can be accessed in other parts of the node tree using the
:doc:`Separate Bundle </interface/controls/nodes/types/utilities/bundles/separate_bundle>`


Inputs
======

The node can contain an arbitrary number of input sockets.
Each socket can be given a custom name and type. Supported types include (but not limited to):

- Geometry
- Objects
- Values (e.g. float, integer, boolean, vector, color)
- Fields
- Nested Bundles


Properties
==========

Properties are available in the *Node* tab of the Sidebar.

Sync Sockets
   Update matching :doc:`Separate Bundle </interface/controls/nodes/types/utilities/bundles/separate_bundle>`
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

Bundle
   The resulting bundle containing all defined inputs.
