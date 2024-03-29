
*****
Proxy
*****

As projects involve increasingly high-resolution footage,
the performance of the video preview can decrease drastically.
To combat this, Blender can generate proxies -- copies of the original footage stored at a
lower quality and/or resolution -- to maintain a smooth editing experience without
compromising visual fidelity in the end result.

The quickest way to set up proxies for videos is to simply select a
:ref:`Proxy Render Size <bpy.types.SpaceSequenceEditor.proxy_render_size>`
in the *View* tab (visible when the editor is in *Preview* or
*Sequencer & Preview* mode). This will automatically enable the selected
proxy resolution in all the strips and start generating the downscaled video files.

You can use the *Proxy* tab if you want to configure proxies in more detail
(or create proxies for image sequences).

Proxy Settings
==============

.. reference::

   :Panel:     :menuselection:`Sidebar region --> Proxy --> Proxy Settings`

Contains scene-wide proxy settings.

.. _bpy.types.SequenceEditor.proxy_storage:

Storage
   How proxies are stored for the project.

   :Per Strip: Each strip can specify where to store its proxies (see below).
   :Project: All proxies are stored in one directory.

      .. _bpy.types.SequenceEditor.proxy_dir:

      Proxy Directory
         The location to store the proxies for the project.

.. _bpy.ops.sequencer.enable_proxies:

Set Selected Strip Proxies
   Shows a pop-over that lets you choose the resolution(s) to generate
   and whether to overwrite existing proxy files. Once you confirm with the *Set* button,
   your choices are applied to the selected strips. You can view and tweak the
   settings for individual strips in the *Strip Proxy & Timecode* panel (see below).

   In the *Preview* mode, where the *Proxy* tab is not available,
   this is instead done through the menu :menuselection:`View --> Proxy --> Setup`.

.. _bpy.ops.sequencer.rebuild_proxy:

Rebuild Proxy and Timecode Indices
   Generates proxies and time indices for the selected strips.

   In the *Preview* mode, where the *Proxy* tab is not available,
   this is instead done through the menu :menuselection:`View --> Proxy --> Rebuild`.

.. _bpy.types.SequenceProxy:
.. _bpy.types.MovieSequence.use_proxy:

Strip Proxy & Timecode
======================

.. reference::

   :Panel:     :menuselection:`Sidebar region --> Proxy & Timecode --> Strip Proxy & Timecode`

.. figure:: /images/video-editing_sequencer_sidebar_proxy_panel.png
   :align: right

Contains strip-specific proxy settings. The checkbox in the header can be used to
enable/disable proxy generation.

Custom Proxy
   Directory
      By default, all generated proxy videos are stored to
      the folder ``<path of original footage>/BL_proxy/<clip name>``,
      but this can be changed to a custom directory using this option.
   File
      Allows you to use preexisting proxies.

.. _bpy.types.SequenceProxy.build:

Resolutions
   The resolution(s) of the proxy videos to generate; multiple sizes can be selected.

.. _bpy.types.SequenceProxy.use_overwrite:

Overwrite
   Whether to overwrite existing proxy files or keep them.

.. _bpy.types.SequenceProxy.quality:

Quality
   The video/image quality for proxies.

.. _bpy.types.SequenceProxy.timecode:

:term:`Timecode` Index
   When you are working with footage directly copied from a camera without preprocessing it,
   there might be numerous artifacts, mostly due to seeking to a given frame in the sequence.
   This happens because such footage usually does not have correct frame rate values in the file header.
   This issue can still arise when the source clip has the same frame rate as the scene settings.
   In order for Blender to correctly calculate the frames and frame rate there are two possible solutions:

   #. Preprocess your video with e.g. MEncoder to repair the file header and insert the correct keyframes.
   #. Use the Proxy/Timecode option in Blender.

   :None: Do not use any timecode.
   :Record Run: Use images in the order they are recorded.
   :Free Run: Use global timestamp written by recording device.
   :Free Run (Rec Date):
      Interpolate a global timestamp using the record date and time written by recording device.
   :Record Run No Gaps:
      Similar to *Record Run*, but ignores the timecode given in the file header,
      changes in frame rate, or frame dropouts.

   .. note::

      Record Run is the *Timecode Index* which usually is best to use, but if the source file is totally damaged,
      *Record Run No Gaps* will be the only chance of getting an acceptable result.
