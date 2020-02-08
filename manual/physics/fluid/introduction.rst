
************
Introduction
************

Liquid Simulations
==================

Fluid physics are used to simulate physical properties of liquids especially water.
While creating a scene in Blender, certain objects can be marked to participate in the fluid simulation.
These can include but not limited to, being a fluid or as an obstacle.
For a fluid simulation you have to have a domain to define the space that the simulation takes up.
In the domain settings you will be able to define the global simulation parameters (such as viscosity and gravity).

.. figure:: /images/physics_fluid_introduction_example.jpg

   Example of a fluid simulation.


Gas Simulations
===============

Gas or smoke simulations are a subset of the fluids system, and can be used for simulating collections
of airborne solids, liquid particulates and gases, such as those that make up smoke.
It simulates the fluid movement of air and generates animated :term:`voxel`
textures representing the density, heat, and velocity of other fluids or suspended particles
(e.g. smoke) which can be used for rendering.

.. figure:: /images/physics_smoke_types_domain_note-on-resolution.jpg

   Example of smoke simulation.

Gases/Smoke are emitted inside of a :doc:`Domain </physics/fluid/type/domain/index>`
from a mesh object or particle system.
Smoke movement is controlled by airflow inside the domain,
which can be influenced by :doc:`Effector objects </physics/fluid/type/effector>`.
Smoke will also be affected by the scene's gravity and :doc:`force fields </physics/forces/force_fields/index>`.
Airflow inside the domain can affect other physics simulations via the *Smoke Flow* force field.


Workflow
========

At least a :doc:`Domain object </physics/fluid/type/domain/index>` and
one :doc:`Flow object </physics/fluid/type/flow>`
are required to create a fluid simulation.

#. Create a :doc:`Domain object </physics/fluid/type/domain/index>`
   that defines the bounds of the simulation volume.
#. Set up :doc:`Flow objects </physics/fluid/type/flow>` which will emit fluid.
#. Set up :doc:`Effector objects </physics/fluid/type/effector>`
   to make the fluid interact with objects in the scene.
#. Assign a :doc:`material </physics/fluid/material>` to the domain object.
#. Save the blend-file.
#. :doc:`Bake the Cache </physics/fluid/type/domain/cache>` for the simulation.

.. note::

   There is a *Quick Fluid* and *Quick Smoke* :ref`:operator <bpy.ops.object.quick>`
   which will automatically create a domain object with a basic liquid/smoke/fire material.
