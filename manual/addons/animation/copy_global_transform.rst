
*********************
Copy Global Transform
*********************

Copy and paste object and bone transforms with ease.

When copying, the global (:term:`World Space`) transform is placed on the
clipboard. This can then be pasted onto any object or bone, at the current frame
or at another one.

Since the transform is placed on the clipboard as text, you can even copy-paste
it into an instant messenger and send it to someone else.


Activation
==========

- Open Blender and go to Preferences then the Add-ons tab.
- Click Animation then Copy Global Transform to enable the add-on.


Interface
=========

Located in :menuselection:`3D Viewport --> N-panel --> Animation tab`.

.. figure:: /images/addons_animation_copy-global-transform.png
   :align: right


Description
===========

Copy
   Inspects the active Object (in Object mode) or Bone (in Pose mode) and places
   its current global transform onto the clipboard as a matrix.

Paste
   Takes the copied global transform and applies it to the active Object or
   Bone. This is done by **adjusting its location, rotation, and scale properties**.

Mirrored
   Same as 'Paste' above, but then mirrored relative to some other object or
   bone. This can be useful, for example, to copy the foot position of one foot
   to the other. See :ref:`copy-global-transform-mirror-options` below.

Paste to Selected Keys
   Paste as described above and additionally use auto-keying to update one or
   more frames. The key selection is used to tell Blender *which frames* this
   should happen on; it does not influence which parts of the transform are
   keyed. *What* is keyed is determined by the active keying set.

Paste and Bake
   Almost the same as *Paste to Selected Keys*. Instead of only pasting on the
   selected keys, *Paste and Bake* will paste & auto-key on every frame between
   the first and last selected keys.

.. _copy-global-transform-mirror-options:

Mirror Options
==============

The copied transform can be mirrored relative to an object or a :term:`Bone`.
This requires choosing that object or bone first.

Armature + Bone
   Choosing an :term:`Armature` object as mirror object will show the bone
   selector. You can use that to pick the bone to use as mirror. This will
   always use the named bone on that specific armature object.
Bone Only
   When you choose *no mirror object* at all, you can still choose a *bone
   name*. This is used for mirroring against a bone in the *active armature*.
   This can be useful to mirror bone transforms relative to the the 'chest' bone
   of the active character.
Object Only
   This will just mirror relative to the chosen object.

After pasting with 'Paste Mirrored', the mirror axes can be chosen in the
:ref:`redo panel <bpy.ops.screen.redo_last>`.


Limitations
===========

Pasting a transform adjusts the Object/Bone's location, rotation, and
scale. This means that when copying a skewed transform, this skew is lost.

If there are constraints on the Object/Bone, the resulting visual transformation
may not be the same as the pasted one. To give a concrete example: if you have a
constraint that adds a rotation, it will always add that rotation on top of the
pasted transform.


.. seealso::

   :doc:`/animation/armatures/posing/editing/pose_library` for a way to manage
   and share entire poses.

.. reference::

   :Category: Animation
   :Description: Simple add-on for copying world-space transforms.
   :Location: :menuselection:`3D Viewport --> N-panel --> Animation tab`
   :File: copy_global_transform.py
   :Author: Sybren A. Stüvel
   :Maintainer: Sybren A. Stüvel
   :License: GPL 2+
   :Support Level: Official
   :Note: This add-on is bundled with Blender.
