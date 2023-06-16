.. _bpy.ops.curve.primitive*add:

**********
Primitives
**********

.. reference::

   :Mode:      Object Mode and Edit Mode
   :Menu:      :menuselection:`Add --> Curve`
   :Shortcut:  :kbd:`Shift-A`

.. seealso::

   When adding curves there are some common options like other :ref:`Objects <object-common-options>`.

.. note::

   Eventually all the primitive curves will be replaced to use the same curve system used for hair curves.
   Until this is done, their features will diverge.

   They can be converted interchangeably to access the full range of edit and sculpting functionalities.

In Object/Edit Mode, the *Add Curve* menu, provides a few different curve primitives:


Bézier Curve
============

Adds an open 2D Bézier curve with two control points.


Bézier Circle
=============

Adds a closed, circle-shaped 2D Bézier curve (made of four control points).


NURBS Curve
===========

Adds an open 2D :term:`NURBS` curve, with four control points, with *Uniform* knots.


NURBS Circle
============

Adds a closed, circle-shaped 2D :term:`NURBS` curve (made of eight control points).


Path
====

Adds a :term:`NURBS` open 3D curve made of five aligned control points,
with *Endpoint* knots and the *Curve Path* setting enabled.


.. _bpy.ops.object.curves_empty_hair_add:

Empty Hair
==========

Adds an empty high-performance curves object and automatically:

* Assigns the active object as the :doc:`Surface </sculpt_paint/curves_sculpting/introduction>`.
* Set the surface object as the parent of the new object.
* Adds a Geometry Nodes modifier to deform the curves on the surface.


Selecting
---------

Hair curves, while similar to regular curves are a bit different and have their own selection tools.
Many of these match their regular curve tools but are implemented differently
All hair curve selection operators are documented below for completeness.

These selection operators work in both Sculpt and Edit modes.


.. _bpy.ops.curves.set_selection_domain:

Selection Modes
^^^^^^^^^^^^^^^

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`3D Viewport Header --> Select Mode`
   :Shortcut:  :kbd:`1`, :kbd:`2`

   Note, this is only supported for "Hair Curves".

Selection modes limits selection operators to certain curve domains.
This feature is makes it easy to select whole segments at once, or to give more granular control over editing.

:Control Points:
   Allows selection of individual control points.
:Curve:
   Limits selection to whole curve segments.


Operators
^^^^^^^^^

All
   Select all control points or curves.

None
   Deselect all control points or curves.

Invert
   Invert the selection.

Random
   Randomizes inside the existing selection or create new random selection if nothing is selected already.

Endpoints
   Select endpoints of curves.
   Only supported in the Control Point selection mode.

Grow
   Select points or curves which are close to already selected elements.


Editing
-------

The curves can be edited via :doc:`sculpting </sculpt_paint/curves_sculpting/introduction>`.

Curves objects also have basic editing support in "Edit Mode".
Currently, only the basic :ref:`Transform <modeling-curves-transform>` and Delete operators are supported.

.. _bpy.ops.curves.delete:

The Delete operator can remove Control Points or Segments.
Deleting can be used to make curves shorter or simplify
segments by deleting control points in the mid section of a segment.


Properties
----------

Hair Curves have different properties than regular Curve objects;
these properties are documented below.


Attributes
^^^^^^^^^^

The *Attributes* panel contains different hair characteristics such as the position and color of hair strands.

Use the :ref:`List View <ui-list-view>` to manage attributes.

.. seealso::

   See the :doc:`Attribute Reference </modeling/geometry_nodes/attributes_reference>` for details on attributes.


Surface
^^^^^^^

.. _bpy.types.Curves.surface:

Surface
   The curve surface is an optional mesh that is used to anchor the curves, and behave as a scalp for hair grooming.
   When adding a new Curves object via the `Add Menu` the active object is automatically set as the surface.

   To set a new surface press :kbd:`Ctrl-P` and select *Object (Attach Curves to Surface)*
   in the *Set Parent To* pop-up menu. This option can be seen as part of the Curves settings in the Properties
   Editor.

   .. figure:: /images/sculpt-paint_sculpting_curves-surface.png

.. _bpy.types.Curves.surface_uv_map:

Surface UV Map
   The name of the attribute on the surface mesh used to define the attachment of each curve.

   .. note::

      If the UV from the surface changed,
      run :ref:`Snap to Nearest Surfaces <bpy.ops.curves.snap_curves_to_surface>` to re-attach the curves.


Fur
===

Adds a fur setup to the selected objects.
The fur setup is based on :doc:`/modeling/geometry_nodes/index` and built with
:doc:`Hair Node Groups </modeling/geometry_nodes/hair/index>` that come with Blender as bundled assets.

See :ref:`bpy.ops.object.quick_fur` for more information.
