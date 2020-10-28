
**********
Lasso Trim
**********

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Lasso Trim`

Adds or removes geometry using a boolean operation based on a :ref:`lasso selection <tool-select-lasso>`.

Trim Mode
   The operation to perform on the mesh; geometry can be either added or removed.
   When using the *Union* or *Join* mode the new geometry is assigned to a new
   :ref:`Face Set <sculpting-editing-facesets>`.

   Difference
      Removes geometry in the shape of the selection filling any holes that are created in existing geometry.
   Union
      Fills the selected outline with a new mesh and joins any intersections with existing geometry.
   Join
      Similar to *Union* but joins the mesh as separate geometry,
      without performing any boolean operations with existing geometry.
