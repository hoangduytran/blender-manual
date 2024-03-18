
******
Baking
******

Baking allows saving and loading intermediate geometries.
Baking parts of the node tree can be used for better performance.

The data format used to store geometry data is not considered to be an import/export format.
Volume objects, however, are saved using the OpenVDB file format which can be used interoperably.

Data can be baked using two methods:

- :doc:`/modeling/geometry_nodes/geometry/operations/bake` -- used to bake any portion of the node tree.
- :ref:`Simulation Zone Baking <geometry_nodes-simulation-baking>` --
  used to bake animations where the result of one geometry state can influence the next state.


.. _bpy.types.NodesModifierDataBlock:

Data-Block References
=====================

.. reference::

   :Editor:    Geometry Node Editor
   :Panel:     :menuselection:`Sidebar --> Node --> Data-Block References`

Baked geometries that reference other data-blocks such as materials are listed here.

This panel allows changing these references after the data has been baked.

.. note::

   Currently only material data-blocks are supported.
