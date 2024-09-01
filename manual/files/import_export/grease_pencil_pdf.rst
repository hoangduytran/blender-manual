.. _bpy.ops.wm.grease_pencil_export_pdf:

*****************************
Export Grease Pencil as (PDF)
*****************************

The Portable Document Format (PDF) is use for interchanging PDFs between applications,
it support the export of Grease Pencil animation creating one page in the PDF document for each keyframe selected.

.. warning:: The exporter only works in Object Mode.


Scene Options
-------------

Object
   Determine which objects will be included in the export.

   :Active: Export only the active Grease Pencil object.
   :Selected: Export all selected Grease Pencil objects.
   :Visible: Export all visible Grease Pencil object in the scene.


Export Options
--------------

Frame
   Determine which frames will be included in the export.

   :Active: Export only the active keyframe.
   :Selected: Export all selected keyframes as different PDF pages.
   :Scene: Export all frames as different PDF pages.

.. note:: To enable multi-keyframe selection you must enable Multiframe Edition.
   See :doc:`Multiframe Edition </grease_pencil/multiframe>` for more information.

Sampling
   Precision for the stroke sampling. Low values mean a more accurate result.

Fill
   When enabled, Export the Grease Pencil strokes fill.

Uniform Width
   When enabled, Export strokes with constant thickness.

.. note:: The export of the Grease Pencil strokes is always from camera view.
