
*******
Editing
*******

Transform
=========

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Key --> Transform`

An F-Curve can be edited by transforming the locations of the keyframes.

Move, Rotate, Scale
   Like other elements in Blender, keyframes can be
   moved, rotated, or scaled as described in
   :doc:`Basic Transformations </scene_layout/object/editing/transform/introduction>`.
Extend
   Moves keyframes relative to the current frame.
   If the mouse is to the left of the Playhead,
   this operator only affects the selected keyframes that are to the left of the Playhead.
   On the contrary, if the mouse is to the right of the Playhead,
   this operator only affects the selected keyframes that are to the right of the Playhead.

.. tip::

   For precise control of the keyframe position and value,
   you can set values in the *Active Keyframe* of the Sidebar region.


.. _bpy.ops.graph.snap:

Snap
====

.. reference::

   :Menu:      :menuselection:`Key --> Snap`
   :Shortcut:  :kbd:`Shift-S`

Keyframes can be snapped to different properties by using the *Snap Keys* tool.

Selection to Current Frame
   Snap the selected keyframes to the current frame.
Selection to Cursor Value
   Snap the selected keyframes to the *2D Cursor*.
Selection to Nearest Frame
   Snap the selected keyframes to their nearest frame individually.
Selection to Nearest Second
   Snap the selected keyframes to their nearest second individually, based on the *FPS* of the scene.
Selection to Nearest Marker
   Snap the selected keyframes to their nearest marker individually.
Flatten Handles
   Flatten the *Bézier* handles for the selected keyframes.

   .. list-table:: Flatten Handles snapping example.

      * - .. figure:: /images/editors_graph-editor_fcurves_editing_flatten-handles-1.png

             Before Flatten Handles.

        - .. figure:: /images/editors_graph-editor_fcurves_editing_flatten-handles-2.png

             After Flatten Handles.

.. _bpy.ops.graph.equalize_handles:

Equalize Handles
   Ensure selected keyframes' handles have equal length.

   Side
      Side of the keyframes' Bézier handles to affect

      :Left: Equalize selected keyframes' left handles.
      :Right: Equalize selected keyframes' right handles.
      :Both: Equalize both of a keyframe's handles.
   Handle Length
      Length to make selected keyframes' Bézier handles.
   Flatten
      Make the values of the selected keyframes' handles the same as their respective keyframes.

Cursor to Selected :kbd:`Ctrl-G`
   Places the cursor at the midpoint between selected keyframes.

.. _bpy.ops.graph.snap_cursor_value:

Cursor Value to Selection
   Places the cursor value on the average value of selected keyframes.


.. _bpy.ops.graph.mirror:

Mirror
======

.. reference::

   :Menu:      :menuselection:`Key --> Mirror`
   :Shortcut:  :kbd:`Ctrl-M`

Selected keyframes can be mirrored over different properties using the *Mirror Keys* tool.

By Times over Current Frame
   Mirror horizontally over the current frame.
By Values over Cursor Value
   Mirror vertically over the 2D cursor.
By Times over Time 0
   Mirror horizontally over frame 0.
By Values over Value 0
   Mirror vertically over value 0.
By Times over First Selected Marker
   Mirror horizontally over the first selected marker.


.. _bpy.ops.graph.frame_jump:

Jump to Selected
================

.. reference::

   :Menu:      :menuselection:`Key --> Jump to Selected`
   :Shortcut:  :kbd:`Ctrl-G`

Places the 2D cursor at the center of the selected keyframes.


.. _bpy.ops.graph.keyframe_insert:

Insert
======

.. reference::

   :Menu:      :menuselection:`Key --> Insert`
   :Shortcut:  :kbd:`I`

Inserts a keyframe to the active F-Curve at the mouse position.
The newly added keyframes will be selected, making it easier to quickly tweak the newly added keyframes.
All previously selected keyframes are kept selected by using :kbd:`I`.

Type
   :All Channels:
      Insert a keyframe on all visible and editable F-Curves using each curve's current value.
   :Only Selected Channels:
      Insert a keyframe on selected F-Curves using each curve's current value.
   :Only Active F-Curve:
      Insert a keyframe on the active F-Curve using the curve's current value.
   :Active Channels at Cursor:
      Insert a keyframe for the active F-Curve at the cursor point.
   :Selected Channels at Cursor:
      Insert a keyframe for selected F-Curves at the cursor point.


.. _bpy.ops.graph.copy:
.. _bpy.ops.graph.paste:

Copy/Paste
==========

.. admonition:: Reference

   :Menu:      :menuselection:`Key --> Copy`, :menuselection:`Key --> Paste`
   :Shortcut:  :kbd:`Ctrl-C`, :kbd:`Ctrl-V`

Use :kbd:`Ctrl-C` to copy selected keyframes and :kbd:`Ctrl-V` to paste the previously copied keyframes.
During the paste action, the :ref:`bpy.ops.screen.redo_last` panel provides some options in
how the paste is applied.

Frame Offset
   :No Offset:
      Pastes the keyframes in the location they were copied from.
   :Frame Relative:
      Pastes the keyframe relative to the current frame based on the locations of
      the keyframes relative to the current frame when they were copied.
   :Frame Start:
      Pastes the keyframes with the first keyframe of the copied set placed at the current frame.
   :Frame End:
      Pastes the keyframes with the last keyframe of the copied set placed at the current frame.

Value Offset
   :No Offset:
      Pastes the keyframes with the value they were copied from.
   :Cursor Value:
      Paste the keyframes at the 2D cursor as a starting point.
   :Current Frame Value:
      Paste keyframes relative to the value of the curve under the cursor.
   :Right Key:
      Paste keyframes such that the last frame matches the key value right of the cursor.
   :Left Key:
      Paste keyframes such that the first key matches the key value left of the cursor.

Type
   :Mix:
      Integrates the pasted keyframes in with existing keyframes only overwriting keyframes that share a frame.
   :Overwrite All:
      Removes all previous keyframes and replaces them with the pasted keyframes.
   :Overwrite Range:
      Overwrite keys in pasted range.
   :Overwrite Entire Range:
      Overwrite keys in pasted range, using the range of all copied keys.
Flipped
   Paste keyframes from mirrored bones if they exist.


.. _bpy.ops.graph.duplicate_move:

Duplicate
=========

.. reference::

   :Menu:      :menuselection:`Key --> Duplicate`
   :Shortcut:  :kbd:`Shift-D`

Duplicates the selected keyframes. You can reposition them by moving the mouse.


.. _bpy.ops.graph.delete:

Delete
======

.. reference::

   :Menu:      :menuselection:`Key --> Delete`
   :Shortcut:  :kbd:`X`, :kbd:`Delete`

Pressing :kbd:`X` or :kbd:`Delete` opens a pop-up menu from where you can delete the selected keyframes.


.. _bpy.ops.graph.handle_type:

Handle Type
===========

.. reference::

   :Menu:      :menuselection:`Key --> Handle Type`
   :Shortcut:  :kbd:`V`

Sets the :ref:`handle type <editors-graph-fcurves-settings-handles>` of the selected keyframes.


.. _bpy.ops.graph.interpolation_type:

Interpolation Mode
==================

.. reference::

   :Menu:      :menuselection:`Key --> Interpolation Mode`
   :Shortcut:  :kbd:`T`

Sets the :ref:`interpolation mode <editors-graph-fcurves-settings-interpolation>` between the selected keyframes.


.. _bpy.ops.graph.easing_type:

Easing Type
===========

.. reference::

   :Menu:      :menuselection:`Key --> Easing Type`
   :Shortcut:  :kbd:`Ctrl-E`

Sets the :ref:`easing mode <editors-graph-fcurves-settings-easing>` of the selected keyframes.


Density
=======

.. _bpy.ops.graph.decimate:

Decimate
--------

.. reference::

   :Menu:      :menuselection:`Key --> Density --> Decimate (Ratio)`
   :Menu:      :menuselection:`Key --> Density --> Decimate (Allowed Change)`

The *Decimate* tool simplifies an F-Curve by removing
keyframes that influence the curve shape the least.

Mode
   Controls which method is used pick the number of keyframes to use.

   :Ratio:
      Deletes a defined percentage of keyframes,
      the amount of keyframes to delete is define by the *Remove* property.
   :Error Margin:
      Deletes keyframes which only allowing the F-Curve to change by a defined amount.
      The amount of change is controlled by the *Max Error Margin*
      which controls how much the new decimated curve is allowed to deviate from the original.


.. _bpy.ops.graph.bake_keys:

Bake Keyframes
--------------

.. reference::

   :Menu:      :menuselection:`Key --> Density --> Bake Keyframes`
   :Shortcut:  :kbd:`Shift-Alt-O`

Baking a set of keyframes replaces interpolated values with a new keyframe for each frame.

.. list-table::

   * - .. figure:: /images/editors_graph-editor_fcurves_editing_sample.png

          F-Curve before baking.

     - .. figure:: /images/editors_graph-editor_fcurves_editing_sample2.png

          F-Curve after baking.


.. _bpy.ops.graph.clean:

Clean Keyframes
---------------

.. reference::

   :Menu:      :menuselection:`Key --> Density --> Clean Keyframes`
   :Shortcut:  :kbd:`X`

Removes redundant keys within the selection of keyframes.
*Clean Keyframes* resets the keyframe tangents on selected keyframes
to their auto-clamped shape, if they have been modified.

.. tip::

   The modified curve left after the *Clean* tool is run is not the same as the original,
   so this tool is better used before doing custom editing of F-Curves and after initial keyframe insertion,
   to get rid of any unwanted keyframes inserted while doing mass keyframe insertion
   (by selecting all bones and pressing :kbd:`I` for instance).

Channels
   Operate on selected channels and cleans them regardless of keyframe selection.
   Deletes the channel itself if it is only left with
   a single keyframe containing the default property value and
   it's not being used by any generative F-Curve modifiers or drivers.


.. list-table::

   * - .. figure:: /images/editors_graph-editor_fcurves_editing_clean1.png

          F-Curve before cleaning.

     - .. figure:: /images/editors_graph-editor_fcurves_editing_clean2.png

          F-Curve after cleaning.


Blend
=====

.. reference::

   :Menu:      :menuselection:`Key --> Blend`
   :Shortcut:  :kbd:`Alt-D`

.. _bpy.ops.graph.breakdown:

Breakdown
---------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Breakdown`

