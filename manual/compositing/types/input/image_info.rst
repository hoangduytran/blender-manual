.. index:: Compositor Nodes; Image Info
.. _bpy.types.CompositorNodeImageInfo:

***************
Image Info Node
***************

.. figure:: /images/node-types_CompositorNodeImageInfo.webp
   :align: right
   :alt: Image Info Node.

The *Image Info* node outputs spatial and transformation information about an image in the compositor.

This node is useful for generating procedural effects that depend on image size, position, or pixel coordinates.
It enables workflows such as vignette creation using math nodes,
or dynamic scaling of effects relative to image dimensions.


Inputs
======

Image
   The image to retrieve information from.


Properties
==========

This node has no properties.


Outputs
=======

Pixel Coordinates
   Coordinates representing the center of each pixel in the image.
   These are integer coordinates with a half-pixel offset applied.

Texture Coordinates
   Normalized coordinates centered at zero, scaled based on the image's largest dimension.
   These are useful for general-purpose procedural generation, similar to *Object* coordinates in shader nodes.

Resolution
   The width and height of the image in pixels.

Location
   The position of the image in compositing space.

Rotation
   The rotation of the image in radians, around its center.

Scale
   The scale of the image relative to its original size in compositing space.
