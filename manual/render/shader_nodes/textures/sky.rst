.. _bpy.types.ShaderNodeTexSky:

****************
Sky Texture Node
****************

.. figure:: /images/node-types_ShaderNodeTexSky.webp
   :align: right
   :alt: Sky Texture Node.

The *Sky Texture* node generates a procedural sky. It's typically used in combination
with the :doc:`/render/shader_nodes/output/world`.


Inputs
======

Vector
   Texture coordinate to sample texture at;
   defaults to Generated texture coordinates if the socket is left unconnected.


Properties
==========

Sky Type
   Sky model to use.

   Multiple Scattering
      Improved version of the 1993
      `model <https://www.scratchapixel.com/lessons/procedural-generation-virtual-worlds/simulating-sky/simulating-
      colors-of-the-sky.html>`__
      by Nishita et al.

      Note that this sky type is quite bright and makes the image look overexposed with the default scene settings.
      You can reduce the Exposure setting in :menuselection:`Properties --> Render --> Film` to fix this.
   Single Scattering
     Same algorithm as Multiple Scattering, with just a single light bounce.
     This is legacy and may be removed in a future version.
   Preetham
      Based on the 1999 `paper <https://doi.org/10.1145/311535.311545>`__ by Preetham et al.
      This is legacy and will be removed in a future version.
   Hosek/Wilkie
      Based on the 2012 `paper <https://cgg.mff.cuni.cz/projects/SkylightModelling/>`__ by Hosek and Wilkie.
      This is legacy and will be removed in a future version.

Sun Direction
   Sun direction vector.

Turbidity
   Atmospheric turbidity.

   - 2: Arctic like
   - 3: clear sky
   - 6: warm/moist day
   - 10: hazy day

Ground Albedo
   Amount of light reflected from the planet surface back into the atmosphere.

Sun Disc :guilabel:`Cycles Only`
   Enable/Disable sun disc lighting.

Sun Size
   Angular diameter of the sun disc (in degrees).

Sun Intensity
   Multiplier for sun disc lighting.

Sun Elevation
   Rotation of the sun from the horizon (in degrees).

Sun Rotation
   Rotation of the sun around the zenith (in degrees).

Altitude
   The distance from sea level to the location of the camera.
   For example, if the camera is placed on a beach then a value of 0 should be used.
   However, if the camera is in the cockpit of a flying airplane then a value of 10 km will be more suitable.
   Note, this is limited to 60 km because the mathematical model only accounts
   for the first two layers of the earth's atmosphere (which ends around 60 km).

Air
   Density of air molecules.
   A value of 1 corresponds roughly to urban city air, while 0 is no air.
   
Aerosols
   Density of dust, pollution and water droplets.
   A value of 1 corresponds roughly to urban city aerosols, while 0 is no aerosols.

Ozone
   Density of ozone molecules; useful to make the sky appear bluer.
   A value of 1 corresponds roughly to urban city ozone, while 0 is no ozone.


Outputs
=======

Color
   Texture color output.


Examples
========

.. figure:: /images/render_shader-nodes_textures_sky_example.jpg
   :width: 200px

   Example of Sky Texture.
