
************
Introduction
************

Shape keys are used to deform objects into new shapes for animation.
In other terminology, shape keys may be called "morph targets" or "blend shapes".

The most popular use cases for shape keys are in character facial animation and
in tweaking and refining a skeletal rig.
They are particularly useful for modeling organic soft parts and muscles
where there is a need for more control over the resulting shape
than what can be achieved with combination of rotation and scale.

Shape keys can be applied on object types with vertices like mesh, curve, surface and lattice.

.. figure:: /images/animation_shape-keys_introduction_example.png

   Example of a mesh with different shape keys applied.


.. _animation-shapekeys-relative-vs-absolute:

Relative or Absolute Shape Keys
===============================

A mesh (curve, surface or lattice) has a stack of shape keys.
The stack may be of *Relative* or *Absolute* type.

Relative
   Mainly used for muscles, limb joints, and facial animation.

   Each shape is defined relative to the Basis or to another specified shape key.

   The resulting effect visible in the 3D Viewport, also called *Mix*,
   is the cumulative effect of each shape with its current value.
   Starting with the Basis shape, the result is obtained by **adding**
   each shape's weighted **relative** offset to its reference key.

   Value
      Represents the weight of the blend between a shape key and its reference key.

      A value of 0.0 denotes 100% influence of the reference key and 1.0 of the shape key.
      Blender can extrapolate the blend between the two shapes above 1.0 and below 0.0.

   Basis
      Basis is the name given to the first (top-most) key in the stack.

      The Basis shape represents the state of the object's vertices in their original position.
      It has no weight value and it is not keyable.
      This is the default *Reference Key* when creating other shapes.

Absolute
   Mainly used to deform the objects into different shapes over time.

   Each shape defines how the object's shape will be at *Evaluation Time* specified in its *Value*.

   The resulting shape, or *Mix*, is the interpolation of the previous and next shape
   given the current *Evaluation Time*.

   Value
      Represents the *Evaluation Time* at which that shape key will be active.

   Basis
      Basis is the name given to the first (topmost) key in the stack.

      The Basis shape represents the state of the object's vertices in their original position.
