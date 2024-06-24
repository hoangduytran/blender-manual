
*******
Toolbar
*******

The amount of tools in sculpt mode is very extensive.
This is an overview of all of them, categorized by their general functions.


Add/Subtract Brushes
====================

.. figure:: /images/sculpt-paint_sculpting_toolbar_add_subt_brushes.png
   :align: right

Recognizable by their blue icon and cursor.
These brushes generally push vertices outwards and inwards.

:doc:`/sculpt_paint/sculpting/tools/draw`
   The standard brush for pushing vertices inwards and outwards from the surface direction.

:doc:`/sculpt_paint/sculpting/tools/draw_sharp`
   Same as *Draw* but with a much sharper :doc:`Falloff </sculpt_paint/brush/falloff>`.
   Useful for creating creases and sharp angles.

:doc:`/sculpt_paint/sculpting/tools/clay`
   Similar to the *Draw* brush but with a flattening effect and subtle smoothing.
   Useful for polishing and building volumes.

:doc:`/sculpt_paint/sculpting/tools/clay_strips`
   The same as the *Clay* brush, but more aggressive with a square falloff.
   A common standard for building rough volumes.

:doc:`/sculpt_paint/sculpting/tools/layer`
   Draw with a fixed height. Useful for adding flat layers to a surface.

:doc:`/sculpt_paint/sculpting/tools/inflate`
   Moves the mesh in multiple direction. Useful for inflating or shrinking surfaces and volumes.

:doc:`/sculpt_paint/sculpting/tools/blob`
   Magnifies the mesh as you draw. Useful for an additional inflation effect on the stroke.

:doc:`/sculpt_paint/sculpting/tools/crease`
   Same as *Blob* but with a pinching effect. Useful for creating and polishing sharp creases.

Contrast Brushes
================

.. figure:: /images/sculpt-paint_sculpting_toolbar_contrast_brushes.png
   :align: right

Recognizable by their red icon and cursor.
These brushes generally flatten or heighten the contrast of the surface.

:doc:`/sculpt_paint/sculpting/tools/smooth`
   Smooths out irregularities in the surface and shrinks volumes by averaging the vertices positions.
   An essential brush that is frequently used.

:doc:`/sculpt_paint/sculpting/tools/flatten`
   Pushes vertices to an average height to create a flat plateau.

:doc:`/sculpt_paint/sculpting/tools/fill`
   Pushes surfaces outwards. Useful for filling in holes and crevices.

:doc:`/sculpt_paint/sculpting/tools/scrape`
   Pushes surfaces inwards. This is the most common brush for flattening meshes.

:doc:`/sculpt_paint/sculpting/tools/multiplane_scrape`
   Scrapes the mesh with two angled planes at the same time, producing a sharp edge between them.


Transform Brushes
=================

.. figure:: /images/sculpt-paint_sculpting_toolbar_transform_brushes.png
   :align: right

Recognizable by their yellow icon and cursor.
These brushes generally move, pinch and magnify the mesh.

:doc:`/sculpt_paint/sculpting/tools/pinch`
   Pulls vertices towards the center of the brush. Useful for polishing angles and creases.

:doc:`/sculpt_paint/sculpting/tools/grab`
   Moves vertices along with the mouse. An essential brush for building shapes and adjusting proportions.

:doc:`/sculpt_paint/sculpting/tools/elastic_deform`
   Used to simulate realistic deformations such as grabbing or twisting of :term:`Elastic` objects.

:doc:`/sculpt_paint/sculpting/tools/snake_hook`
   Pulls vertices along with the stroke to create long, snake-like forms.

:doc:`/sculpt_paint/sculpting/tools/thumb`
   Same as *Grab* but moves vertices along the surface direction. Useful for preserving specific surfaces.

:doc:`/sculpt_paint/sculpting/tools/pose`
   Simulating an armature-like deformations. Useful for quick posing and transformations.

:doc:`/sculpt_paint/sculpting/tools/nudge`
   Similar as *Thumb* but dynamically picks up vertices like the *Snake Hook*.
   Useful for nudging something along the mesh surface.

:doc:`/sculpt_paint/sculpting/tools/rotate`
   Rotates vertices within the brush in the direction mouse.

:doc:`/sculpt_paint/sculpting/tools/slide_relax`
   Slides the topology of the mesh in the direction of the stroke
   while preserving the geometrical shape of the mesh.
   Also useful for redistributing topology where it is needed.

