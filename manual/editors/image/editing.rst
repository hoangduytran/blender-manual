
*******
Editing
*******

.. _bpy.ops.image.new:

New
===

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> New`
   :Shortcut:  :kbd:`Alt-N`

Create a new :ref:`image-generated` Image.


.. _bpy.ops.image.open:

Open
====

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Open`
   :Shortcut:  :kbd:`Alt-O`

Load an image from a file.


.. _bpy.ops.image.read_viewlayers:

Open Cached Render
==================

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Open Cached Render`
   :Shortcut:  :kbd:`Ctrl-R`

Find the render cache file for the current scene and load it into the
Render Result. This way, you can restore the last render from a previous
Blender session and continue working in the Compositor without having to
render the scene again.

Note that Blender doesn't create these cache files by default. You
have to enable :ref:`Cache Result <bpy.types.RenderSettings.use_render_cache>`
in the scene's Output options and then render it at least once.


.. _bpy.ops.image.replace:

Replace
=======

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Replace`

Replace the current image by another.


.. _bpy.ops.image.reload:

Reload
======

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Reload`
   :Shortcut:  :kbd:`Alt-R`

Reload the image from the file on drive.


.. _bpy.ops.image.external_edit:

Edit Externally
===============

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Edit Externally`

Open the image in the *Image Editor* program specified in the
:doc:`File Paths Preferences </editors/preferences/file_paths>`.


.. _bpy.ops.image.save:

Save
====

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Save`
   :Shortcut:  :kbd:`Alt-S`

Save the image to its current path.

.. important::

   While animation renders are automatically saved, still renders are not.
   These have to be saved manually.


.. _bpy.ops.image.save_as:

Save As
=======

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Save As`
   :Shortcut:  :kbd:`Shift-Alt-S`

Save the image to a separate file of any type.
The image output settings can be configured and are the same as the
:doc:`Render Output Properties </render/output/properties/output>`.


Save a Copy
===========

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Save a Copy`

Save the file under a specified name,
but keep the old one open in the Image editor.


.. _bpy.ops.image.save_all_modified:

Save All Images
===============

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Save All Images`

Save all modified images. Packed images will be repacked.


.. _bpy.ops.image.invert:

Invert
======

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Invert`

Invert Image Colors
   Invert the colors of an image.
Invert Red/Green/Blue/Alpha Channel
   Invert a single color channel.


.. _bpy.ops.image.resize:

Resize
======

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Resize`

Adjust the image size in pixels.



Transform
=========

.. _bpy.ops.image.flip:

Flip Horizontally
   Mirrors the image so the left side becomes the right side.
Flip Vertically
   Mirrors the image so the top becomes the bottom.

.. _bpy.ops.image.rotate_orthogonal:

Rotate 90° Clockwise
   Rotates the image clockwise 90°.
Rotate 90° Counter-Clockwise
   Rotates the image counter-clockwise 90°.
Rotate 180°
   Rotates the image 180°.


.. _bpy.ops.image.pack:

Pack
====

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Pack`

Pack the image into the blend-file.
See :ref:`pack-unpack-data`.


.. _bpy.ops.image.unpack:

Unpack
======

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Unpack`

Unpack the image to a drive.


.. _bpy.ops.palette.extract_from_image:

Extract Palette
===============

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Extract Palette`

Extract a :ref:`Color Palette <bpy.types.PaletteColor>` from the image for use by painting tools.


.. _bpy.ops.gpencil.image_to_grease_pencil:

Generate Grease Pencil
======================

.. reference::

   :Mode:      All Modes
   :Menu:      :menuselection:`Image --> Generate Grease Pencil`

Create a :doc:`Grease Pencil </grease_pencil/index>` object using the currently selected image as a source.
