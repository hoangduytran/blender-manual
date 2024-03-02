
******
Header
******

.. figure:: /images/video-editing_preview_introduction_header.png

   Sequencer Display header.


.. _bpy.types.SpaceSequenceEditor.show:

View Menu
=========

Toolbar :kbd:`T`
   Show or hide the :ref:`Toolbar <ui-region-toolbar>`.
Sidebar :kbd:`N`
   Show or hide the :ref:`Sidebar <ui-region-sidebar>`.
Tool Settings
   Show or hide the settings for the currently selected tool.

----------

Preview During Transform
   Show a preview of the start or end frame while transforming a strip's start/end handles.

----------

Refresh All
   To force Blender to re-read in files, and to force a re-render of the 3D Viewport,
   click the *Refresh Sequencer* button.
   Blender will update and synchronize all cached images and compute the current frame.

   Certain operations, like moving an object in the 3D Viewport, may not force the *Sequencer*
   to call for a refresh of the rendered image (since the movement may not affect the rendered image).
   If an image or video, used as a strip, is changed by some application outside of Blender,
   Blender has no real way of being notified from your operating system.

----------

Frame Selected
   Zoom and position the bounding box of the selected image into the center of the preview.
Fit Preview in Window :kbd:`Home`
   Resize the preview so that it fits in the area.
Zoom to Border :kbd:`Shift-B`
   Click and drag to draw a rectangle and zoom to this rectangle.
Fractional Zoom
   Resize the preview in steps from 1:8 to 8:1.
Zoom to Fit
   Automatically zoom preview image to make it fully fit the region.

----------

Proxy
   See :doc:`/editors/video_sequencer/sequencer/sidebar/proxy`.

----------

Sequence Render Image
   Render the image at the current frame.
Sequence Render Animation
   Render timeline from Preview Start to Preview End Frame to a Video file or series of images.

----------

.. _bpy.ops.sequencer.export_subtitles:

Export Subtitles
   Exports :doc:`Text strips </video_editing/edit/montage/strips/text>`,
   which can act as subtitles, to a `SubRip <https://en.wikipedia.org/wiki/SubRip>`__ file (``.srt``).
   The exported file contains all Text strips in the video sequence.

----------

Toggle Sequencer/Preview :kbd:`Ctrl-Tab`
   Switch the editor display type between Sequencer and Preview.

----------

Area
   Area controls, see the :doc:`user interface </interface/window_system/areas>`
   documentation for more information.


Display Mode
============

See :doc:`/editors/video_sequencer/preview/display/display_mode`.


Display Channels
================

Color & Alpha
   Display preview image with transparency over checkerboard pattern.
Color
   Ignore transparency of preview image (fully transparent areas will be black).


Overlays
========

See :doc:`Preview Overlays </editors/video_sequencer/preview/display/overlays>`.
