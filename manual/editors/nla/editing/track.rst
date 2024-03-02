
*****
Track
*****

.. _bpy.ops.nla.tracks_add:

Add
===

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Track --> Delete`

Add a new NLA-Track on top of the selected object.


Add Above Selected
==================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Track --> Add Above Selected`

Add a new NLA-Track just above the selected NLA-track.


.. _bpy.ops.nla.tracks_delete:

Delete Tracks
=============

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Track --> Delete`

Delete the selected NLA track and all strips that it contains.


Move
====

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Track --> Move`

To Top
   Move selected track to the top of the tracks.
Up
   Move selected track one track up.
Down
   Move selected track one track down.
To Bottom
   Move selected tracks to the bottom of the tracks.


.. _bpy.ops.anim.channels_clean_empty:

Remove Empty Animation Data
===========================

.. reference::

   :Editor:    Nonlinear Animation
   :Menu:      :menuselection:`Track --> Remove Empty Animation Data`

This operator removes AnimData data-blocks (restricted to only those
which are visible in the animation editor where it is run from) which are "empty"
(i.e. that is, have no active action, drivers, and NLA tracks or strips).

It is sometimes possible to end up with a lot of data-blocks which have old and
unused Animation Data containers still attached.
This most commonly happens when doing motion graphics work
(i.e. when some linked-in objects may have previously been used to develop a set of reusable assets),
and is particularly distracting in the NLA Editor.
