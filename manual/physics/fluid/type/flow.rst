.. _bpy.types.FluidFlowSettings:

****
Flow
****

Todo.


Settings
========

Todo.


.. _bpy.types.FluidFlowSettings.flow_source:
.. _bpy.types.FluidFlowSettings.use_plane_init:
.. _bpy.types.FluidFlowSettings.surface_distance:
.. _bpy.types.FluidFlowSettings.volume_density:
.. _bpy.types.FluidFlowSettings.particle_system:
.. _bpy.types.FluidFlowSettings.use_particle_size:
.. _bpy.types.FluidFlowSettings.particle_size:

Flow Source
-----------

Flow Source
   This setting defines the method used to emit fluid.

   Mesh
      Create smoke/fire directly from the object's mesh.

      Is Planar
         Todo.

      Surface Emission
         Maximum distance in voxels from the surface of the mesh in which fluid is created (see :term:`voxel`).
         Since this setting uses voxels to determine distance,
         results will vary depending on the domain's resolution.

      Volume Emission
         Amount of fluid to emit inside the emitter mesh, where 0 is none and 1 is
         Note that emitting fluid based on volume may have unpredictable results
         if your mesh is :term:`non-manifold`.

   Particle System :guilabel:`Fire or Smoke Only`:
      Create smoke/fire from a particle system on the flow object.
      Note that only *Emitter* type particle systems can add smoke.
      See :doc:`Particles </physics/particles/introduction>` for information on how to create a particle system.

      With this option selected, there is a box to select a particle system and one additional setting, *Set Size*.

         Set Size
            When this setting is enabled, it allows the *Size* setting to define
            the maximum distance in voxels at which particles can emit smoke,
            similar to the *Surface Emission* setting for mesh sources.

            When disabled, particles will fill the nearest :term:`voxel` with smoke.


.. _bpy.types.FluidFlowSettings.use_initial_velocity:
.. _bpy.types.FluidFlowSettings.velocity:

Initial Velocity
----------------

When enabled, fluid will inherit the momentum of the flow source.

Source
   Multiplier for inherited velocity. A value of 1 will emit fluid moving at the same speed as the source.
Normal
   When using a *Geometry Flow Source*,
   this option controls how much velocity fluid is given along the source's :term:`normal`.
Initial X, Y, Z
   Todo.


.. _bpy.types.FluidFlowSettings.use_texture:
.. _bpy.types.FluidFlowSettings.noise_texture:
.. _bpy.types.FluidFlowSettings.texture:

Texture
-------

.. admonition:: Reference
   :class: refbox

   :Type:      Flow
   :Panel:     :menuselection:`Physics --> Fluid --> Settings --> Texture`

When enabled, use the specified texture and settings to control where on
the mesh smoke or fire can be emitted from. These settings have no effect on *Outflow Flow Behavior*.

Texture
   Todo.
Mapping
   Todo.
Size
   Todo.
Offset
   Todo.

.. figure:: /images/physics_smoke_types_flow-object_texture-usecase.jpg
   :align: center

   Example of using a texture to control smoke flow.
