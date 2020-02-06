
************
Smoke Domain
************

.. _smoke-resolution:

.. seealso:: Also see `Note on Divisions and High Resolution`_.


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
