

***********
Brush Types
***********

See :ref:`Brush Type <sculpt-tool-settings-brush-type>`.

Available brush types are listed here, together with links to the *Essentials* library brushes
using them.

Add/Subtract Brushes
====================

.. figure:: /images/sculpt-paint_sculpting_brushes_overview-add-substract.png
   :align: right
   :width: 250

These brush types generally push vertices outwards and inwards.

Draw
   Brushes: :doc:`draw`

   The standard brush for pushing vertices inwards and outwards from the surface direction.

Draw Sharp
   Brushes: :doc:`draw_sharp`

   Same as *Draw* but with a much sharper :doc:`Falloff </sculpt_paint/brush/falloff>`.
   Useful for creating creases and sharp angles.

Clay
   Brushes: :doc:`clay`

   Similar to the *Draw* brush but with a flattening effect and subtle smoothing.
   Useful for polishing and building volumes.

Clay Strips
   Brushes: :doc:`clay_strips`

   The same as the *Clay* brush, but more aggressive with a square falloff.
   A common standard for building rough volumes.

Layer
   Brushes: :doc:`layer`

   Draw with a fixed height. Useful for adding flat layers to a surface.

Inflate
   Brushes: :doc:`inflate`

   Moves the mesh in multiple direction. Useful for inflating or shrinking surfaces and volumes.

Blob
   Brushes: :doc:`blob`

   Magnifies the mesh as you draw. Useful for an additional inflation effect on the stroke.

Crease
   Brushes: :doc:`crease`

   Same as *Blob* but with a pinching effect. Useful for creating and polishing sharp creases.


Contrast Brushes
================

.. figure:: /images/sculpt-paint_sculpting_brushes_overview-contrast.png
   :align: right
   :width: 250

Recognizable by their red icon and cursor.
These brushes generally flatten or heighten the contrast of the surface.

Smooth
   Brushes: :doc:`smooth`

   Smooths out irregularities in the surface and shrinks volumes by averaging the vertices positions.
   An essential brush that is frequently used.

Flatten
   Brushes: :doc:`flatten`

   Pushes vertices to an average height to create a flat plateau.

Fill
   Brushes: :doc:`fill`

   Pushes surfaces outwards. Useful for filling in holes and crevices.

Scrape
   Brushes: :doc:`scrape`

   Pushes surfaces inwards. This is the most common brush for flattening meshes.

Multi-plane Scrape
   Brushes: :doc:`multiplane_scrape`

   Scrapes the mesh with two angled planes at the same time, producing a sharp edge between them.


Transform Brushes
=================

.. figure:: /images/sculpt-paint_sculpting_brushes_overview-transform.png
   :align: right
   :width: 250

Recognizable by their yellow icon and cursor.
These brushes generally move, pinch and magnify the mesh.

Pinch
   Brushes: :doc:`pinch`

   Pulls vertices towards the center of the brush. Useful for polishing angles and creases.

Grab
   Brushes: :doc:`grab`

   Moves vertices along with the mouse. An essential brush for building shapes and adjusting proportions.

Elastic Deform
   Brushes: :doc:`elastic_deform`

   Used to simulate realistic deformations such as grabbing or twisting of :term:`Elastic` objects.

Snake Hook
   Brushes: :doc:`snake_hook`

   Pulls vertices along with the stroke to create long, snake-like forms.

Thumb
   Brushes: :doc:`thumb`

   Same as *Grab* but moves vertices along the surface direction. Useful for preserving specific surfaces.

Pose
   Brushes: :doc:`pose`

   Simulating an armature-like deformations. Useful for quick posing and transformations.

Nudge
   Brushes: :doc:`nudge`

   Similar as *Thumb* but dynamically picks up vertices like the *Snake Hook*.
   Useful for nudging something along the mesh surface.

Rotate
   Brushes: :doc:`twist`

   Rotates vertices within the brush in the direction mouse.

Slide Relax
   Brushes: :doc:`slide_relax`

   Slides the topology of the mesh in the direction of the stroke
   while preserving the geometrical shape of the mesh.
   Also useful for redistributing topology where it is needed.

Boundary
   Brushes: :doc:`boundary`

   Transform mesh boundaries specifically with various deformations.


Utility Brushes
===============

.. figure:: /images/sculpt-paint_sculpting_brushes_overview-utilities.png
   :align: right
   :width: 250

No clear color assignment.
These brushes are general purpose brushes or specific.

Cloth
   Brushes: :doc:`cloth`

   Simulates cloth to create folds and draping, which can be sculpted further.

Simplify
   Brushes: :doc:`density`

   Cleans up geometry by collapsing short edges.

Mask
   Brushes: :doc:`mask`

   Paints a selection on parts of the mesh to be unaffected by other brushes.

Draw Face Sets
   Brushes: :doc:`draw_facesets`

   Paint new or extend existing face sets.

Multires Displacement Eraser
   Brushes: :doc:`multires_displacement_eraser`

   Remove displacement information on a Multiresolution modifier.

Multires Displacement Smear
   Brushes: :doc:`multires_displacement_smear`

   Smear displacement information on a Multiresolution modifier.


Painting Brushes
================

.. figure:: /images/sculpt-paint_sculpting_brushes_overview-paint.png
   :align: right
   :width: 250

Recognizable by their green icon.
These brushes are used for painting color attributes within sculpt mode.

Paint
   Brushes: :doc:`paint`

   Paint on the vertices of your mesh via color attributes.

Smear
   Brushes: :doc:`smear`

   Smears the vertex colors via color attributes.

