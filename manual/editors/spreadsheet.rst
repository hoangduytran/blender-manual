.. index:: Editors; Spreadsheet

.. _bpy.ops.spreadsheet:
.. _bpy.types.SpaceSpreadsheet:

***********
Spreadsheet
***********

The Spreadsheet editor is used to inspect the geometry attributes of the :term:`active` object,
typically in order to debug :doc:`geometry nodes </modeling/geometry_nodes/introduction>`.

.. figure:: /images/editors_spreadsheet_interface.png
   :align: center

   The Spreadsheet editor.


Header
======

.. _bpy.types.SpaceSpreadsheet.object_eval_state:

Object Evaluation State
   The state for which to display data.

   :Evaluated: Display data from the object with all modifiers applied.
   :Original: Display data from the original object without any modifiers applied.
   :Viewer Node: Display the data that's fed into the active :doc:`/modeling/geometry_nodes/output/viewer`.

   You can also toggle between *Evaluated* and *Viewer Node* by clicking the eye icon in the
   Viewer node's header.

.. _bpy.types.SpaceSpreadsheet.display_context_path_collapsed:

Breadcrumbs
   Shows the name of the active object, and (if *Object Evaluation State* is set to *Viewer Node*)
   the name of the Geometry Nodes modifier and the active Viewer node.

   You can click one of the arrows between the names to hide the modifier.

.. _bpy.ops.spreadsheet.toggle_pin:

Toggle Pin
   Click to "lock" the editor to the currently active object, and have it keep displaying that
   object's data even if another object becomes active. Click again to unlock.

.. _bpy.types.SpaceSpreadsheet.show_only_selected:

Selected Only
   This option is only available if the object is in Edit Mode.
   When checked, only data for the selected geometry elements is shown.

.. _bpy.types.SpaceSpreadsheet.use_filter:

Use Filter
   Whether to use the filters that are defined in the Sidebar (see below).

Main Region
===========

The main view shows the actual spreadsheet.
Column names and row indices remain visible when scrolling down or to the side.

.. note::

   Byte color attributes are displayed as scene linear floats.
   The actual byte values are displayed in a tooltip when hovering over the float values.


.. _bpy.types.SpaceSpreadsheet.geometry_component_type:
.. _bpy.types.SpaceSpreadsheet.attribute_domain:

Data Set Region
===============

With region on the left, you can choose what to display data for.
The top tree lets you pick from the hierarchy of geometries, such as a mesh inside an instance.
The bottom tree lets you pick a domain, such as mesh vertices or curve splines.

Each tree item shows the number of elements inside.


Sidebar
=======

.. _bpy.ops.spreadsheet.add_row_filter_rule:

In the Sidebar, you can define filters so that only the rows matching these filters
are displayed. Click *Add Row Filter* and set up the properties described below.

.. _bpy.types.SpaceSpreadsheetRowFilter.enabled:

Enabled
   Uncheck to temporarily disable the filter.

.. _bpy.types.SpaceSpreadsheetRowFilter.column_name:

Column
   The name of the column to filter on. If there is no column with the specified name,
   the filter will be grayed out and ignored.

   If you want to filter on an attribute from another domain, you can use the
   :doc:`/modeling/geometry_nodes/attribute/store_named_attribute` to create a copy
   that's converted to the current domain, then filter on that.

.. _bpy.types.SpaceSpreadsheetRowFilter.operation:

Operation
   For numerical columns, you can select one of the following comparison operators.
   Other columns only support *Equal To*.

   :Equal To: Only display rows whose value for the column is equal to the filter value
      (within the specified threshold).
   :Greater Than: Only display rows whose value for the column is greater than the filter value.
   :Less Than: Only display rows whose value for the column is less than the filter value.

Value
   The filter value to compare the row value to.

.. _bpy.types.SpaceSpreadsheetRowFilter.threshold:

Threshold
   How much the row's value is allowed to deviate from the filter value before it is excluded.


Status Bar
==========

The status bar shows how many rows and columns there are, and how many rows remain after filtering.
