.. _bpy.ops.object.vertex_parent_set:

******************
Make Vertex Parent
******************

.. reference::

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Vertex --> Make Vertex Parent`
   :Shortcut:  :kbd:`Ctrl-P`

Parents the selected objects (except the active one) to the selected vertices.
If one vertex is selected, the objects will follow its location.
If three vertices are selected, the objects will follow the centerpoint of the resulting
triangle and rotate together with that triangle.

While in Edit Mode, other objects can be selected by clicking them in the
:doc:`Outliner </editors/outliner/introduction>` or pressing :kbd:`Ctrl-LMB` on them
in the 3D Viewport.

.. seealso::

   - :doc:`Parenting overview </scene_layout/object/editing/parent>`
   - :doc:`/modeling/meshes/editing/vertex/hooks` -- for the opposite operation, "parenting" vertices to objects.
