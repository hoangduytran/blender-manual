
*************
Select Mirror
*************

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Mirror Selection`
   :Hotkey:    :kbd:`Shift-Ctrl-M`

*Mirror Selection* will take an existing selection, whether it be a group of faces, edges, or vertices, and flip it to the opposite side of the mesh.

Axis
   Choose on which axis the *Mirror Selection* will occur. The axis is based on the meshes *Origin Ponit*. Therefore, if the *Origin Point* is not centered within the mesh, the selection will have varying results.
   
Extend
   The new selection will include the mirrored selection as well as the original.

.. figure:: /images/modeling_meshes_selecting_mirror_extend.png 
   
   (from left to right) Initial Selection, After Mirror Selection on X-Axis, With Extend.

.. tip::
   
   With *Extend* activated, hold :kbd:`Shift` while chosing an axis to include more than one axis in the selection. Otherwise, with *Extend* off, the mirror will take into account two to three axes.
   
Example

.. figure:: /images/modeling_meshes_selecting_mirror_axis-xz-extend.png
   
   (from left to right) Initial Selection, Mirrored along X and Z axes, With Extend.
