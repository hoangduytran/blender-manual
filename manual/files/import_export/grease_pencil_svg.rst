
**********************************
Import/Export SVG as Grease Pencil
**********************************

The Scalable Vector Graphics (SVG) format is use for interchanging vector based illustrations between applications
and is supported by vector graphics editors such as Inkscape, and modern browsers among others.

.. warning:: The exporter only works in Object Mode.


.. _bpy.ops.wm.gpencil_import_svg:

Import
======

.. reference::

   :menu: :menuselection:`File --> Import --> SVG as Grease Pencil`

Options
-------

Resolution
   Resolution for generated strokes.

Scale
   Generated strokes scale.


.. _bpy.ops.wm.gpencil_export_svg:

Export
======

.. reference::

   :menu: :menuselection:`File --> Export --> Grease Pencil as SVG`

Options
-------

Object
   Determine which objects include in the export.

   :Active: Export only the active Grease Pencil object.
   :Selected: Export all selected Grease Pencil objects.
   :Visible: Export all visible Grease Pencil object in the scene.

Sampling
   Precision for the stroke sampling. Low values mean a more accurate result.

Fill
   When enabled, Export the Grease Pencil strokes fill.

Normalize
   When enabled, Export strokes with constant thickness.

Clip Camera
   When enabled, and camera view is active export only the strokes clipped from camera view.
