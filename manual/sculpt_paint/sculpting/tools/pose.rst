.. _bpy.types.Brush.pose_deform_type:
.. _bpy.types.Brush.pose_origin_type:
.. _bpy.types.Brush.pose_offset:
.. _bpy.types.Brush.pose_smooth_iterations:
.. _bpy.types.Brush.pose_ik_segments:
.. _bpy.types.Brush.use_pose_ik_anchored:
.. _bpy.types.Brush.use_connected_only:
.. _bpy.types.Brush.disconnected_distance_max:

****
Pose
****

.. admonition:: Reference
   :class: refbox

   :Mode:      Sculpt Mode
   :Tool:      :menuselection:`Toolbar --> Pose`

This brush is used to pose a model simulating an armature-like deformations.
Several different deformation modes can be used to preform
IK deformations or altering and moving the proportions of the mesh.
The falloff of the deformation across multiple segments is controlled by the brush falloff curve.

Deformation
   Deformation type that is used by the brush.

   Rotate/Twist
      Rotates segments around a pivot point that is calculated automatically based
      on the radius of the brush and the topology of the model.
      When pressing :kbd:`Ctrl`, the brush applies a twist rotation
      to the posing segments instead of using the rotation or an IK deformation.
   Scale/Translate
      Alters the proportions of the of the mesh, using the segment's origin as a pivot.
      While holding :kbd:`Ctrl` the brush moves the entire segment.
   Squash/Stretch
      Works similar to *Scale/Translate* however, it applies different
      scale values along different axes to achieve the stretching affect.
      The pivot point for this mode is calculated by using the local space aligned to the segment.

Rotation Origins
   Method to set the rotation origins for the segments of the brush.

   Topology
      Sets the rotation origin automatically using the topology and shape of the mesh as a guide.
   Face Sets
      Creates a pose segment per :ref:`Face Set <sculpting-editing-facesets>`, starting from the active face set.
   Face Sets FK
      Simulates an :term:`Forward Kinematics` deformation using the :ref:`Face Set <sculpting-editing-facesets>`
      under the cursor as control.

Pose Origin Offset
   Offset of the pose origin in relation to the brush radius.
   This is useful to manipulate areas with a lot of complex shapes like fingers.

Smooth Iterations
   Controls the smoothness of the falloff of the deformation.

Pose IK Segments
   Controls how many :ref:`IK bones <bone-constraints-inverse-kinematics>`
   are going to be created for posing.

Keep Anchor Point
   Keeps the position of the last segment in the IK chain fixed.

Connected Only
   Causes the brush to only affect topologically connected elements.
   Disabling this can have an impact on performance; when disabled,
   keeping the *Max Element Distance* as low as possible will help counteract the performance impact.

Max Element Distance
   Maximum distance to search for disconnected loose parts in the mesh.
