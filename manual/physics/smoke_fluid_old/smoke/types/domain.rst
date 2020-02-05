.. _bpy.types.SmokeDomainSettings:

************
Smoke Domain
************

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Smoke`
   :Type:      Domain

The domain object contains the entire simulation. Smoke and fire cannot leave the domain,
it will either collide with the edge or disappear, depending on the domain's settings.

Keep in mind that large domains require higher resolutions and longer bake times.
You will want to make it just large enough that the simulation will fit inside it,
but not so large that it takes too long to compute the simulation.

To create a domain, add a cube :menuselection:`Add --> Mesh --> Cube`, :kbd:`Shift-A`
and transform it until it encloses the area where you want smoke. Translation, rotation,
and scaling are all allowed. To turn it into a smoke domain, click *Smoke*
in :menuselection:`Properties --> Physics`, then select *Domain* as the *Smoke Type*.

.. note::

   You *can* use other shapes of mesh objects as domain objects,
   but the smoke simulator will use the shape's :term:`bounding box`
   as the domain bounds. In other words, the actual shape of the domain will still be rectangular.

.. TODO2.8:
   .. figure:: /images/physics_smoke_types_domain_settings.png
      :align: right

      *Smoke Domain* options.


Settings
========

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Smoke --> Settings`
   :Type:      Domain

.. _smoke-resolution:

Resolution
   The smoke domain is subdivided into many "cells" called voxels (see :term:`voxel`)
   which make up "pixels" of smoke. This setting controls the number of subdivisions in the domain.
   Higher numbers of subdivisions are one way of creating higher resolution smoke (see `High Resolution`_).

   Since the resolution is defined in terms of *subdivisions*,
   larger domains will need more divisions to get an equivalent resolution to a small domain.

   Also see `Note on Divisions and High Resolution`_.

Time Scale
   Controls the speed of the simulation. Low values result in a "slow motion" simulation,
   while higher values can be used to advance the simulation faster
   (useful for generating smoke for use in still renders).

Border Collisions
   Controls which sides of the domain will allow smoke "through" the domain,
   making it disappear without influencing the rest of the simulation,
   and which sides will deflect smoke as if colliding with
   a :doc:`Collision Object </physics/smoke/types/collision>`.

   Vertically Open
      Smoke disappears when it hits the top or bottom of the domain, but collides with the walls.
   Open
      Smoke disappears when it hits any side of the domain.
   Collide All
      Smoke collides with all sides of the domain.

Empty space
   Value under which voxels are considered to be empty.


.. _smoke-high-resolution:

High Resolution
===============

.. admonition:: Reference
   :class: refbox

   :Type:      Domain
   :Panel:     :menuselection:`Physics --> Smoke --> High Resolution`

The High Resolution option lets you simulate at a low resolution and then it uses noise techniques
to enhance the resolution without actually computing it. This allows animators to set up a low
resolution simulation quickly and later add details without changing the overall fluid motion.
Also see `Note on Divisions and High Resolution`_.

Resolution Divisions
   Factor by which to enhance the resolution of smoke using the specified noise method.
Flow Sampling
   Method for sampling the high resolution flow.
Noise Method
   The two options, *Wavelet* and *FFT*, are very similar.

   .. figure:: /images/physics_smoke_types_domain_high-resolution-method.jpg
      :width: 400px

      Comparison of noise methods. *Wavelet* on the left, *FFT* on the right.

   .. note::

      *Wavelet* is an implementation of `Turbulence for Fluid Simulation
      <https://web.archive.org/web/20140911163550/https://graphics.ethz.ch/research/physics_animation_fabrication/simulation/turb.php>`__.

Strength
   Strength of noise.

   .. figure:: /images/physics_smoke_types_domain_high-resolution-strength.jpg
      :width: 400px

      From left to right, the domains' high resolution strengths are set to 0, 2, and 6.

.. tip::

   The visibility of high resolution smoke in the viewport can be toggled in the render
   :ref:`Simplify options <render-cycles-simplify-viewport>`.


Note on Divisions and High Resolution
-------------------------------------

:ref:`High Resolution Divisions <smoke-high-resolution>`
and :ref:`Domain Subdivisions <smoke-resolution>` are not equivalent.
By using different combinations of these resolution settings, you can obtain a variety of different styles of smoke.

.. figure:: /images/physics_smoke_types_domain_high-resolution-comparison.jpg
   :align: center

   Comparison between a domain with 24 divisions and 4 *High Resolution* divisions (left),
   and a domain with 100 divisions and 1 *High Resolution* division (right).

Low division simulations with lots of *High Resolution*
divisions generally appear smaller in real-world scale
(larger flames, etc.) and can be used to achieve pyroclastic plumes such as this:

.. figure:: /images/physics_smoke_types_domain_note-on-resolution.jpg
   :align: center

High *Domain Division* simulations tend to appear larger in real-world scale, with many smaller details.