Moves the selected keyframes to an in between position relative to the adjacent keyframes.
To use this operator, drag the mouse left or right to adjust the operator's *Factor* property.

Factor
   The amount to favor either the left or the right key. Values less than 0.5 favor the left keyframe,
   values greater than 0.5 favor the right keyframe, a value of 0.5 results in no change.


.. _bpy.ops.graph.blend_to_neighbor:

Blend to Neighbor
-----------------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Blend to Neighbor`

Transitions the current keyframe with the neighboring keyframes in the timeline.
In order for this operator to work, there must be a keyframe before and after the current frame.
To use this operator, drag the mouse left or right to adjust the operator's *Blend* property.

Blend
   The amount to favor either the left or the right key. Values less than 0.5 favor the left keyframe,
   values greater than 0.5 favor the right keyframe, a value of 0.5 results in no change.


.. _bpy.ops.graph.blend_to_default:

Blend to Default Value
----------------------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Blend to Default Value`

Transitions the current keyframe towards the property's default value.
To use this operator, drag the mouse left or right to adjust the operator's *Blend* property.

Blend
   The amount to favor either the current key or the default value.
   A value of 0 represents the current key, a value of 1 represents the default value.

.. seealso::

   The :ref:`Reset to Default <bpy.ops.ui.reset_default_button>` operator resets
   any property to its default value without the need of keyframing.


