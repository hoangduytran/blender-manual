.. _bpy.types.ShaderNodeTexSky:

****************
Sky Texture Node
****************

:guilabel:`Cycles Only`

.. figure:: /images/render_shader-nodes_textures_sky_node.png
   :align: right

   Sky Texture Node.

The *Sky Texture* node adds a procedural Sky texture.


Inputs
======

Vector
   Texture coordinate to sample texture at;
   defaults to Generated texture coordinates if the socket is left unconnected.


Properties
==========

Sky Type
   Sky model to use.

   Preetham
      Based on the 1999 `paper <https://www2.cs.duke.edu/courses/cps124/spring08/assign/07_papers/p91-preetham.pdf>`__ by Preetham
   Hosek/Wilkie
      Based on the 2012 `paper <https://cgg.mff.cuni.cz/projects/SkylightModelling/>`__ by Hosek and Wilkie
   Nishita
      Improved version of the 1993 `model <https://www.scratchapixel.com/lessons/procedural-generation-virtual-worlds/simulating-sky/simulating-colors-of-the-sky>`__ by Nishita

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

Sun Disc
   Enable/Disable sun disc lighting.

Sun Size
   Diameter of the sun disc in degrees.

Sun Elevation
   Rotation of the sun from the horizon line.

Sun Rotation
   Rotation of the sun around the Z axis.

Altitude
   Height from sea level to the space in meters.

Air
   Density of air molecules.

   - 0 no air
   - 1 clear day atmosphere
   - 2 highly polluted day

Dust
   Density of dust and water droplets.

   - 0 no dust
   - 1 clear day atmosphere
   - 5 city like atmosphere
   - 10 hazy day

Ozone
   Density of ozone molecules;
   useful to make the sky appear bluer.

   - 0 no ozone
   - 1 clear day atmosphere
   - 2 city like atmosphere


Outputs
=======

Color
   Texture color output.


Examples
========

.. figure:: /images/render_shader-nodes_textures_sky_example.jpg
   :width: 200px

   Example of Sky Texture.
