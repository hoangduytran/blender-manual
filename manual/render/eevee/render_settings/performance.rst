
***********
Performance
***********

.. reference::

   :Panel:     :menuselection:`Properties --> Render --> Performance`

.. _bpy.types.RenderSettings.use_high_quality_normals:

High Quality Normals
   Uses higher precision normals and tangents which can improve
   visual quality for dense meshes with high frequency textures at the cost of memory.


Memory
======

.. _bpy.types.SceneEEVEE.shadow_pool_size:

Shadow Pool
   A bigger pool size allows for more shadows in the scene
   but might not fit into GPU memory and decreases performance.
   Increasing the size might fix the *Shadow buffer full* error.

   .. seealso::
      :ref:`Shadow documentation <bpy.types.Light.shadow>`

.. _bpy.types.SceneEEVEE.gi_irradiance_pool_size:

Light Probes Volume Pool
   A bigger pool size allows for more irradiance grids in the scene
   but might not fit into GPU memory and decreases performance.


Viewport
========

.. _bpy.types.RenderSettings.preview_pixel_size:

Pixel Size
   Option to control the resolution for viewport rendering.
   Allows you to speed up viewport rendering, which is especially useful for displays with high DPI.

.. --- copy below this line ---

Compositor
==========

.. _bpy.types.RenderSettings.compositor_device:

Device
   The device used for compositing.

   :CPU: Use the CPU for compositing.
   :GPU: Use the GPU for compositing.

.. _bpy.types.RenderSettings.compositor_precision:

Precision
   The precision of compositor intermediate result.

   :Auto: Use full precision for final renders, half precision otherwise.
   :Full: Use full precision for final renders and viewport.