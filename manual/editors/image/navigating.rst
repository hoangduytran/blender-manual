
**********
Navigating
**********

Panning can be done by dragging with :kbd:`MMB`.

Zooming can be done using :kbd:`Wheel` or :kbd:`NumpadPlus`/:kbd:`NumpadMinus`.


.. _editors-image-navigate-gizmos:

Gizmos
======

Next to the Sidebar region at the top, there are gizmos that allow panning
and zooming more comfortably when e.g. no mouse wheel is available.


View Menu
=========

Region Controls
   Adjust which regions are visible in the Image editor.
Update Automatically
   Instantly update any other editors that are affected by changes in this Image Editor.
   When disabled, the other editors may display outdated information until they're manually refreshed
   (e.g. by orbiting for the 3D Viewport).
Show Metadata
   Displays metadata about the selected Render Result. See the Output tab's
   :doc:`/render/output/properties/metadata` panel to change what metadata to include.
Display Texture Paint UVs
   Toggles UVs in Paint Mode. The object must be in Texture Paint Mode or Edit Mode for the UVs to be visible.
Zoom In/Out :kbd:`Wheel`
   Adjusts the zoom level.
Fractional Zoom
   - Zoom 1:8 :kbd:`Numpad8`
   - Zoom 1:4 :kbd:`Numpad4`
   - Zoom 1:2 :kbd:`Numpad2`
   - Zoom 1:1 :kbd:`Numpad1`
   - Zoom 2:1 :kbd:`Ctrl-Numpad2`
   - Zoom 4:1 :kbd:`Ctrl-Numpad4`
   - Zoom 8:1 :kbd:`Ctrl-Numpad8`
Frame All :kbd:`Home`
   Pans and zooms the view so that the image is centered and fully visible.
Frame All Fit :kbd:`Shift-Home`
   Same as *Frame All*, but uses as much of the editor's space as possible
   (rather than leaving some margin around the image).
Center View to Cursor
   Pan the view so that the 2D cursor is at the center of the editor.
Render Region :kbd:`Ctrl-B`
   Only available when viewing the Render Result.
   See :ref:`Render Region <editors-3dview-navigate-render-region>`.
Clear Render Region :kbd:`Ctrl-Alt-B`
   Only available when viewing the Render Result.
   See :ref:`Render Region <editors-3dview-navigate-render-region>`.
Render Slot Cycle Next/Previous :kbd:`J`/:kbd:`Alt-J`
   Switch to the next/previous render slot (that contains a render).
Area
   Adjust the :doc:`area </interface/window_system/areas>` the Image Editor is in.
