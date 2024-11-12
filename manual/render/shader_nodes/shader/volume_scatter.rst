.. _bpy.types.ShaderNodeVolumeScatter:

**************
Volume Scatter
**************

.. figure:: /images/node-types_ShaderNodeVolumeScatter.png
   :align: right
   :alt: Volume Scatter node.

The *Volume Scatter* node allows light to be scattered as it passes through the volume.
Typical usage would be to add fog to a scene. It can also be used with
the :doc:`Volume Absorption </render/shader_nodes/shader/volume_absorption>`
node to create smoke.


Inputs
======

Common
------

Color
   Scattering coefficients per color channel.
Density
   The density of the scatter effect.

Henyey-Greenstein
-----------------
Anisotropy
   Controls the relative amount of backward and forward scattering.

Fournier-Forand :guilabel:`Cycles Only`
---------------------------------------
IOR
   Refractive index of the scattering particles relative to water.
Backscatter
   Fraction of light that is scattered backwards. Most oceanic particles have backscatter fractions between 0.001 (e.g., very large phytoplankton) and 0.1 (e.g., very small mineral particles).

Draine :guilabel:`Cycles Only`
------------------------------
Anisotropy
   Controls the relative amount of backward and forward scattering.
Alpha
   Blending factor between Henyey-Greenstein (:math:`\alpha = 0`) and Cornette & Shanks (:math:`\alpha = 1`) phase functions.

Mie :guilabel:`Cycles Only`
---------------------------
Diameter
   Diameter of the scattering particles in µm.

Properties
==========
Phase
  Volume scattering phase function.

  :Henyey-Greenstein: Simple and widely used phase function, useful for
                      approximating scattering in biological tissues.
  :Fournier-Forand:  :guilabel:`Cycles Only`
     Suitable for modeling the scattering behavior of seawater.
  :Draine:  :guilabel:`Cycles Only`
     Suitable for modeling the scattering of interstellar dust.
  :Rayleigh:  :guilabel:`Cycles Only`
     Describes the scattering by particles with a size smaller than the wavelength of light, such as the scattering of sunlight in earth's atmosphere.
  :Mie: :guilabel:`Cycles Only`
     Describes the scattering by particles with a size larger than the wavelength of light, such as cloud and fog.

Outputs
==========

Volume
   The Volume Shader output must be plugged into the *Volume Input*
   of the :doc:`Material </render/shader_nodes/output/material>`
   or :doc:`World </render/shader_nodes/output/world>` Output node.


Examples
========

.. figure:: /images/render_shader-nodes_shader_volume-scatter_example.png

   Example of Volume Scatter.
