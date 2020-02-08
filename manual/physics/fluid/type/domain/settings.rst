.. _bpy.types.FluidDomainSettings.domain_type:
.. _bpy.types.FluidDomainSettings.resolution_max:
.. _bpy.types.FluidDomainSettings.time_scale:
.. _bpy.types.FluidDomainSettings.cfl_condition:
.. _bpy.types.FluidDomainSettings.use_adaptive_timesteps:
.. _bpy.types.FluidDomainSettings.timesteps_max:
.. _bpy.types.FluidDomainSettings.timesteps_min:
.. _bpy.types.FluidDomainSettings.gravity:

********
Settings
********

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Fluid --> Settings`
   :Type:      Domain

The domain object contains the entire simulation. Fluid simulations cannot leave the domain,
it will either collide with the edge or disappear, depending on the domain's settings.

Keep in mind that large domains require higher resolutions and longer bake times.
You will want to make it just large enough that the simulation will fit inside it,
but not so large that it takes too long to compute the simulation.

To create a domain, add a cube and transform it until it encloses the area where you want fluid.
Translation, rotation, and scaling are all allowed. To turn it into a fluid domain, click *Fluid*
in :menuselection:`Properties --> Physics`, then select *Domain* as the fluid *Type*.

.. note::

   You *can* use other shapes of mesh objects as domain objects,
   but the fluid simulator will use the shape's :term:`bounding box` as the domain bounds.
   In other words, the actual shape of the domain will still be rectangular.

Resolution Divisions
   The fluid domain is subdivided into many "cells" called voxels (see :term:`voxel`)
   which make up "pixels" of fluid. This setting controls the number of subdivisions in the domain.
   Higher numbers of subdivisions are one way of creating higher resolution fluids.

   Since the resolution is defined in terms of "subdivisions",
   larger domains will need more divisions to get an equivalent resolution to a small domain.
   To help with this, the *Resolution Divisions* can be previewed with a small cube
   shown in the 3D Viewport, to show the size of these divisions.

Time Scale
   Controls the speed of the simulation. Low values result in a "slow motion" simulation,
   while higher values can be used to advance the simulation faster
   (useful for generating fluids for use in still renders).


.. _bpy.types.FluidDomainSettings.use_collision_border:

Border Collisions
=================

Controls which sides of the domain will allow fluid "through" the domain,
making it disappear without influencing the rest of the simulation,
and which sides will deflect fluids.


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

.. _smoke-domain-heat:

Heat
   Controls how much smoke is affected by temperature.
   The effect this setting has on smoke depends on the per flow object
   :ref:`Initial Temperature <physics-fluid-flow-init-temp>`:

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


.. _bpy.types.FluidDomainSettings.burning_rate:
.. _bpy.types.FluidDomainSettings.flame_smoke:
.. _bpy.types.FluidDomainSettings.flame_vorticity:
.. _bpy.types.FluidDomainSettings.flame_max_temp:
.. _bpy.types.FluidDomainSettings.flame_ignition:
.. _bpy.types.FluidDomainSettings.flame_smoke_color:

Fire
====

.. admonition:: Reference
   :class: refbox

   :Type:      Domain
   :Panel:     :menuselection:`Physics --> Smoke --> Flames`

Reaction Speed
   How fast fuel burns. Larger values result in smaller flames (fuel burns before it can go very far),
   smaller values result in larger flames (fuel has time to flow farther before being fully consumed).
Flame Smoke
   Amount of extra smoke created automatically to simulate burnt fuel.
Vorticity
   Additional vorticity for flames.
Temperature Maximum
   Maximum temperature of flames.
Minimum
   Minimum temperature of flames.
Flame Color
   Color of flame created by burnt fuel.


Liquid
======

Todo.
