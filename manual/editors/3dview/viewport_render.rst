
***************
Viewport Render
***************

Viewport rendering lets you create quick preview renders from the current viewpoint
(rather than from the active camera, as would be the case with a regular render).

You can use *Viewport Render* to render both images and animations.

Below is a comparison between the Viewport render and a final render using
the Cycles Renderer.

.. list-table:: Model by © 2016 pokedstudio.com

   * - .. figure:: /images/editors_3dview_viewport-render_example-workbench-render.jpg
          :width: 320px

          Viewport render using Solid Mode.

     - .. figure:: /images/editors_3dview_viewport-render_example-eevee-render.jpg
          :width: 320px

          Viewport render using Material Preview Mode.

     - .. figure:: /images/editors_3dview_viewport-render_example-cycles-render.jpg
          :width: 320px

          Full render.

.. note::

   Viewport rendering only works for the Workbench and EEVEE render engines.
   It's not supported for Cycles.

.. tip::

   Disable overlays to get a render without "clutter" like rigs, empties and so on.


Settings
========

For the most part, *Viewport Render* uses the current viewport settings.
Some settings are located in the properties of the render engine
that is used to render the view.

Solid mode uses the render settings of Workbench;
Material Preview mode uses the render settings of EEVEE.

Additionally, some output settings are used too:

- Resolution
- Aspect
- Output path
- File format


Rendering
=========

Activating *Viewport Render* will render from the current active view.
This means that if you are not in an active camera view,
a virtual camera is used to match the current perspective.
To get an image from the camera point of view,
enter the active camera view with :kbd:`Numpad0`.

As with a normal render, you can abort it with :kbd:`Esc`.

.. _bpy.ops.render.opengl:

Render a Still Image
   To render a still image, use :menuselection:`3D Viewport --> View --> Viewport Render Image`.
Render an Animation
   To render an animation, use :menuselection:`3D Viewport --> View --> Viewport Render Animation`.

.. tip::

   You can limit the viewport render to a particular region with
   :ref:`Render Regions <editors-3dview-navigate-render-region>`.
