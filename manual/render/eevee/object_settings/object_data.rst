
******
Object
******

Ray Visibility
--------------

Objects can be set to be invisible to particular ray types.
This can be used, for example, to make an emitting mesh invisible to camera rays.
For instanced objects, visibility is inherited; if the parent object is hidden for some ray types,
the children will be hidden for these too.

In terms of performance, using these options is more efficient that using a shader node setup
that achieves the same effect.

.. _bpy.types.Object.visible_shadow:

Shadow
   Enables the object to cast shadows. The object will not be capture inside the shadow maps.


Light Probes
------------

Objects can be set to not be captured by certain :doc:`light probe </render/eevee/light_probes/introduction>`.
This can be used, for example, to avoid animated object being recorded into static light probes.
For instanced objects, visibility is inherited; if the parent object is hidden for some ray types,
the children will be hidden for these too.

.. _bpy.types.Object.hide_probe_volume:

Volume
   Makes the object visible during light probe volumes :ref:`baking <eevee-lightprobe-volume-bake>`.

.. _bpy.types.Object.hide_probe_sphere:

Sphere
   Makes the object visible during light probe sphere capture.

.. _bpy.types.Object.hide_probe_plane:

Plane
   Makes the object visible during light probe plane capture.
