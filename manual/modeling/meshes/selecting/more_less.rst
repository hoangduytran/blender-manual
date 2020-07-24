
****************
Select More/Less
****************

.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Select More/Less --> More`
   :Hotkey:    :kbd:`Ctrl-NumpadPlus`
   :Menu:      :menuselection:`Select --> Select More/Less --> Less`
   :Hotkey:    :kbd:`Ctrl-NumpadMinus`

With at least one vertex, edge, or face selected, *Select More/Less* can be used to grow or shrink the selection. However, if there is only one selection in any given mode, the :kbd:`Ctrl-NumpadMinus` action will deselect it.

Face Step
   With *Face Step* on, each use of :kbd:`Ctrl-NumpadPlus` or :kbd:`Ctrl-NumpadMinus`` will affect the size of the selection on a face by face bases. With this off, it will be based on either vertecies or edges depending on which :doc:`Selection Mode </modeling/meshes/selecting/introduction>` is active.
      
.. figure:: /images/modeling_meshes_selecting_more-less.png
   
   (from left to right) Initial Selection, :kbd:`Ctrl-NumpadPlus` w/o Face Step, with Face Step, :kbd:`Ctrl-NumpadPlus` in *Edge Selection Mode*.
   
More
   Enlarge the selection from the center of the intial selection.
   
Less
   Reduce the selection towards the center of the intial selection.


Select Next/Previous Active
===========================
   
.. admonition:: Reference
   :class: refbox

   :Mode:      Edit Mode
   :Menu:      :menuselection:`Select --> Select More/Less --> Next Active`
   :Hotkey:    :kbd:`Shift-Ctrl-NumpadPlus`
   :Menu:      :menuselection:`Select --> Select More/Less --> Previous Active`
   :Hotkey:    :kbd:`Shift-Ctrl-NumpadMinus`

Next Active
   This uses selection history to select the next vertex/edge/face based on surrounding topology. Meaning, it will predict the next selection based on the previous two selections
   
.. list-table:: Depending on which *Selection Mode* is being used, :kbd:`Shift-Ctrl-NumpadPlus` will perform this action.

   * - .. figure:: /images/modeling_meshes_selecting_select-active-1.png
		  :width: 200px
		  
		  Initial Selection.
       
     - .. figure:: /images/modeling_meshes_selecting_select-active-2.png
		  :width: 200px
          
		  Using Next Active Once.
       
     - .. figure:: /images/modeling_meshes_selecting_select-active-3.png
		  :width: 200px
          
		  Using Next Active Twice.

Previous Active
   Only the last selected element will be removed.
   