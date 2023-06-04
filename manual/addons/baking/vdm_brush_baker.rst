***************
VDM Brush Baker
***************

This is a small add-on that makes it easy to create vector displacement map (aka VDM) brushes in Blender.
Sculpting setups and the brushes can be created with one click.

Activation
==========

- Open Blender and go to Preferences then the Add-ons tab.
- Switch the category to "Baking"
- Enable the "VDM Brush Baker" addon.

Interface
=========

Located in the :menuselection:`3D Viewport --> Sidebar --> Tools`.

Usage
=====

Use the "Create Sculpting Plane" button for an optimal startign setup for sculpting your own VDM brush.

Use the "Render and Create VDM Brush" button to covnert bake the plane into a new brush.
The brush will be added with all relevant options and a vector displacement map
is saved near the blender file as an Open EXR file (or a 'tmp' folder if the blender file wasn't saved).
New brushes can be found as Draw brushes in sculpt mode.
The add-on won't create any preview images for these brushes.

Tips
----

- While Sculpting make sure to mask the borders of the plane for a better result.
- If your VDM brush gets cut off at the corners,
  you can increase the size inside the texture panel of the brush settings to 1.1 or 1.2 for each axis.
- A vdm-resolution of 512 px or lower is usually enough. Unless you have extremely detailed sculptings.
