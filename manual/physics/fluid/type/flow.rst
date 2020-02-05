
****
Flow
****

Todo.


Settings
========

Todo.


Flow Source
-----------

Todo.


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
