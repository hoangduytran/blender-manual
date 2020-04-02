
************
Introduction
************

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Hotkey:    :kbd:`Tab`

As with any other object, you edit your armature in *Edit Mode* :kbd:`Tab`.

The set of bone editing tools is quite similar to the one for
:doc:`mesh </modeling/meshes/editing/introduction>` editing.

.. important::

   One important thing to understand about armature editing is that you
   edit the *rest position* of your armature, i.e. its "default state".
   An armature in its *rest position* has all bones with *no* rotation and scaled to 1.0 in their own local space.

The different :doc:`poses </animation/armatures/posing/index>`
you might create afterwards are based on this rest position.
So if you modify it in *Edit Mode*, all the poses already existing will also be modified.
Thus you should in general be sure that your armature is definitive before starting to
:doc:`skin </animation/armatures/skinning/index>` and :doc:`pose </animation/armatures/posing/index>` it!

.. note::

   Please note that some tools work on bones' joints, while others work on bones themselves.
   Be careful not to get confused.


Add Menu
========

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Add`
   :Hotkey:    :kbd:`Shift-A`

In the 3D View, :kbd:`Shift-A` to add a new bone to your armature.

This bone will be:

- Of one unit of length.
- Oriented towards the global Z axis.
- With its root placed at the 3D cursor position.
- With no relationship with any other bone of the armature.