.. _bpy.ops.graph.ease:

Ease
----

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Ease`

Aligns selected keyframes to follow an S-curve between the first and last keyframe.
To use this operator, drag the mouse left or right to adjust the operator's *Curve Bend* property.
During modal operations, pressing :kbd:`Tab` will change which property the slider affects.

Curve Bend
   Changes which key the S-curve favors. At 0 the S-curve is right in the center. At either -1 or 1
   it favors one of the ends.

Sharpness
   How abruptly the S-curve changes. At 0 it will be a straight line. Higher values give a quicker change.


.. _bpy.ops.graph.blend_offset:

Blend Offset
------------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Blend Offset`

Move the selected keyframes as a block so the first/last key align with the key before/after the selection.
Does nothing when there is no key before/after the current selection.

Offset Factor
   At -1 the first key of the selection is aligned with the key just before the selection.
   At 1 the last key is aligned with the key after the selection.


.. _bpy.ops.graph.blend_to_ease:

Blend to Ease
-------------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Blend to Ease`

Blend the selected keys from their current position to either an ease in or an ease out curve.

Blend
   At -1 the keys will start slowly and then accelerate to the end.
   At 1 the keys will rise quickly and then taper off.


.. _bpy.ops.graph.match_slope:

Match Slope
-----------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Match Slope`

Blend the selected keys to a straight line formed by the two keys just outside the current selection.
The factor determines if the two keys left or right of the selection are used. If there are not
two keys in the given direction the operator will throw a warning and not change the keys.

Factor
   Determines which slope to blend towards. At -1 will blend to the left slope, at 1 to the right.


.. _bpy.ops.graph.shear:

