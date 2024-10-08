
***********
Stroke Menu
***********

This page covers many of the tools in the *Strokes* menu.
These are tools that work primarily on strokes, however,
some also work with point selections.


.. _bpy.ops.grease_pencil.stroke_subdivide:

Subdivide
=========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Subdivide`

Subdivides the strokes by inserting points between the selected points.

Number of Cuts
   The number of subdivisions to perform.
Selected Points
   When enabled, limits the effect to only the selected points within the stroke.


.. _bpy.ops.grease_pencil.stroke_subdivide_smooth:

Subdivide and Smooth
====================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Subdivide and Smooth`


Subdivides and smooths the strokes by inserting points between the selected points.

Number of Cuts
   The number of subdivisions to perform.
Selected Points
   When enabled, limits the effect to only the selected points within the stroke.
Iterations
   Number of times to repeat the procedure.
Factor
   The amount of the smoothness on subdivided points.
Smooth Endpoints
   Smooths the stroke's endpoints.
Keep Shape
   Preserves the strokes shape.
Position
   When enabled, the operator affect the points location.
Radius
   When enabled, the operator affect the points thickness.
Opacity
   When enabled, the operator affect the points strength (alpha).


.. _bpy.ops.grease_pencil.stroke_simplify:

Simplify
========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Simplify`

Uses the RDP algorithm (Ramer-Douglas-Peucker algorithm) for points deletion.
The algorithm tries to obtain a similar line shape with fewer points.

Factor
   Controls the amount of recursively simplifications applied by the algorithm.


.. .. _bpy.ops.gpencil.stroke_simplify_fixed:

.. Fixed
.. -----

.. Deletes alternated points in the strokes, except the start and end points.

.. Steps
..    The number of times to repeat the procedure.


.. .. _bpy.ops.gpencil.stroke_sample:

.. Sample
.. ------

.. Recreates the stroke geometry with a predefined length between points.

.. Length
..    The distance between points on the recreated stroke.
..    Smaller values will require more points to recreate the stroke,
..    while larger values will result in fewer points needed to recreate the curve.
.. Sharp Threshold
..    The maximum angle between points on the recreated stroke.
..    Smaller values will require more points to recreate the stroke,
..    while larger values will result in fewer points needed to recreate the curve.


.. _bpy.ops.gpencil.stroke_trim:

Trim
====

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Trim`

Trims selected stroke to first loop or intersection.

.. list-table::

   * - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_trim-1.png
          :width: 320px

          Original stroke.

     - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_trim-2.png
          :width: 320px

          Result of trim operation.


.. .. _bpy.ops.gpencil.stroke_outline:

.. Outline
.. =======

.. .. reference::

..    :Mode:      Edit Mode
..    :Menu:      :menuselection:`Stroke --> Outline`

.. Converts a stroke to an outline.

.. View
..    The projection method to generate the outline

..    :View: Use the viewport's view as a projection.
..    :Front: Use the X-Z axes view as a projection.
..    :Side: use the Y-Z axis view as a projection
..    :Top: Use the X-Y axes view as a projection
..    :Camera: Use the view from the active camera as a projection.
.. Material Mode
..    How materials are assigned to the outline.

..    :Active Material: The stroke outline will be assigned the active material.
..    :Keep Material: The stoke outline will have the same material as before.
..    :New Material: A new material will be created and assigned to the outline.
.. Thickness
..    Thickness of the stroke perimeter.
.. Keep Shape
..    Try to keep global shape when the stroke thickness change.
.. Subdivisions
..    Number of subdivisions for the start and end caps.
.. Sample Length
..    The length each resulting segment of the outline.
..    Smaller values create outlines closer to the original shape.

.. .. list-table::

..    * - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_outline-1.png
..           :width: 320px

..           Original stroke.

..      - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_outline-2.png
..           :width: 320px

..           Generated stroke after outline operation.


Join
====

.. _bpy.ops.grease_pencil.join_selection:

Join
----

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Join --> Join,`
   :Shortcut:  :kbd:`Ctrl-J`

Join two or more strokes into a single one.

Type
   :Join:
      Join selected strokes by connecting points.
   :Join and Copy:
      Join selected strokes by connecting points in a new stroke.
Leave Gaps
   When enabled, do not use geometry to connect the strokes.


Join and Copy
-------------

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Join --> Join and Copy`
   :Shortcut:  :kbd:`Shift-Ctrl-J`

Same as :ref:`grease_pencil.join_selection` but *Type* defaults to *Join and Copy*.


.. _bpy.ops.grease_pencil.move_to_layer:

Move to Layer
=============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Move to Layer`
   :Shortcut:  :kbd:`M`

A pop-up menu to move the stroke to a different layer.
You can choose the layer to move the selected strokes to
from a list of layers of the current Grease Pencil object.
You can also add a new layer to move the selected stroke to.
When creating a new layer, there is another pop-up to type in the name of the new layer.


.. _bpy.ops.grease_pencil.stroke_material_set:

Assign Material
===============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Assign Material`

