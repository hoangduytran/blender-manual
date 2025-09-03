
********
Workflow
********

Shape keys are authored in the :doc:`Shape Keys panel </animation/shape_keys/shape_keys_panel>`
which is accessed in the Object Data tab of the Properties (e.g. the Mesh tab for mesh objects).

A shape key is modified by first selecting a shape key in the panel,
and then moving the object's vertices to a new position in the 3D Viewport.

The panel has controls for affecting the current *Value* (influence, weight) of a shape.
It is possible to see a shape in isolation or how it combines with others.


Adding and Removing Vertices
============================

It is not possible to add or remove vertices in a shape key.
The number of vertices and how they connect is specified by the mesh, curve, surface or lattice.
A shape key merely records a position for each vertex and therefore shapes always
contain all the object's vertices.

When adding a vertex, all shape keys will record it with the position in which it is created.
Workflow-wise, adding and deleting vertices after creating shape keys is possible, but it is best
to leave the creation of shape keys for when the mesh is finished or its topology is stable.


Adding Shape Keys
=================

When adding a new shape key with the :bl-icon:`add` button next to the list,
the new shape will be a copy of the Basis shape,
independently of the current result visible in the 3D Viewport.

When adding a new shape key from :menuselection:`Specials --> New Shape from Mix`,
the shape will start of with the vertex configuration that is visible at that moment.

When doing facial animation with relative shape keys, it can be useful to first
create a shape key with a complex extreme pose (e.g. anger or surprise), and
then break this complex shape into components by applying a temporary vertex group to
the complex shape and creating a copy with *New Shape from Mix*.
This technique helps reducing conflicts between different shape keys
that would otherwise produce a double effect.


Relative Shape Keys
-------------------

#. In *Object Mode*, add a new shape key via the *Shape Key* panel with the :bl-icon:`add` button.
#. "Basis" is the rest shape. "Key 1", "Key 2", etc. will be the new shapes.
#. Switch to *Edit Mode*, select "Key 1" in the *Shape Key* panel.
#. Deform mesh as you want (do not remove or add vertices).
#. Select "Key 2", the mesh will be changed to the rest shape.
#. Transform "Key 2" and keep going for other shape keys.
#. Switch back to *Object Mode*.
#. Set the *Value* for "Key 1", "Key 2", etc. to see the transformation between the shape keys.

In the figure below, from left to right shows: "Basis", "Key 1", "Key 2"
and mix ("Key 1" ``1.0`` and "Key 2" ``0.8``) shape keys in Object Mode.

.. figure:: /images/animation_shape-keys_workflow_relative.png

   Relative shape keys example.

For more practical examples, see
:ref:`how to combine shape keys and drivers <shapekey-driver-example>`.


Absolute Shape Keys
-------------------

#. Add sequence of shape keys as described above for relative shape keys.
#. Uncheck the *Relative* checkbox.
#. Click the *Reset Timing* button.
#. Switch to *Object Mode*.
#. Drag *Evaluation Time* to see how the shapes succeed one to the next.

.. figure:: /images/animation_shape-keys_workflow_absolute.png

   Absolute shape keys workflow.

By adding a :doc:`driver </animation/drivers/index>` or
setting :doc:`keyframes </animation/keyframes/introduction>`
to *Evaluation Time* you can create an animation.

.. seealso:: Shape Key Operators

   There are two modeling tools used to control shape keys and
   are found in :ref:`Edit Mode <modeling-meshes-editing-vertices-shape-keys>`.
