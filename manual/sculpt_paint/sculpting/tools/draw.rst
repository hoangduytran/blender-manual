
****
Draw
****

.. reference::

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Draw`
   :Shortcut:  :kbd:`X`

Moves vertices inward or outward, based the average vertex normals within the brush radius.
This is a very default behavior for sculpting and can be used in most cases.

It is common to use this particular brush with heavy customization for creating many custom brushes.

Brush Settings
==============

.. note::
   More info at :ref:`sculpt-tool-settings-brush-settings-general` brush settings
   and on :ref:`sculpt-tool-settings-brush-settings-advanced` brush settings.

VDM Displacement
================

*Vector Dispalcement Maps* are supported for the *Draw* brush to insert complex & overhanging shapes.
Unlike regular displacement, this uses all 3 color channels of the image
to displace geometry in three directions instead of just one.

.. figure:: /images/sculpt-paint_sculpt_vdm_example.png
   :width: 580px

   Example of a horn VDM brush being used on the monkey object.

To use this feature, enable :ref:`Vector Displacement <bpy.types.Brush.use_color_as_displacement>` in the texture panel.
All :ref:`stroke methods <bpy.types.Brush.stroke_method>` are supported, but the recommended behavior is *Anchored*.

Ideal images for vector displacement are open EXR files
with :doc:`color clamping </render/materials/legacy_textures/colors>` disabled.

.. note::
   This feature is only supported with Area Plane mapping.

.. A demo file with examples, additional information and a premade baking setup can be found here.