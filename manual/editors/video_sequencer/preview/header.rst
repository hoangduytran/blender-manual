
******
Header
******

.. figure:: /images/video-editing_preview_introduction_header.png

   Header in Preview mode.


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
   When enabled, previews the strip's new first/last frame while dragging its left/right handle.

----------

Refresh All
   Reloads external files and refreshes the current frame preview.
   This is useful when you modified an external file or made a change in a scene that Blender
   didn't detect.

----------

Frame Selected
   Pan and zoom the view to focus on the selected image.
Fit Preview in Window :kbd:`Home`
   Pan and zoom the view so that the entire video is visible.
   This enables *Zoom to Fit*.
Zoom to Border :kbd:`Shift-B`
   Click and drag a rectangle to zoom to it.
Fractional Zoom
   Resize the preview in steps from 1:8 to 8:1.
Zoom to Fit
   As long as this option is enabled, the preview will automatically zoom to keep the
   video size synchronized with the editor size.

----------

Proxy
   See :doc:`/editors/video_sequencer/sequencer/sidebar/proxy`.

----------

Sequence Render Image
   Show the current frame preview as a Render Result where you can save it as an image file.
Sequence Render Animation
   Save previews of the frames in the scene range (or the preview range, if active) to a video file
   or a series of image files. See the :doc:`/render/output/properties/output` panel for details.

.. note::
   *Sequence Render Image* and *Sequence Render Animation* don't render the final video by default --
   specifically, they don't render Scene Strips, instead using the preview's
   :doc:`shading mode </editors/3dview/display/shading>` (which is initially Solid).

   To output a video where the Scene Strips are rendered, use the *Render* menu in the top-bar,
   or change :menuselection:`Sidebar --> View --> Scene Strip Display --> Shading` to *Rendered*.

----------

.. _bpy.ops.sequencer.export_subtitles:

Export Subtitles
   Exports :doc:`Text strips </video_editing/edit/montage/strips/text>`,
   which can act as subtitles, to a `SubRip <https://en.wikipedia.org/wiki/SubRip>`__ file (``.srt``).
   The exported file contains all Text strips in the video sequence.

----------

Toggle Sequencer/Preview :kbd:`Ctrl-Tab`
   Switch the editor mode between *Sequencer* and *Preview*.

----------

Area
   Area controls. See the :doc:`user interface </interface/window_system/areas>`
   documentation for more information.


Select Menu
===========

See :doc:`/video_editing/edit/montage/selecting`.

Strip Menu
==========

See :doc:`/video_editing/edit/montage/editing`.

Image Menu
==========

Clear
   Resets the position, rotation, or scale of the selected images.
Apply
   Scale to Fit
      Resizes the selected images so that they're as large as possible while still
      fitting completely inside the video. They don't get cropped, and their aspect ratio
      stays the same.

   Scale to Fill
      Resizes the selected images to that they fill the entire video space.
      They may get cropped, but their aspect ratio stays the same.

   Stretch to Fill
      Resizes the selected images to match the video dimensions.
      They don't get cropped, but their aspect ratio may change.


Pivot Point
===========

See :doc:`/editors/video_sequencer/preview/controls/pivot_point`.


Display Mode
============

See :doc:`/editors/video_sequencer/preview/display/display_mode`.


Display Channels
================

Color & Alpha
   Display the preview image with transparency over a checkerboard pattern.
Color
   Ignore the transparency of the preview image (fully transparent areas will be black).


Gizmos
======

See :doc:`/editors/video_sequencer/preview/display/gizmos`.

Overlays
========

See :doc:`/editors/video_sequencer/preview/display/overlays`.
