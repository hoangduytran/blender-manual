
************
Introduction
************

*Sculpt Mode* is similar to *Edit Mode* in that it is used to alter the shape of a drawing,
but Sculpt Mode uses a very different workflow:
Instead of dealing with individual elements (points and edit lines),
an area of the model is altered using a brush.
In other words, instead of selecting a group of points,
Sculpt Mode manipulates the drawing in the brush region of influence.


Sculpt Mode
===========

.. figure:: /images/grease-pencil_modes_sculpting_introduction_mode-selector.png

   3D Viewport Mode selector: Sculpt Mode.

Sculpt Mode is selected from the *Mode* menu in the 3D Viewport header.
Once Sculpt Mode is activated, the Toolbar of the 3D Viewport will change to
Sculpt Mode specific panels.
A red circle will appear and follow the location of the cursor in the 3D Viewport.


Sculpting Options
=================

.. figure:: /images/grease-pencil_modes_sculpting_introduction_sculpting-options.png

   General sculpting options.

Selection Mask
   Sculpt Mode in Grease Pencil allows you to select points or strokes to restrict the effect
   of the sculpting tools to only a certain areas of your drawing.

   You can use the selection tools in the Toolbar for a quick selection.
   You can restrict sculpting only on the selected points or strokes with the Selection mode buttons.

Multiframe
   Sometimes you may need to modify several frames at the same time with the sculpting tools.

   You can activate multiframe edition with the Multiframe button next to the modes selector (faded lines icon).
   See :doc:`Multiframe </grease_pencil/multiframe>` for more information.

Auto-Masking
============

.. figure:: /images/grease-pencil_modes_sculpting_introduction_auto-masking.png

   Auto-Masking settings.

These properties automatically mask geometry based on stroke, layers and materials under the cursor.
It's an quick alternative to frequent manual masking.
These masks are initialized on every new tool usage. They are also never visible as an overlay.

These properties can be accessed via a :ref:`bpy.types.UIPieMenu` by pressing :kbd:`Shift-Alt-A`.

All auto-masking modes can be combined, which makes the generated auto-mask more specific.
For example it's possible to auto-mask strokes that use specific layer and material while excluding others.

Strokes
   Only strokes that are under the cursor when you started the tool are affected.

Layers
   Only strokes on the same layers that are under the cursor when you started the tool are affected.

Materials
   Only materials with the same material that are under the cursor when you started the tool are affected.

Active Layer
   Only the strokes on the active layer are affected.

Active Material
   Only the strokes with the active material are affected.


Keyboard Shortcuts
==================

- Invert stroke toggle :kbd:`Ctrl`
- Change active material :kbd:`U`
- Auto-masking :kbd:`Shift-Alt-A`
