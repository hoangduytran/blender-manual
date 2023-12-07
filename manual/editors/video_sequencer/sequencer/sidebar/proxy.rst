
*****
Proxy
*****

As projects involve increasingly high-resolution footage,
the performance of the video preview can decrease drastically.
To combat this, proxies are used to maintain a smooth editing experience without compromising visual fidelity.

Proxies are optimized, lower-resolution, versions of original video files
that are used as a substitute of the high-quality source videos to increase playback performance.
For rendering out the final project, the original, high quality source files are used.


Proxy Settings
==============

.. reference::

   :Panel:     :menuselection:`Sidebar region --> Proxy & Timecode --> Proxy Settings`

.. _bpy.types.SequenceEditor.proxy_storage:

Storage
   Defines whether the proxies are for individual strips or the entire sequence.

   :Per Strip: Proxies are stored in the directory of the input.
   :Project: All proxies are stored in one directory.

      .. _bpy.types.SequenceEditor.proxy_dir:

      Proxy Directory
         The location to store the proxies for the project.

.. _bpy.ops.sequencer.enable_proxies:

Set Selected Strip Proxies
   Set proxy size and overwrite flag for all selected strips.

.. _bpy.ops.sequencer.rebuild_proxy:

Rebuild Proxy and Timecode Indices
   Generates Proxies and Timecodes for all selected strips,
   same as doing :menuselection:`Strip --> Rebuild Proxy and Timecode Indices`.


.. _bpy.types.SequenceProxy:
.. _bpy.types.MovieSequence.use_proxy:

Strip Proxy & Timecode
======================

.. reference::

   :Panel:     :menuselection:`Sidebar region --> Proxy & Timecode --> Strip Proxy & Timecode`

.. figure:: /images/video-editing_sequencer_sidebar_proxy_panel.png
   :align: right

Once you have chosen the :term:`Proxy`/:term:`Timecode` options,
you need to select all strips for which you want proxies to be built.
Then use :menuselection:`Strip --> Rebuild Proxy and Timecode Indices`, or button in `Proxy Settings`_ panel.
Once all proxies are built, they will be ready to use.

In order to use proxies, you have to select matching
:ref:`Proxy Render Size <bpy.types.SpaceSequenceEditor.proxy_render_size>` in
the Sequencer preview Sidebar panel.

Custom Proxy
   Directory
      By default, all generated proxy images are storing to
      the ``<path of original footage>/BL_proxy/<clip name>`` folder,
      but this location can be set by hand using this option.
   File
      Allows you to use preexisting proxies.

.. _bpy.types.SequenceProxy.build:

Resolutions
   Buttons to control how big the proxies are.
   The available options are 25%, 50%, 75%, 100 percent of original strip size.

.. _bpy.types.SequenceProxy.use_overwrite:

Overwrite
   Saves over any existing proxies in the proxy storage directory.

.. _bpy.types.SequenceProxy.quality:

Quality
   Defines the quality of the images used for proxies.

.. _bpy.types.SequenceProxy.timecode:

Timecode Index
   When you are working with footage directly copied from a camera without preprocessing it,
   there might be bunch of artifacts, mostly due to seeking a given frame in sequence.
   This happens because such footage usually does not have correct frame rate values in their headers.
   This issue can still arise when the source clip has the same frame rate as the scene settings.
   In order for Blender to correctly calculate frames and frame rate there are two possible solutions:

   #. Preprocess your video with e.g. MEncoder to repair the file header and insert the correct keyframes.
   #. Use Proxy/Timecode option in Blender.

   :None: Do not use any timecode.
   :Record Run: Use images in the order they are recorded.
   :Free Run: Use global timestamp written by recording device.
   :Free Run (Rec Date):
      Interpolate a global timestamp using the record date and time written by recording device.
   :Record Run No Gaps:
      Record run, but ignore timecode, changes in frame rate or dropouts.

   .. note::

      Record Run is the timecode which usually is best to use, but if the source file is totally damaged,
      *Record Run No Gaps* will be the only chance of getting acceptable result.
