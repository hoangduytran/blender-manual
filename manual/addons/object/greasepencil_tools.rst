
*******************
Grease Pencil Tools
*******************

A set of tools for Grease Pencil drawing.


Activation
==========

- Open Blender and go to Preferences then the Add-ons tab.
- Click Object then Grease pencil tools to enable the script.


Tools
=====

Box Deform
----------

Create a deformation box around Grease Pencil strokes.
Press :kbd:`Ctrl-T` to launch the deformation mode.

The operational scope depends on the mode:

- Object Mode: the whole Grease Pencil object is deformed.
- Edit Mode: deform the selected points.
- Draw Mode: deform the last strokes only.

Shortcuts available during deformation:

- :kbd:`Spacebar`/ :kbd:`Return` to confirm.
- :kbd:`Delete`/ :kbd:`Backspace`/ :kbd:`Ctrl-T`/ :kbd:`Tab` (twice) to cancel.
- :kbd:`M` to toggle between Linear and Spline mode.
- :kbd:`1-9` to set the subdivision level of the box.
- :kbd:`Ctrl-Left`/ :kbd:`Ctrl-Right` to subdivide the box incrementally on the X axis and
  :kbd:`Ctrl-Up`/ :kbd:`Ctrl-Down` on the Y axis.


Rotate Canvas
-------------

Perform a rotation of the view in free navigation or active camera in camera view.

- Maintain :kbd:`Ctrl-Alt-MMB` to rotate view (customizable in add-on preferences).
- Click and release immediately to reset view.


Layer Navigator
---------------

Continuous press on :kbd:`Y` shortcut call a customized layer popup with following features:

- Active layer always pop under mouse when called.
- Active layer is changed by hovering, without any click.
- Layers can be reordered with simple drag-and-drop.
- Layer opacity, hide and lock states can be tweaked in popup.
- Placing mouse outside popup limits will fade inactive layers, useful to quickly inspect content.
- The plus button on the right adds a new layer.

Extra shortcuts are enabled while layer navigator is up:

- :kbd:`H` toggle all hide.
- :kbd:`L` toggle all lock.
- :kbd:`T` toggle auto-lock.
- :kbd:`X` toggle In Front value of the object.
- :kbd:`RMB` or :kbd:`Esc` to reset original active layer.

Layers box height, width, font size, and left-handed mode are customizable in add-on preferences.


Timeline Scrub
--------------

Call a timeline popup at mouse position to scrub without leaving the 3D viewport.

Default shortcut to call the timeline is :kbd:`Alt-MMB`.
The shortcut enable the scrubbing when hovering timeline editors as well (dopesheet, sequencer, etc).

Scene start/end and keyframes are represented with symbols on the timeline.

While scrubbing, pressing :kbd:`Ctrl` key Snap time cursor on keyframes.

There are several settings to customize visual aspect and behavior in addon preferences:

- "Always Snap" checkbox invert the snapping behavior.
- Special "Rolling" mode is available. It displays keyframes with a constant spacing, discarding timing data when
  scrubbing back and forth. This is useful for quick flipping between keyframes.
- Filter to restrict the key display and snapping to Grease Pencil frames only.
- Change shortcut and choose to propagate it to timeline editors
- Customizable colors, frame spacing and amount of displayed information.

Straighten Stroke
-----------------

Straighten the stroke between first and last point.
The influence can be tweaked in the redo panel.

The scopes for this tool are:

- Last stroke in Grease Pencil Paint Mode.
- Selected stroke in Grease Pencil Edit Mode.

.. tip:: Straight Influence Reset

   The influence percentage is stored for next use.
   Use :kbd:`Shift-LMB` on the button to reset influence to full.


Brush Pack Installer
--------------------

Install included Grease Pencil `textured brush pack
<https://cloud.blender.org/p/gallery/5f235cc297f8815e74ffb90b>`__ (made by Daniel Martinez Lara).
This is available in Draw Mode in the :ref:`Brushes panel <grease-pencil-draw-common-options>`.

.. note::

   This feature will be removed once the :doc:`Blender Asset Browser </editors/asset_browser>`
   has support for brushes.

.. reference::

   :Category: Object
   :Description: Set of tools for Grease Pencil drawing.
   :Location: :menuselection:`3D Viewport --> Sidebar --> Grease Pencil`
   :File: greasepencil_addon folder
   :Author: Samuel Bernou, Antonio Vazquez, Daniel Martinez Lara, Matias Mendiola
   :License: GPL
   :Note: This add-on is bundled with Blender.
