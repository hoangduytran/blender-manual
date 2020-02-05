
********
Settings
********

Todo


Border Collisions
=================

Todo.


.. _bpy.types.FluidDomainSettings.alpha:
.. _bpy.types.FluidDomainSettings.beta:
.. _bpy.types.FluidDomainSettings.vorticity:

Smoke
=====

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Fluid -- Settings --> Smoke`
   :Type:      Domain (Gas)

Buoyancy Density
   Buoyant force based on smoke density.

   - Values above 0 will cause the smoke to rise (simulating smoke which is lighter than ambient air).
   - Values below 0 will cause smoke to sink (simulating smoke which is heavier than ambient air).

Heat
   Controls how much smoke is affected by temperature.
   The effect this setting has on smoke depends on the per flow object *Initial Temperature*:

   - Values above 0 will result in the smoke rising when the flow object *Initial Temperature* is
     set to a positive value, and smoke sinking when the flow object *Initial Temperature* is
     set to a negative value.
   - Values below 0 will result in the opposite of positive values, i.e.
     smoke emitted from flow objects with a positive *Initial Temperature* will sink,
     and smoke from flow objects with a negative *Initial Temperature* will rise.

   Note that smoke from multiple flow objects with different temperatures
   will mix and warm up/cool down until an equilibrium is reached.

Vorticity
   Controls the amount of turbulence in the smoke. Higher values will make lots of small swirls,
   while lower values make smoother shapes.

   .. figure:: /images/physics_smoke_types_domain_vorticity.jpg
      :align: center

      Comparison of different amounts of vorticity. The domain on the left has a vorticity of 3,
      while the domain on the right has a vorticity of 0.01.


.. _bpy.types.FluidDomainSettings.use_dissolve_smoke:
.. _bpy.types.FluidDomainSettings.dissolve_speed:
.. _bpy.types.FluidDomainSettings.use_dissolve_smoke_log:

Dissolve
--------

Allow smoke to dissipate over time.

Time
   Speed of smoke's dissipation in frames.
Slow
   Dissolve smoke in a logarithmic fashion. Dissolves quickly at first, but lingers longer.


Fire
====

Todo.


Liquid
======

Todo.
