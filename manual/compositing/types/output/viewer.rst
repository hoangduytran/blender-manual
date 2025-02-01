.. index:: Compositor Nodes; Viewer
.. _bpy.types.CompositorNodeViewer:

***********
Viewer Node
***********

.. figure:: /images/node-types_CompositorNodeViewer.webp
   :align: right
   :alt: Viewer Node.

The *Viewer* node allows temporarily visualizing data from inside a node graph.
It can be plugged in anywhere to inspect an image or value map in your node tree.

Select a view node with :kbd:`LMB` to switch between multiple viewer nodes.
It is possible to automatically plug any other node into a Viewer node
by pressing :kbd:`Shift-Ctrl-LMB` on it.


Inputs
======

Image
   RGB image. The default is black, so leaving this node unconnected will result in a black image.
Alpha
   Alpha channel.


Properties
==========

Use Alpha
   Used alpha channel, colors are treated alpha *premultiplied*.
   If disabled, alpha channel gets set to 1,
   and colors are treated as alpha *straight*, i.e. color channels does not change.


Outputs
=======

This node has no output sockets.

.. note::

   It is possible to add multiple Viewer nodes, though only the active one
   (last selected, indicated by a red header) will be shown on the backdrop or in the Image editor.


Using the Image Editor
======================

The Viewer node allows results to be displayed in the Image Editor.
The image is facilitated in the header by selecting *Viewer Node* in the linked *Image* data-block menu.
The Image Editor will display the image from the currently selected Viewer node.

To save the image being viewed,
use :menuselection:`Image --> Save As...`, :kbd:`Alt-S` to save the image to a file.

The Image Editor also has three additional options in its header to view Images with or
without Alpha, or to view the Alpha or Z itself.
Click and holding the mouse in the Image displayed allows you to sample the values.
