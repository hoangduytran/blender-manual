*************
Light Linking
*************

.. _bpy.types.Object.light_linking:

With light linking, lights can be set to affect only specific objects in the scene.
Shadow linking additionally gives control over which objects acts as shadow blockers for a light.

This adds more artistic control for lighting by breaking the laws of physics.
For example the environment and characters in a shot might have different light setups.
A character could have a dedicated linked rim light to make it stand out,
and shadow linking could be used to ensure no objects from the environment block it.


Setup
=====

* Select the light or emissive mesh object and go to the
  :ref:`Cycles Shading panel <render-cycles-object-light-linking-settings>` or
  :ref:`EEVEE Shading panel <render-cycles-object-light-linking-settings>`.
* Create a new light or shadowing linking collection.
* Drag & drop objects or collection from the outliner.

.. note::
  Light linking emissive mesh object is only available for Cycles.

Links can also be set up in the 3D viewport, with the Link Data operator.
The active light object is linked to selected receiver or blocker object.

A light or shadow linking collection can be assigned to and shared between multiple light objects.
While a scene collection can be directly assigned as a light or shadow linking collection,
it is recommended to instead create a dedicated collection and link any scene collection inside it instead.
This way it's easy to include or exclude additional objects without affecting the scene layout.


Include & Exclude
=================

Light receiver objects can be set to be either included or excluded.
The behavior is as follows:

* If only included objects are specified, the light only affects those objects.
* If only excluded objects are specified, the light affects all objects in the scene except those specified.
* If both included and excluded objects are specified, the light affects only included objects minus the excluded
  objects. This can be used to for example set a character collection to be included, and then exclude specific
  objects part of the character.


Performance
===========

Sampling for light linking is most efficient with the light tree enabled,
where a specialized acceleration structure is built for light linking.

When using shadow linking, renders can be slower and trace additional rays,
as direct and indirect lighting take different paths.