Shear Keys
----------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Shear Keys`

Shear the keys based on the position of the keyframe selection ends.
Pressing :kbd:`D` while the modal operator is active will toggle the anchor key
between the start and end of the selection.

Shear Factor
   How much to shear and if it shears up or down. Negative values shear down, positive shear up.
Direction
   `From Left` or `From Right` determine the anchor key from which to shear.


.. _bpy.ops.graph.scale_average:

Scale Average
-------------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Scale Average`

Scale the selected key segments to their average value. This differs from the regular scaling by being per segment.
That means selected keyframes on two different F-Curves will scale to different points.

Factor
   The scale factor applied to the F-Curve segments.


.. _bpy.ops.graph.scale_from_neighbor:

Scale from Neighbor
-------------------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Scale from Neighbor`

Scale the selected key segments from either their left or right neighbor key. Pressing :kbd:`D` while in the modal
operator switches the reference key from one end to the other.

Factor
   The scale factor applied to the F-Curve segments.
Reference Key
   `From Left` or `From Right` determine from which end of the segment to scale.


.. _bpy.ops.graph.push_pull:

Push Pull
---------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Push Pull`

Scale the keys from an imaginary line that runs from the start to the end of the selected segment.

Factor
   How far to push or pull the keys.


.. _bpy.ops.graph.time_offset:

Time Offset
-----------

.. reference::

   :Menu:      :menuselection:`Key --> Blend --> Time Offset`

This operator shifts the value of the keys in time, while keeping the actual key positions in the same place. It
supports wrapping, so when offsetting beyond the range of the F-Curve it will take values from the other end, but
offset in y-value so there is no jump. This works best with dense key data. Gaps in the keyframe data might cause data
to get lost if it is shifted into the gaps.

Frame Offset
   How far in frames to offset the animation.


Smooth
======

.. reference::

   :Menu:      :menuselection:`Key --> Smooth`
   :Shortcut:  :kbd:`Alt-S`


.. _bpy.ops.graph.smooth:

Smooth (Legacy)
---------------

.. reference::

   :Menu:      :menuselection:`Key --> Smooth --> Smooth (Legacy)`
   :Shortcut:  :kbd:`Alt-O`

There is also an option to smooth the selected curves, but beware: its algorithm seems to be
to divide by two the distance between each keyframe and the average linear value of the curve,
without any setting, which gives quite a strong smoothing! Note that the first and last keys
seem to be never modified by this tool.

.. list-table::

   * - .. figure:: /images/editors_graph-editor_fcurves_editing_clean1.png

          F-Curve before smoothing.

     - .. figure:: /images/editors_graph-editor_fcurves_editing_smooth.png

          F-Curve after smoothing.


.. _bpy.ops.graph.gaussian_smooth:

Smooth (Gaussian)
-----------------

.. reference::

   :Menu:      :menuselection:`Key --> Smooth --> Smooth (Gaussian)`

Smooths the selected keyframes using a Gaussian kernel. It can handle gaps in the keyframe data.
The operator is modal with a blend factor, making it possible to tweak the strength of the filter.

Factor
   A blend factor from original to filtered curve.

Sigma
   The shape of the gaussian distribution. Lower values mean a sharper curve, giving keys that are close to each
   other more weight. A high value behaves like a simple average filter.

Filter Width
   A wider filter looks at more keyframes, producing a smoother result.
   At a size of 1 the filter only looks at the keyframes to the immediate left and right for a weighted average.

.. figure:: /images/editors_graph-editor_gaussian_smooth.jpg

   F-Curve after applying the Gaussian Smooth with the original curve overlayed.


Butterworth Smooth
------------------

.. reference::

   :Menu:      :menuselection:`Key --> Smooth --> Butterworth Smooth`

Smooth the selected keyframes using a Butterworth filter. This filter is ideal for
smoothing large amounts of data because it preserves the peaks of the animation.
The downside is that it can introduce a ripple effect when the key values change rapidly.

Frequency Cutoff
   The lower the value the smoother the curve. There is an implicit maximum at which
   the value no longer changes the curve which is at half the sample rate. The sample
   rate in this case is the scene frame rate multiplied by the `Samples per Frame` of this operator.
Filter order
   Higher values mean the frequency cutoff is steeper.
Samples per Frame
   Before the filter is applied, the curve is resampled at this interval to avoid errors when there
   are uneven spaces between frames. If keys are on subframes, e.g. a 60fps file in a 30fps scene,
   increase this value to 2.
Blend
   A 0-1 value to blend from original curve to filtered curve.
Blend In/Out
   The number of frames at the start and end for which to blend between the filtered and unfiltered curve.
   This can help reducing jumps in the animation at the selection border. At value 1 it only locks the first and
   last frame of the selection to the original position.
