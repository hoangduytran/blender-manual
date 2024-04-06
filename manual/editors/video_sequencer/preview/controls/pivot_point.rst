.. _bpy.types.SequencerToolSettings.pivot_point:
.. |pivot-icon| image:: /images/editors_3dview_controls_pivot-point_menu.png

***********
Pivot Point
***********

.. reference::

   :Header:    |pivot-icon| :menuselection:`Pivot Point`
   :Shortcut:  :kbd:`Period`

The Pivot Point is the point around which images are rotated and scaled.
It's indicated by the position of the selected tool's gizmo.

.. seealso::
   The :doc:`/editors/3dview/controls/pivot_point/index` of the 3D Viewport

Bounding Box Center
   Use the center of the rectangle that's wrapped as tightly as possible around the selected
   images' origin points.
Median Point
   Use the averaged-out position of the selected images' origin points.
2D Cursor
   Use the location of the :ref:`2D Cursor <editors_sequencer_preview_2d-cursor>`,
   for when you want to specify the pivot point by hand.
Individual Origins
   Rotate/scale each image around its own origin, rather than rotating/scaling
   all of them around the same single point like the other options do.
