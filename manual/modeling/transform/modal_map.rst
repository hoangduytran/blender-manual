
*******************
Transform Modal Map
*******************

During a transformation, some hotkeys can change the behavior of the operation.

You can check editing the keys of these modal modifiers in
:menuselection:`Blender Preferences --> Keymap --> Transform Modal Map`
(at the bottom of the keymap).


Constraints
===========

When moving, rotating or scaling, if you only want certain axes to be affected,
you can restrict the transformation to those axes.

By default the constraint keys are :kbd:`X`, `Y` and `Z`.
This constraint can be restricted to plane if :kbd`Shift`
is pressed or automatically detected if :kbd:`MMB` is pressed.

It is worth noting that if you press the same contraint hotkey a second time,
you change the orientation from Local to Global or vice versa. Pressing a third time disables the constraint.


Snapping
========

Transform operations use the :doc:`snapping settings </editors/3dview/controls/snapping>` set in the scene.
However, some options can be changed during the transformation.


Snap Invert
-----------

Even if the magnetic icon is disabled, you can still enable snapping during a transformation.
The default hotkey in this case is :kbd:`Ctrl`.


Set Snap Base
-------------

Snap Base is taken automatically depending on the :ref:`Snap With <bpy.types.ToolSettings.snap_target>` options.
However, this automatic snap detection point of origin is not always what the user desires.
Therefore, transform operations have a utility to set a new snap origin point during the transformation.
By default the hotkey is :kbd:`B`.


Add Snap Point
--------------

While you're transforming a selection with snapping enabled,
you can press :kbd:`A` whenever there's a highlighted snap target to
mark it. With multiple such targets marked, the selection will
then be snapped to their average location.

Marking a target more than once will give it more weight.

.. figure:: /images/editors_3dview_controls_snapping_target-multiple.png

   Multiple snapping targets.


Navigating
==========

While performing a modal transformation, you can perform navigation actions such as zooming,
panning, or rotating by holding :kbd:`Alt` then perform the desired action.
