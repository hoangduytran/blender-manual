.. _bpy.types.ShaderNodeBsdfRayPortal:

***************
Ray Portal BSDF
***************

:guilabel:`Cycles Only`

The *Ray Portal BSDF* node transports rays that enter to another location
in the scene. It can be used to render portals for visual effects, and
other production rendering tricks.

It acts much like a :doc:`Transparent BSDF </render/shader_nodes/shader/transparent>`:
render passes are passed through,
and it is affected by light path max transparent bounces.

.. note::

   - The *Ray Portal BSDF* only allows rays to pass through it in one direction. Add a
     second portal at the target location to make rays go in the other direction as well.

   - Light sampling does not work efficiently through portals. This can lead to increased
     noise from lights on the other side of portals. Particularly small lights may be very
     noisy, or not pass through at all.


Inputs
======

Color
   Tint rays passing through the portal.
Position
   Ray start position at new location. Defaults to the current position,
   matching the Position output of the
   :doc:`Geometry node </render/shader_nodes/input/geometry>`.
Direction
   Ray direction at the new location. Defaults to the current view direction,
   which is the same as the negation of the Incoming output of the
   :doc:`Geometry node </render/shader_nodes/input/geometry>`.


Properties
==========

This node has no properties.


Outputs
=======

BSDF
   Standard shader output.
