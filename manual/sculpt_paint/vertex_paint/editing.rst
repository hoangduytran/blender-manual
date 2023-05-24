
*******
Editing
*******

.. reference::

   :Mode:      Vertex Paint Mode
   :Menu:      :menuselection:`Paint`

.. _bpy.ops.paint.vertex_color_set:

Set Vertex Colors :kbd:`Shift-K`
   Fill the active Color Attribute with the current paint color.

.. _bpy.ops.paint.vertex_color_smooth:

Smooth Vertex Colors
   Smooth colors across vertices.

.. _bpy.ops.paint.vertex_color_dirt:

Dirty Vertex Colors
   Blur Strength
      Blur strength per iteration.
   Blur Iterations
      Number of times to blur the colors (higher blurs more).
   Highlight Angle
      Clamps the angle for convex areas of the mesh.
      Lower values increase the contrast but can result in clamping.
      90 means flat, 180 means infinitely pointed.
   Dirt Angle
      Clamps the angle for concave areas of the mesh.
      Higher values increase the contrast but can result in clamping.
      90 means flat, 0 means infinitely deep.
   Dirt Only
      When active it won't calculate cleans for convex areas.
   Normalize
      Choose optimal contrast by effectively lowering
      *Highlight Angle* and increasing *Dirt Angle* automatically.
      Disabling *Normalize* allows getting consistent results across multiple
      objects.

.. _bpy.ops.paint.vertex_color_from_weight:

Vertex Color from Weight
   Converts the active weight into grayscale colors.

.. _bpy.ops.paint.vertex_color_invert:

Invert
   Invert RGB values.

.. _bpy.ops.paint.vertex_color_levels:

Levels
   Adjust the levels of the selected vertices.

.. _bpy.ops.paint.vertex_color_hsv:

Hue/Saturation/Value
   Adjust the HSV values of the selected vertices.

.. _bpy.ops.paint.vertex_color_brightness_contrast:

Bright/Contrast
   Adjust the brightness/contrast of the selected vertices.
