.. _bpy.types.GreasePencilLayer:

******
Layers
******

.. reference::

   :Mode:      All Modes
   :Panel:     :menuselection:`Object Data tab --> Layers`
   :Shortcut:  :kbd:`Y`

.. figure:: /images/grease-pencil_properties_layers_panel.png
   :align: right

   Grease Pencil Layers panel.

Grease Pencil objects can be organized into a tree known as layers for grouping and arranging strokes.

Any stroke can only belong to a single 2D layer.
There is always only one active layer in the list (the selected one).
When you draw, the new strokes are added to the active layer.
By default the view order of the layers in the viewport is top to bottom.

Every layer correspond to a channel in the Dope Sheet editor (in Grease Pencil mode).
See :doc:`Dope Sheet </editors/dope_sheet/modes/grease_pencil>` for more information.

Layers can also be used together with Modifiers to only affects part of your drawing.
See :doc:`Modifiers </grease_pencil/modifiers/introduction>` for more information.

In Grease Pencil there are no special mask layers, any layer can act as a mask for other layers.
The mask system is flexible enough to allow top-bottom and bottom-top masking.

Layers used as mask can use all the blend modes and different opacity values like any other layer.

.. note::

   If you want to make a full transparent masking
   you will have to set the mask layer(s) opacity to 0.

By activating the mask toggle (mask icon) next to the layer name or
using the checkbox on the masks panel header
the layer becomes prepared to be masked by other layer(s).

.. tip::

   Sometimes the layers you are not working on can be a distraction.
   Activate *Fade Inactive Layers* in overlays to control the opacity of the non-active layers.
   See :doc:`Overlays </editors/3dview/display/overlays>` for more information.

Layers List
   :ref:`List view <ui-list-view>` of all layers for the Grease Pencil object.

   Next to the layer name there are four icons buttons that control common properties of the layer:

   Use Mask (mask icon)
      Toggle the affect of :ref:`Masks <bpy.types.GreasePencilLayer.use_masks>` on the layer.

   .. _bpy.types.GreasePencilLayer.use_onion_skinning:

   Onion Skinning (onion skin icon)
      Toggle using the layer for :doc:`Onion Skinning </grease_pencil/properties/onion_skinning>`.

   .. _bpy.types.GreasePencilLayer.hide:

   Hide (eye icon)
      Toggle layer visibility in the viewport and in render.

   .. _bpy.types.GreasePencilLayer.lock:

   Lock (padlock icon)
      Toggle layer from being editable.

Layer Specials
   Operators for working with layers.

   .. _bpy.ops.grease_pencil.layer_duplicate:

   Duplicate
      Makes an exact copy of the selected layer appending a number to differentiate its name.
   Duplicate Empty Keyframes
      Makes a copy of the selected layer but with empty keyframes.
      Useful to easily have empty keyframes preset to work on the cleanup or filling process.

   .. _bpy.ops.grease_pencil.layer_reveal:

   Show All
      Turns on the visibility of every layer in the list.
   Hide Others
      Turns off the visibility of every layer in the list except the active one.

   .. _bpy.ops.grease_pencil.layer_lock_all:

   Lock All
      Locks edition of all the layers in the list.
   Unlock All
      Unlocks edition of all the layers in the list.

   .. _bpy.types.GreasePencilv3.use_autolock_layers:

   Autolock Inactive Layer
      Locks automatically the edition of every layer in the list except the active one.
      This way you avoid to make unwanted changes in other layers without the need to lock them every time.

   .. _bpy.types.GreasePencilLayer.use_locked_material:

   Use Locked Materials Editing
      Avoids editing locked materials in the layer. When disabled,
      any material can be edited even if they are locked in the material list.

   .. _bpy.ops.grease_pencil.layer_merge:

   Merge Down
      Combine the selected layer with the layer below, the new layer keeps the name of the lower layer.
   Merge Group
       Combine layers in the active group into a single layer.
   Merge All
      Combine all layers into the active layer.

   Copy Layer to Selected
      Copy the active layer to the selected Grease Pencil object.

   Copy All Layers to Selected
      Copy all layers to the selected Grease Pencil object.

