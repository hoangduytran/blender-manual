
*****
Usage
*****

Toggling Interaction Modes
==========================

Selecting some data-blocks with :kbd:`LMB` will toggle into the relevant interaction mode.
For example, selecting the mesh data of the cube will select the cube and enter *Edit Mode*.
Selecting the data-block again will toggle back into *Object Mode*.

If the data-block type supports multi-editing,
you can use :kbd:`Ctrl` to add or remove objects from the Edit Mode.


Relations Management
====================

.. figure:: /images/editors_outliner_relations.png
   :align: right

   Linking objects to a collection.

Data-blocks can be dragged and dropped to manage data relations in the Outliner.
To begin a drag and drop, :kbd:`LMB` click and drag from the name or icon of a data-block.

Objects can be moved to collections by dropping on the name or contents of a collection.
To link an object to a collection, hold :kbd:`Ctrl` while dropping.
To set parent-child relations between objects, drop an object onto another object
while holding :kbd:`Shift`.

.. note::

   Drag and drop will attempt to operate on the entire selection. Selected data-blocks
   that are incompatible with the operation will remain unmodified.
