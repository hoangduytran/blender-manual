.. _bpy.ops.anim.keying_set:

***********
Keying Sets
***********

.. figure:: /images/editors_timeline_keying-sets.png
   :align: right

   The Active Keying Sets data ID in the Timeline.

Keying Sets are a collection of animated properties that are used to animate
and keyframe multiple properties at the same time.
For example, pressing :kbd:`K` in the 3D Viewport will bring up the available Keying Sets.
Blender will then add keyframes for whichever Keying Set is chosen.
There are some built-in Keying Sets and,
also custom Keying Sets called *Absolute Keying Sets*.
To select and use a Keying Set, set the *Active Keying Set*
in the :ref:`Keying popover <timeline-keying>` in the Timeline header,
or the Keying Set panel, or press :kbd:`Shift-K` in the 3D Viewport.


Keying Set Panel
================

.. reference::

   :Editor:    Properties
   :Panel:     :menuselection:`Scene --> Keying Set`

This panel is used to add, select, manage *Absolute Keying Sets*.

.. figure:: /images/animation_keyframes_keying-sets_scene-keying-set-panel.png

   The Keying Set panel.

Active Keying Set
   The :ref:`List View <ui-list-view>` of Keying Sets in the active scene.

   Add ``+``
      Adds an empty Keying Set.

Description
   A short description of the Keying Set.

Export to File
   Export Keying Set to a Python script ``File.py``.
   To re-add the Keying Set from the ``File.py``, open then run the ``File.py`` from the Text Editor.


Keyframing Settings
-------------------

General Override
   These options control all properties in the Keying Set.
   Note that the same settings in *Preferences* override these settings if enabled.

Active Set Override
   These options control individual properties in the Keying Set.

Common Settings
   Only Needed
      Only insert keyframes where they are needed in the relevant F-Curves.
   Visual Keying
      Insert keyframes based on the visual transformation.
   XYZ to RGB
      For new F-Curves, set the colors to RGB for the property set, Location XYZ for example.


Active Keying Set Panel
=======================

.. reference::

   :Editor:    Properties
   :Panel:     :menuselection:`Scene --> Active Keying Set`

This panel is used to add properties to the active Keying Set.

.. figure:: /images/animation_keyframes_keying-sets_scene-active-keying-set-panel.png

   The Active Keying Set panel.

Paths
   A collection of paths in a :ref:`List View <ui-list-view>` each with a *Data Path* to a property
   to add to the active Keying Set.

   Add ``+``
      Adds an empty path.

Target ID-Block
   Set the ID Type and the *Object IDs* data path for the property.

Data Path
   Set the rest of the Data Path for the property.

Array All Items
   Use *All Items* from the Data Path or select the array index for a specific property.

F-Curve Grouping
   This controls what group to add the channels to.

   Keying Set Name, None, Named Group


.. _bpy.ops.anim.keyingset_button_add:

Adding Properties
=================

.. reference::

   :Menu:      :menuselection:`Context menu --> Add All/Single to Keying Set`
   :Shortcut:  :kbd:`K`

Some ways to add properties to Keying Sets.

:kbd:`RMB` the property in the *User Interface*, then select *Add Single to Keying Set* or *Add All to Keying Set*.
This will add the properties to the active Keying Set, or to a new Keying Set if none exist.

Hover the mouse over the properties, then press :kbd:`K`, to add *Add All to Keying Set*.


.. _whole-character-keying-set:

Whole Character Keying Set
==========================

The built-in *Whole Character* Keying Set is made to keyframe all properties
that are likely to get animated in a character rig. It was also implicitly used by
the :ref:`Old Pose Library system <pose-library-old>`.

In order to determine which bones to add keys for, and which bones to skip,
the Keying Set uses the bone names. The following bone name prefixes will be skipped:

"COR", "DEF", "GEO", "MCH", "ORG", "VIS"
