.. index:: Compositor Nodes; Film Grain

***************
Film Grain Node
***************

.. figure:: /images/node-types_CompositorNodeFilmGrain.webp
   :align: right
   :alt: Film Grain Node.

The *Film Grain* node adds random noise resembling photographic or cinematic film grain,
simulating the texture and imperfections of analog film.
It is often used to integrate CGI with filmed footage, reduce the overly clean look of digital renders,
or achieve a stylized, cinematic appearance.

Compared to the :doc:`Sensor Noise </compositing/types/camera_lens_effects/sensor_noise>` node,
which mimics the color and luminance noise patterns of digital sensors,
the *Film Grain* node focuses on recreating the organic texture and tonal qualities
of physical film stock.


Inputs
======

Image
   Standard color input image.

Type
   Determines how the film grain is applied.

   :Color:
      Adds colored noise to each RGB channel independently, resulting in a more vibrant grain effect.
   :Monochrome:
      Applies the grain uniformly to the luminance channel only, producing a classic black-and-white grain look.

Factor
   Controls the intensity of the grain effect.
   Lower values apply subtle texture, while higher values create a coarse and more noticeable grain.

Grain Size
   Defines the size of the grain particles.
   Smaller values simulate fine film stock, while larger values create rougher, more pronounced grain.

Animated
   When enabled, the grain pattern changes every frame, simulating real film grain movement.
   When disabled, the same pattern is reused, resulting in static grain.


Outputs
=======

Image
   The input image with the film grain applied.