Changes the material linked to the selected stroke.
You can choose the name of the material to be used by the selected stroke
from a list of materials of the current Grease Pencil object.


.. _bpy.ops.grease_pencil.set_active_material:

Set as Active Material
======================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set as Active Material`

Sets the active object material based on the selected stroke material.


.. _bpy.ops.grease_pencil.reorder:

Arrange
=======

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Arrange`

Change the drawing order of the strokes in the 2D layer.

Bring to Front
   Moves to the top the selected points/strokes.
Bring Forward
   Moves the selected points/strokes upper the next one in the drawing order.
Send Backward
   Moves the selected points/strokes below the previous one in the drawing order.
Send to Back
   Moves to the bottom the selected points/strokes.


.. _bpy.ops.grease_pencil.cyclical_set:

Close
=====

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Close`
   :Shortcut:  :kbd:`F`

Close or open strokes by connecting the last and first point.

Type
   :Close All: Close all open selected strokes.
   :Open All: Open all closed selected strokes.
   :Toggle: Close or Open selected strokes as required.

.. Create Geometry
..    When enabled, points are added for closing the strokes.
..    If disabled, the operator act the same as *Toggle Cyclic*.


Toggle Cyclic
=============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Toggle Cyclic`

Toggles between an open stroke and closed stroke (cyclic).

Type
   :Close All: Close all open selected strokes.
   :Open All: Open all closed selected strokes.
   :Toggle: Close or Open selected strokes as required.

.. Create Geometry
..    When enabled, points are added for closing the strokes like when using the *Close* tool.
..    If disabled, the stroke is close without any actual geometry.


.. _bpy.ops.grease_pencil.caps_set:

Set Caps
========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set Caps`

Toggle ending cap styles of the stroke.

Rounded
   Sets stroke start and end points to rounded (default).

Flat
   Toggle stroke start and end points caps to flat or rounded.

Toggle Start
   Toggle stroke start point cap to flat or rounded.

Toggle End
   Toggle stroke end point cap to flat or rounded.

.. list-table::

   * - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_cap-1.png
          :width: 200px

          Stroke ending with rounded caps.

     - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_cap-2.png
          :width: 200px

          Stroke ending with flat caps.

     - .. figure:: /images/grease-pencil_modes_edit_stroke-menu_cap-3.png
          :width: 200px

          Stroke ending with combined caps.


.. _bpy.ops.grease_pencil.stroke_switch_direction:

Switch Direction
================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Switch Direction`

Reverse the direction of the points in the selected strokes
(i.e. the start point will become the end one, and vice versa).


.. .. _bpy.ops.gpencil.stroke_start_set:

.. Set Start Point
.. ===============

.. .. reference::

..    :Mode:      Edit Mode
..    :Menu:      :menuselection:`Stroke --> Set Start Point`

.. Set the start point for cyclic strokes.


.. _bpy.ops.grease_pencil.set_uniform_thickness:

Set Uniform Thickness
=====================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set Uniform Thickness`

Makes the thickness equal for the entire stroke.

Thickness
   Thickness value to use on all points of the stroke.


.. _bpy.ops.grease_pencil.set_uniform_opacity:

Set Uniform Opacity
===================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set Uniform Opacity`

Makes the opacity equal for the entire stroke.

Opacity
   Opacity value to use on all points of the stroke.


.. _bpy.types.GPencilSculptSettings.use_scale_thickness:

Scale Thickness
===============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Scale Thickness`

When enabled, scales the stroke thickness during scale transformations.


.. Reset Fill Transform
.. ====================

.. .. reference::

..    :Mode:      Edit Mode
..    :Menu:      :menuselection:`Stroke --> Reset Fill Transform`

.. Reset all fill translation, scaling and rotations in the selected strokes.


.. _bpy.ops.grease_pencil.set_curve_type:

Set Curve Type
==============

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set Curve Type`

Sets the spline type for the splines in the stroke component that are in the selection.

Type
   The type to convert the splines in the selection to.
   Read the :ref:`Spline Types <curve-spline-types>` page for more details
   on the different spline types.

   :Bézier:
      Convert to a Bézier spline. A spline converted from a poly spline gets vector handles,
      while one converted from NURBS or Catmull Rom spline gets auto handles.

      .. note::

         When converting from a NURBS spline to a Bézier spline, at least six points are needed.
         When the number of points is not a multiple of three a full
         conversion is not possible and the spline has to be truncated.

   :NURBS: Convert to a NURBS spline.
   :Poly: Convert to a poly spline.
   :Catmull Rom: Convert to a Catmull Rom spline.

Handles
   Take handle information into account in the conversion


.. _bpy.ops.grease_pencil.set_curve_resolution:

Set Curve Resolution
====================

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set Curve Resolution`

Sets the :ref:`Curve Resolution <bpy.types.GreasePencil.edit_curve_resolution>` value.


.. _bpy.ops.grease_pencil.reset_uvs:

Reset UVs
=========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Stroke --> Set Curve Resolution`

Reset UV transformation to default values.
