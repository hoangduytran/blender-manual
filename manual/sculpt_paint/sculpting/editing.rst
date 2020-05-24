
*******
Editing
*******

Sculpt
======

.. _bpy.ops.sculpt.set_pivot_position:

Set Pivot
   Like Object and Edit Mode, Sculpt Mode also has a :term:`pivot point`.
   This is because the basic move, scale, rotate transforms are also possible in Sculpt Mode.

   Origin
      Sets the pivot to the origin of the sculpt.
   Unmasked
      Sets the pivot position to the average position of the unmasked vertices.
   Mask Border
      Sets the pivot position to the center of the mask's border.
   Active Vertex
      Sets the pivot position to the active vertex position.
   Surface
      Sets the pivot position to the surface under the cursor.

      .. seealso::

         :doc:`Object and Edit Mode Pivot </editors/3dview/controls/pivot_point/index>`

Rebuild BVH
   Recalculates the :term:`BVH` used by :doc:`/sculpt_paint/sculpting/tool_settings/dyntopo`
   which can improve performance which might degrade over time while using Dyntopo.


Mask
====

See :doc:`/sculpt_paint/sculpting/hide_mask`.


.. _sculpting-editing-facesets:

Face Sets
=========

Face Sets are another way to control the visibility state of the mesh in sculpt mode.
They are designed to work in modes where brushes are the primary way of interaction and they provide
much more control when working with meshes with complex shapes and overlapping surfaces.
Geometry can be assigned to a Face Set and each Face Set is represented as a different color in the 3D Viewport.
A pie menu to edit Face Sets can be accessed with :kbd:`W`.


Face Set From Masked
--------------------

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Face Sets --> Randomize Colors`

Creates a new Face Set from :ref:`Masked Geometry <sculpt-mask-menu>`.


Face Set From Visible
---------------------

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Face Sets --> Randomize Colors`

Creates a new Face Set from all visible geometry.


Invert Visible Face Sets
------------------------

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Face Sets --> Randomize Colors`


Show All Face Sets
------------------

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Face Sets --> Randomize Colors`

Hides all geometry that is part of a Face Set and makes all hidden geometry that is part of a face set visible.


Show All Face Sets
------------------

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Face Sets --> Randomize Colors`

Shows all hidden geometry that is part of a Face Set.


Randomize Colors
----------------

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Menu:      :menuselection:`Face Sets --> Randomize Colors`

Generates a new set of random colors to render the Face Sets in the 3D Viewport.
