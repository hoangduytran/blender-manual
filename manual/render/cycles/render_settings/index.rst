.. _bpy.types.CyclesRenderSettings:

###################
  Render Settings
###################

.. reference::

   :Panel:     :menuselection:`Render`

.. _bpy.types.CyclesRenderSettings.feature_set:

Feature Set
   Selects which Cycles rendering features are available.

   :Supported:
      Enables only fully supported and stable rendering features.
   :Experimental:
      Enables additional features that are still in development or not fully supported.
      Selecting this option may expose extra settings in the user interface.
      These features may be incomplete, unstable, or subject to change in future Blender versions.

      Currently, :doc:`/render/cycles/object_settings/adaptive_subdiv` is the only experimental feature.

.. _bpy.types.CyclesRenderSettings.shading_system:

Open Shading Language
   Enables the use of :doc:`/render/cycles/osl/index` which allows custom shading using shader scripts.
   When OSL is enabled, you can:

   - Use OSL shader nodes in materials using the :doc:`Script Node </render/shader_nodes/script>`.
   - Write custom shading logic that is not possible with built-in Cycles nodes.

   Limitations:

   - OSL is supported only when rendering with the *CPU* or with the
     :ref:`OptiX <render-cycles-gpu-optix>` GPU Compute backend.
   - Rendering performance is typically slower than with built-in nodes due to shader compilation and interpretation.
   - Some features, such as baking and certain volume shaders, may not work with OSL.

.. toctree::
   :maxdepth: 2

   sampling.rst
   light_paths.rst
   volumes.rst
   subdivision.rst
   hair.rst
   simplify.rst
   motion_blur.rst
   film.rst
   performance.rst
   grease_pencil.rst
