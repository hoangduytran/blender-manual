
*******
Options
*******

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Options`

Threaded Sculpt
   Takes advantage of multiple CPU processors to improve the sculpting performance.
Fast Navigate
   For *multiresolution* models, shows low resolution while navigating in the viewport.
Delay Viewport Updated
   Update the geometry when it enters view. This provides for faster navigation.
Use Deform Only
   Limits the activated modifiers on the active object to Deform Modifiers, and Multiresolution.
   Constructive modifiers (like Subdivision Surface, Mirror and other) get deactivated,
   because they could give inaccurate results.

Topology Automasking
   Brush affects only vertices connected to the active vertex under the brush.
Face Sets Automasking
   Affect only vertices that share face sets with active vertex.
Mesh Boundry Automasking
   Does not affect non manifold boundry edges.
Facesets Boundry Automasking
   Does not sffect vertices which belong to a face set boundry.

.. tip::

   The settings for above for Automasking apply across all sculpt brushes. However, the Automasking settings in
   :ref:`Advanced Brush Settings <sculpt-tool-settings-brush-settings-advanced>` apply per sculpt brush.

.. seealso::

   See the :ref:`Display <sculpt-paint-brush-display>` options.


Gravity
=======

Factor
   Setting the factor allows you to add gravity to your brush strokes,
   giving it a draping effect.
Orientation
   Using another object, the gravity can be oriented to the set object's local Z axis,
   changing the direction of the gravity.
