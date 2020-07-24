
**************
Side of Active
**************

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Side of Active`

With an active vertex, this method will select all vertices in a specified direction. This acts similarly to *Loop Inner-Region* in that it will fill select faces within its parameters, however, this method is determined by direction and not by a closed loop.

.. figure:: /images/modeling_meshes_selecting_side-active_example.png
   
   Must have one vertex actively selected.

From the image above, after selecting a vertex, find *Side of Active* in the *Select* menu. From there, the direction to fill select can be determined by the tool options:

Axis Mode
   Determines the behavior of the selection. More information on this can be found in :doc:`Tranform Orientations </editors/3dview/controls/orientation>`.

Axis Sign
   Depending on which *Axis* is chosen, the selection will encompass the positve or negative portion of that axis starting from the active vertex outward.
      
   Aligned Axis
      Where *Postitive and Negative Axis* select all vertices in a given direction, *Aligned Axis* will only select the vertices that are inline with the active vertex.

.. figure:: /images/modeling_meshes_selecting_side-active_sign.png
   
   While following along the X Axis: (from left to right) Active Vertex, Aligned, Positive, Negative.

Axis
   Chooses which direction/dimension the selection will go in.

Threshold
   The amount of influence the selection has outside original parameters. The higher the *threshold* the more vertices will be selected.
