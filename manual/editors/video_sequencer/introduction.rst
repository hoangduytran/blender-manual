.. index:: Editors; Video Sequencer

************
Introduction
************

The Video Sequencer allows you to place images, videos, sounds, and scenes
on a timeline and combine them into a new video. This section only describes its UI;
to read more about its usage, see the :doc:`Video Editing </video_editing/index>` section.


Editor Layout
=============

The Video Sequencer is composed of multiple regions.
They are described in more detail in the next sections.
Figure 1 shows the combined *Sequencer & Preview* view type.
This view can be broken up into the following regions:

.. figure:: /images/editors_vse_overview.svg

   Figure 1: Sequence Editor shown in the Sequencer & Preview view type.

Header
   This region displays menus and buttons for interacting with the editor.
   The header changes slightly depending on the selected view type (see below).
Preview
   This region shows the output of the Sequencer at the time of the Playhead.
Sequencer
   This region shows a timeline for managing the montage of strips.
Sidebar
   This region shows the properties of the active strip.
   It's divided into panels and tabs. Toggle on or off with :kbd:`N`.
Toolbar
   This region shows a list of tools. Toggle on or off with :kbd:`T`.


.. _bpy.types.SpaceSequenceEditor.view_type:

View Types
==========

The Video Sequencer has three view types which can be
changed with the View Type selector (see figure 1; top left).

.. figure:: /images/editors_vse_view_types.svg

   Figure 2: Three view types for the Video Sequence Editor

Sequencer
   View timeline and strip properties.
Preview
   View preview window and preview properties.
Sequencer & Preview
   Combined view of preview and timeline and their properties.

.. tip::

   It's possible to have multiple Video Sequencers in one workspace,
   each with its own view type.


Performance
===========

Playback performance can be improved in several ways.

The method with the most impact is to allow the Video Sequencer to cache the playback.
There are two levels of cache: a memory cache, which is enabled by default
(and can be enlarged if RAM allows), and a disk cache, which is slower but has more capacity.
Both of these can be configured in the :ref:`Preferences <prefs-system-video-sequencer>`.

Another way to improve performance is by using :ref:`Strip Proxies <bpy.types.SequenceProxy>`.
These are copies of source images and videos with a lower resolution and/or quality,
making them faster to load than the originals.