:doc:`/sculpt_paint/sculpting/tools/boundary`
   Transform mesh boundaries specifically with various deformations.


General Brushes
===============

.. figure:: /images/sculpt-paint_sculpting_toolbar_general_brushes.png
   :align: right

No clear color assignment.
These brushes are general purpose brushes or specific.

:doc:`/sculpt_paint/sculpting/tools/cloth`
   Simulates cloth to create folds and draping, which can be sculpted further.

:doc:`/sculpt_paint/sculpting/tools/simplify`
   Cleans up geometry by collapsing short edges.

:doc:`/sculpt_paint/sculpting/tools/mask`
   Paints a selection on parts of the mesh to be unaffected by other brushes.

:doc:`/sculpt_paint/sculpting/tools/draw_facesets`
   Paint new or extend existing face sets.

:doc:`/sculpt_paint/sculpting/tools/multires_displacement_eraser`
   Remove displacement information on a Multiresolution modifier.

:doc:`/sculpt_paint/sculpting/tools/multires_displacement_smear`
   Smear displacement information on a Multiresolution modifier.


Painting Brushes
================

.. figure:: /images/sculpt-paint_sculpting_toolbar_paint.png
   :align: right

Recognizable by their green icon.
These brushes are used for painting color attributes within sculpt mode.

:doc:`/sculpt_paint/sculpting/tools/paint`
   Paint on the vertices of your mesh via color attributes.

:doc:`/sculpt_paint/sculpting/tools/smear`
   Smears the vertex colors via color attributes.


Gesture Tools
=============

.. figure:: /images/sculpt-paint_sculpting_toolbar_gestures.png
   :align: right

General gesture tools to apply an operation via box, lasso, line and polyline shapes. 
See :doc:`/sculpt_paint/sculpting/introduction/gesture_tools` for more information.

:doc:`/sculpt_paint/sculpting/tools/mask_tools`
   Create a mask via a gesture.

Box Hide
   Hides/Shows geometry via a box gesture.

:doc:`/sculpt_paint/sculpting/tools/box_face_set`
   Create a face set via a box gesture.

:doc:`/sculpt_paint/sculpting/tools/lasso_face_set`
   Create a face set via a lasso gesture.

:doc:`/sculpt_paint/sculpting/tools/box_trim`
   Perform a Boolean operation via a box gesture.

:doc:`/sculpt_paint/sculpting/tools/lasso_trim`
   Perform a Boolean operation via a lasso gesture.

:doc:`/sculpt_paint/sculpting/tools/line_project`
   Flatten the geometry towards a drawn line.


Filter Tools
============

.. figure:: /images/sculpt-paint_sculpting_toolbar_filters.png
   :align: right

Tools for applying effects on the entire unmasked and visible mesh.

:doc:`/sculpt_paint/sculpting/tools/mesh_filter`
   Apply a deformation to all unmasked vertices.

:doc:`/sculpt_paint/sculpting/tools/cloth_filter`
   Applies a cloth simulation to all unmasked vertices.

:doc:`/sculpt_paint/sculpting/tools/color_filter`
   Changes the active color attribute on all unmasked vertices.


Single Click Tools
==================

.. figure:: /images/sculpt-paint_sculpting_toolbar_singleclick.png
   :align: right

Simpler tools that apply an operation on surfaces that are clicked on.

:doc:`/sculpt_paint/sculpting/tools/edit_face_set`
   Modifies the face set under the cursor.

:doc:`/sculpt_paint/sculpting/tools/mask_by_color`
   Create a mask from any color from the color attribute by clicking on it.


General Tools
=============

.. figure:: /images/sculpt-paint_sculpting_toolbar_general.png
   :align: right

General transform and annotate tools like in other modes.

:doc:`Move </sculpt_paint/sculpting/tools/transforms>`
   Translation tool.

:doc:`Rotate </sculpt_paint/sculpting/tools/transforms>`
   Rotation tool.

:doc:`Scale </sculpt_paint/sculpting/tools/transforms>`
   Scale tool.

:doc:`Transform </sculpt_paint/sculpting/tools/transforms>`
   Adjust the objects translation, rotations and scale.

:ref:`Annotate <tool-annotate-freehand>`
   Draw free-hand annotation.

   :ref:`Annotate Line <tool-annotate-line>`
      Draw straight line annotation.
   :ref:`Annotate Polygon <tool-annotate-polygon>`
      Draw a polygon annotation.
   :ref:`Annotate Eraser <tool-annotate-eraser>`
      Erase previous drawn annotations.
