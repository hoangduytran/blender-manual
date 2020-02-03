
*******************
Physical Properties
*******************

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Cloth --> Physical Properties`

Mass
   The mass of the cloth material.
Air Viscosity
   Air has some thickness which slows falling things down.
Bending Model
   Linear
      Cloth model with linear bending springs (old).
   Angular
      Cloth model with angular bending springs.


Stiffness
=========

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Cloth --> Physical Properties --> Stiffness`

Tension
   How much the material resists stretching.
Compression
   How much the material resists compression.
Structural
   Overall stiffness of the cloth (only in linear bending model).
Shear
   How much the material resists shearing.
Bending
   Wrinkle coefficient. Higher creates more large folds.


Damping
=======

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Cloth --> Physical Properties --> Damping`

Tension
   Amount of damping in stretching behavior.
Compression
   Amount of damping in compression behavior.
Structural
   Amount of damping in stretching behavior (only in linear bending model).
Shear
   Amount of damping in shearing behavior.
Bending
   Amount of damping in bending behavior.


.. _bpy.types.ClothSettings.use_pressure:
.. _bpy.types.ClothSettings.use_pressure_volume:
.. _bpy.types.ClothSettings.target_volume:
.. _bpy.types.ClothSettings.pressure_factor:
.. _bpy.types.ClothSettings.vertex_group_pressure:

Pressure
========

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Cloth --> Physical Properties --> Damping`

Cloth pressure allows the simulation of soft shelled objects
such as balloons or balls that are filled with some sort of fluid.
This fluid can be seen either as a gas or a liquid however, both are generalized as "fluids".
Cloth pressure can be enabled by toggling the checkbox in the *Pressure* panel header.

.. note::

   Non manifold meshes will work with cloth pressure however,
   pressure will escape out of the mesh holes and cause drifting or propulsion forces.
   One way to get around this is by using the *Vertex Group* to exclude the non manifold portions of the mesh.

Pressure
   The uniform pressure that is constantly applied to the mesh.
   This value can be negative to simulate implosions
   or any other case where an object has outside pressure pushing inwards.

Custom Volume
   Use the *Target Volume* parameter as the initial volume for the cloth.
   This avoids having to use the *Pressure* to first inflate the object.

   Target Volume
      The mesh volume where the inner/outer pressure will be the same.
      If set to zero the volume will not contribute to the total pressure.

Factor
   Scalar control over the overall pressure.
Vertex Group
   Cloth pressure can be controlled via a :doc:`Vertex Group </modeling/meshes/properties/vertex_groups/index>`
   to specify which the portions of the mesh to apply pressure.
   Zero weight means no pressure while a weight of one means full pressure.

   Note, Faces with a vertex that has zero weight will be excluded from the *Target Volume* calculation.
