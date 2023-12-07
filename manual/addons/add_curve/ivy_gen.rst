
*******
Ivy Gen
*******

Adds generated ivy to a mesh object starting at the 3D Cursor.

Based on the wonderful code by Thomas Luft and
his original `IvyGen program <http://graphics.uni-konstanz.de/~luft/ivy_generator/>`__.

.. figure:: /images/addons_add-curve_ivy-gen_example.jpg
   :align: center
   :width: 640px


Activation
==========

- Open Blender and go to Preferences then the Add-ons tab.
- Click Add Curve then Ivy Gen to enable the script.


Interface
=========

.. figure:: /images/addons_add-curve_ivy-gen_ui.jpg
   :align: right
   :width: 220px

Located in the :menuselection:`3D Viewport --> Sidebar --> Create` tab.

Add Default Ivy
   Creates ivy using the default parameters.

The Update Ivy operator is separate from the main menu and appears in the 3D Viewport's
:ref:`bpy.ops.screen.redo_last` panel.
You can adjust settings in the panel and press the *Update Ivy* button to update parameters.


Instructions
============

#. Select the object you want to grow ivy on.
#. Enter Edit Mode and select a vertex that you want the ivy to spawn from.
#. Snap the cursor to the selected vertex.
#. Enter Object Mode and with the object selected go to:
   :menuselection:`Sidebar --> Create --> Ivy Generator`, adjust settings, and choose *Add New Ivy*.

   This will generate your initial Ivy Curve and Leaves.
#. Use the *Update Ivy* in the :ref:`bpy.ops.screen.redo_last` panel
   after making small changes to parameters to adjust the ivy to the desired look.

.. reference::

   :Category: Add Curve
   :Description: Adds generated ivy to a mesh object starting at the 3D Cursor.
   :Location: :menuselection:`Sidebar --> Create tab`
   :File: add_curve_ivygen.py
   :Author: testscreenings, PKHG, TrumanBlending
   :Maintainer: Vladimir Spivak (cwolf3d)
   :License: GPL
   :Support Level: Community
   :Note: This add-on is bundled with Blender.
