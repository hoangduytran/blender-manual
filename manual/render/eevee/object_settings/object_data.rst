
*****************
Object Properties
*****************

Shading
=======

.. reference::

   :Panel:     :menuselection:`Properties --> Object Properties --> Shading`

Light Linking
-------------

.. _render-eevee-object-light-linking-settings:

Limit light influence to specified objects, with :ref:`Light Linking <bpy.types.Object.light_linking>`.

Receiver Collection
   Collection of objects that will receive light emitted from the object.


Shadow Linking
--------------

Limit shadows to specified objects, with :ref:`Light Linking <bpy.types.Object.light_linking>`.

Shadow Blocker Collection
   Collection of objects that will act as shadow blockers for light emitted from the object.


Visibility
==========

.. reference::

   :Panel:     :menuselection:`Object Properties --> Visibility`

Ray Visibility
--------------

Objects can be set to be invisible to particular ray types.
This can be used, for example, to make an emitting mesh invisible to camera rays.
For instanced objects, visibility is inherited; if the parent object is hidden for some ray types,
the children will be hidden for these too.

In terms of performance, using these options is more efficient that using a shader node setup
that achieves the same effect.

.. _bpy.types.Object.visible_camera:

Camera
   Makes the object visible to the :doc:`Camera </render/cameras>`;
   this includes the viewport's perspective in viewport rendering.

.. _bpy.types.Object.visible_shadow:

Shadow
   Enables the object to cast shadows. The object will not be capture inside the shadow maps.


Light Probes
------------

Objects can be set to not be captured by certain :doc:`light probe </render/eevee/light_probes/index>`.
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
