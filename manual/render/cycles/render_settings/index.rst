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