.. .. _bpy.ops.gpencil.layer_isolate:

.. Visibility (screen icon)
..    Toggle whether the active layer is the only one that can be edited and is visible.

.. Isolate Lock (padlock icon)
..    Toggle whether the active layer is the only one that can be edited.

Below the layers list there are additional settings:

.. _bpy.types.GreasePencilLayer.blend_mode:

Blend Mode
   The layer blending operation to perform. See :term:`Color Blend Modes`.

.. _bpy.types.GreasePencilLayer.opacity:

Opacity
   Used to set the opacity of the layer.

.. _bpy.types.GreasePencilLayer.use_lights:

Lights
   When enabled, the layer is affected by lights.


.. _bpy.types.GreasePencilLayer.use_masks:

Masks
=====

.. figure:: /images/grease-pencil_properties_masks_panel.png
   :align: right

   Masks list view.

The layer/s that will act as mask of the current layer could be added
to the Mask :ref:`list view <ui-list-view>`.

In the Masks list next to the layers name there are two icons buttons that control
common properties of the layer mask:

Invert (mask icon)
   Inverts the mask.

Viewport/Render Visibility (eye icon)
   Toggle layer visibility in the viewport and in render.



.. list-table:: Mask (green circle) samples.

   * - .. figure:: /images/grease-pencil_properties_masks_example-01.png
          :width: 200px

          Original image (Blend: Regular, Opacity: 1).

     - .. figure:: /images/grease-pencil_properties_masks_example-02.png
          :width: 200px

          Blend: Hard Light, Opacity: 1.

     - .. figure:: /images/grease-pencil_properties_masks_example-03.png
          :width: 200px

          Blend: Regular, Opacity: 1.


.. _bpy.types.GreasePencilLayer.location:
.. _bpy.types.GreasePencilLayer.rotation:
.. _bpy.types.GreasePencilLayer.scale:

Transform
=========

Allows per-layer location, rotation and scale transformations.


Adjustments
===========

.. figure:: /images/grease-pencil_properties_layers_adjustment.png
   :align: right

   Layers adjustment panel.

.. _bpy.types.GreasePencilLayer.radius_offset:

Tint Color
   Color that tint any material colors used in the layer.

.. _bpy.types.GreasePencilLayer.tint_factor:

Factor
   Controls the amount of tint color to apply.

.. _bpy.types.GreasePencilLayer.radius_offset:

Stroke Thickness
   Thickness value that override the strokes thickness in the layer.


Relations
=========

.. _bpy.types.GreasePencilLayer.parent:

Parent
   Select a Parent object to manipulate the layer.
   The layer will inherit the transformations of the parent,
   this is especially useful when rigging for cut-out animation.

.. _bpy.types.GreasePencilLayer.pass_index:

Pass Index
   The layer index number can be used with some modifiers to restrict changes to only certain areas.

   See :doc:`Modifiers </grease_pencil/modifiers/introduction>` for more information.

.. _bpy.types.GreasePencilLayer.viewlayer_render:

View Layer
   Defines the View Layer to use for the Grease Pencil layer.
   If empty, the layer will be included in all View Layers.
   This is useful to separate drawings parts for :doc:`compositing </compositing/introduction>`.

.. _bpy.types.GreasePencilLayer.use_viewlayer_masks:

Use Masks in Render
   If disabled, no masks on the layer are included in the view layer render.


.. Display
.. =======

.. Custom Channel Color
..    Sets the color to use in the channel region of the :doc:`Dope Sheet </editors/dope_sheet/modes/grease_pencil>`.

.. Show Only On Keyframed
..    Makes the layer visible in the viewport only if it has a keyframe in the actual frame.
..    This helps for example when you are in the inking process using the *Fill* tool and want to only see
..    the strokes that are in the actual frame to avoid fill in unwanted regions.
