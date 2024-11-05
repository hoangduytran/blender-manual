.. index:: Compositor Nodes; Render Layers
.. _bpy.types.CompositorNodeRLayers:

******************
Render Layers Node
******************

.. figure:: /images/compositing_node-types_CompositorNodeRLayers.webp
   :align: right
   :alt: Render Layers Node.

Read render layers and passes from a scene into the compositing node graph.


Inputs
======

This node has no input sockets.


Properties
==========

Scene
   Select the scene within your blend-file. The scene information taken is the raw footage
   (pre-compositing and pre-sequencing).

   .. hint::

      To use composited footage from another scene, it has to be rendered into a multi-layer frameset
      (e.g. ``OpenEXR``) as an intermediate file store and then imported with Image input node again.

Render Layer
   A list of available :doc:`Render Layers </render/layers/index>`.
   The render button is a shorthand to re-render the active scene.


Outputs
=======

Image
   Rendered image.
Alpha
   Alpha channel.


.. rubric:: Render Passes Sockets

Depending on the Render passes that are enabled, other sockets are available.
See :doc:`render passes </render/layers/passes>`.

.. note::

   In the viewport compositor, Render Passes are only supported in EEVEE. For other engines, the
   passes return a zero value, a zero vector, or a transparent color depending on their type.
