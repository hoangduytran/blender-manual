
****************
Images as Planes
****************

.. reference::

   :Category:  Import-Export
   :Menu:      :menuselection:`File --> Import --> Images as Planes`,
               :menuselection:`3D Viewport --> Add --> Image --> Images as Planes`

.. figure:: /images/addons_import-export_images-as-planes_panel.png
   :align: right
   :width: 200px

   Properties panel.

This add-on imports images and creates planes with them as textures.
It automates the process of creating a plane, resizing it to fit the dimensions of the image,
and creating a material with the image texture to it.
The name of the plane, material, and texture will be derived from the name of the image file.

You can import a single image, multiple images, or an image sequence/movie clip.
If you choose a single image, it creates one plane; if you choose multiple images,
it creates as many planes as the number of images you selected, either stacked on top of each other or spaced apart.
Selecting a movie clip or an image sequence will create a single plane with an animation.


Properties
==========

You can save the current import settings as an :ref:`Operator Preset <ui-presets>`.


Import Options
--------------

Relative Path
   Set link to the image file using a :ref:`relative file path <files-blend-relative_paths>`.

Force Reload
   Reload the image file if it already exists as an image data-block.

Animate Image Sequences
   Import sequentially numbered images as
   an animated :doc:`image sequence </video_editing/edit/montage/strips/image>` instead of separate planes.
   They will be imported as a *Clip* texture on a single plane.
   The frame range will be automatically set but can be changed later.


Compositing Nodes
-----------------

Setup Corner Pin
   Add a compositing setup of the Image Texture, Scale, and :doc:`Corner Pin </compositing/types/distort/corner_pin>`
   nodes to inject a warped view of the image into the compositor output. The add-on adds drivers to
   the corner values of the Corner Pin node so that transforms of the plane and camera drive them.
   Make sure to have an active camera in the scene before the import.

.. note::

   You may want to disable the plane object from the final render to prevent it from overlapping the image in
   the composite.


Material Settings
-----------------

Images as Planes sets up a material to display the image. You can set the type of material and related settings
before the import.

Material Type
   :Principled:
      The material will have a :doc:`Principled BSDF </render/shader_nodes/shader/principled>` shader node
      with default settings as its main component.
      An Image Texture node linked to the imported image will be connected to the Base Color of the Principled
      BSDF node.
   :Shadeless:
      A shadeless material is a material that does not respond to light from other objects and always has the same
      color in any lighting environment.
      This option creates a material with a node group of a mix between a Diffuse and an Emission shader controlled
      by a Light Path node.
   :Emit:
      The material will have a Principled BSDF shader node as its main component, but the Color output from
      the Image Texture node will be linked to the Emission input instead of the Base Color.

      Strength
         Set the strength of the emission.

.. note::

   *Blend Mode* and *Shadow Mode* options are specific to the Eevee renderer.
   For a detailed explanation of each option, see :doc:`Material Settings </render/eevee/materials/settings>`.

Blend Mode
   Set the alpha blend mode of the material.

Show Backface
   Show backside of the transparent part.

Shadow Mode
   Set the shadow mode of the material.

Backface Culling
   Hide backside of the plane.

Overwrite Material
   The add-on sets the name of the new material from the name of the imported image. However, if there is already
   a material with the same name, Blender will append a number to the name of the material to avoid conflict.
   This *Override Material* option makes it overwrite the existing material of the same name in that case.


Texture Settings
----------------

.. note::

   For a detailed explanation of each option, see :doc:`Image Texture Node </render/shader_nodes/textures/image>`.

Interpolation
   Set the method to scale the image.

Extension
   Set how the image is extrapolated past the original bounds.

Use Alpha
   Use the alpha channel of the image for transparency.

Auto Refresh
   Automatically refresh the images in the viewport on frame changes.


Position
--------

Images as Planes creates the plane at the 3D Cursor's location. With *Offset Planes*, multiple planes will be
placed with distance intervals set in *Offset*, along the axis set in *Local Axis*, beginning at the 3D Cursor's
location.

Offset Planes
   Place multiple planes with an offset. If disabled, all planes will be created at the same location.

Local Axis
   Choose a local axis (not the global axis) to offset the planes. For example, if you choose *X+*, the planes
   will be placed along the positive direction of the plane's local X axis.

Offset
   Set a distance between each plane.


Plane Dimensions
----------------

Set how the plane's size will be determined.

Absolute
   The size of the plane will be set based on the height value set in *Height*. The width will be set in direct
   ratio to the height value. For example, with the default height value of 1 m, an image of 800 × 600 pixels
   will have a width of 1 / 600 × 800 or 1.33 m.

   Height
      Set the height of the plane.

Camera Relative
   The size of the plane will be set to fit or fill the camera frame. This will automatically set the *Align*
   option to *Face Camera*. Make sure to have an active camera in the scene before the import.

   :Fit:
      Scale the plane to fit inside the camera frame while preserving the aspect ratio.
   :Fill:
      Scale the plane so that it fills the entire camera view while preserving the aspect ratio, but some part of
      the image can spill outside the camera frame.

:abbr:`DPI (Dots per inch)`
   The size of the plane will be set based on the pixels per inch value set in *Definition*. With the *Unit System*
   set to *Metric* and the default definition of 600 DPI, an image of 800 × 600 pixels will have a size of
   0.0339 × 0.0254 units since 600 pixels are defined as 1 inch (0.0254 m).

   Definition
      Set the number of pixels to fit in 1 inch.

Dots/BU
   The size of the plane will be set based on the pixels per Blender Unit set in *Definition*. With the default
   definition value of 600, an image of 800 × 600 pixels will have a size of 1.33 × 1 units.

   Definition
      Set the number of pixels to fit in 1 Blender Unit.


Orientation
-----------

Align
   Set the rotation of the plane.

   :Main Axis:
      The plane will be aligned to a major axis that is best to face the camera's view direction.
      If there is no camera in the scene, the plane will face toward Z+ (Up) axis.
   :Face Camera:
      Similar to the *Main Axis* but the plane will be rotated to directly face the camera's view direction.
   :Z- (Down), Y-, X-, Z+ (Up), Y+, X+:
      The plane will be rotated to face toward the selected axis.

Track Camera
   Add a :doc:`Locked Track </animation/constraints/tracking/locked_track>` constraint to make the plane always
   face the camera, even if the camera moves. This option is only available when *Main Axis* or *Face Camera*
   option is selected in the *Align* menu.
