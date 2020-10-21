.. index:: Modeling Modifiers; Boolean Modifier
.. _bpy.types.BooleanModifier:

****************
Boolean Modifier
****************

The *Boolean* modifier performs operations on meshes that are otherwise too complex
to achieve with as few steps by editing meshes manually. It uses one of
the three available Boolean operations to create a single mesh out of two mesh objects:

.. figure:: /images/modeling_modifiers_generate_booleans_union-intersect-difference-examples.png

   The Union, Intersection and Difference between a Cube and a UV Sphere,
   with the modifier applied to the sphere and using the cube as target.

This modifier needs a second object to be the target (the second operand) of the operation.

.. warning::

   Only :term:`Manifold` meshes are guaranteed to give proper results,
   other cases (especially "opened" meshes, :term:`Non-manifold` but without any self-intersections)
   will usually work well, but might give odd glitches and artifacts in some cases.

.. tip::

   If you have marked your objects to show the edges
   (in :menuselection:`Properties --> Object Properties --> Viewport Display`, enable *Wireframe*),
   you will see the edge creation process while you are moving your objects around. Depending on your mesh topology,
   you can also enable X-Ray and Transparency and see the topology being created in real-time.


Options
=======

.. figure:: /images/modeling_modifiers_generate_booleans_panel.png
   :align: right
   :width: 300px

   The Boolean modifier.

Intersect
   Opposite of *Difference* (everything *inside* of the target mesh is kept).
Union
   The target mesh is added to the modified mesh.
Difference
   The target mesh is subtracted from the modified mesh (everything *outside* of the target mesh is kept).

Object
   The name of the target mesh object.

Solver
   Algorithm used to calculate the boolean intersections.

   Fast
      Uses a mathematically simple solver which offers the best performance;
      however, this solver lacks support for overlapping geometry.

      Overlap Threshold
         Maximum distance between two faces to consider them as overlapping.
         This helps solve the limitation of this solver,
         if the boolean result seems unexpected try using the exact solver.

   Exact
      Uses a mathematically complex solver which offers the best results
      and has full support for overlapping geometry;
      however, this solver is much slower than the *Fast Solver*.

      Self
         Correctly calculates cases when one or both operands have self-intersections,
         this involves more calculations making it slower.
