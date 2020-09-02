
********
Dynamics
********

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Rigid Body --> Dynamics`

.. TODO2.8:
   .. figure:: /images/physics_rigid-body_properties_dynamics.png

      Rigid Body Dynamics panel.

Used to control the physics of the rigid body simulation.
This panel is available only for *Active* type of rigid bodies.

Damping Translation
   Amount of linear velocity that is lost over time.

Rotation
   Amount of angular velocity that is lost over time.


Deactivation
============

Enable deactivation of resting rigid bodies. Allows object to be deactivated during the simulation
(improves the performance and stability, but can cause glitches).

Start Deactivated
   Starts objects deactivated. They are activated on collision with other objects.

Linear Velocity
   Specifies the linear deactivation velocity below which the rigid body
   is deactivated and the simulation stops simulating the object.

Angular Velocity
   Specifies the angular deactivation velocity below which the rigid body
   is deactivated and the simulation stops simulating the object.
