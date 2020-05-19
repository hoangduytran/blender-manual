
*******
Sidebar
*******

The Sidebar can be shown by pressing the hotkey :kbd:`N` or by using :menuselection:'View --> Sidebar'.
It is located at the right-hand side of the Compositor window.


Item
====

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Sidebar region --> Item`

.. figure:: /images/compositing_properties_item.png
   :width: 200px
   :align: right

   Item tab: Render Layers node.


Node
----

This panel is used to change identifiable infomation about a node or node group.
It is good practice to label and color group nodes.

Name
   The nodes unique identifing name, used when linking node groups.
Label
   An optional label that replaces the node type name found at the top of the node.
Color
   Sets the background color of the node.


Properties
----------

The properties that are shown depend on the type of node selected,
e.g. a Mix node has different properties than a Mask node.


Tool
====

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Sidebar region --> Tool`


Active Tool
-----------

.. figure:: /images/compositing_properties_tool.png
   :width: 200px
   :align: right

   Active Tool panel.

The exact info in this panel changes with the selected tool.

.. container:: lead

   .. clear


View
====

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Sidebar region --> View`


Backdrop
--------

.. figure:: /images/compositing_properties_view.png
   :width: 200px
   :align: right

   Backdrop Panel.

The backdrop is a preview of the output of a node, For example,
:kbd:`Ctrl-Shift-LMB` on an Image node, will show the preview of the image.
:kbd:`Ctrl-Shift-LMB` on a Mix node, will show the result of the mixing.
You can toggle the backdrop by clicking on the *Backdrop* button in the Header
or by clicking the checkbox next to *Backdrop* in the View panel.

Channels
   The channel of color to display the backdrop image as.

   Color and Alpha
      Displays the image with all color and transperency channels.
   Color
      Displays only red, green, and blue components of an image and transparent regions of the image shown in black.
   Alpha
      The transparent area is shown in black and the pixels with color info are displayed in white.
   Red, Green, Blue
      Selcting a single color channel will display a gray scale image.
      The intensity of the selected color will be shown as a shade of gray.
      Darker gray signifies less color available of the one that is selected.
      For example, if the *Red* channel is selected a red rose against a blue sky
      will be shown as a white outline of the rose against a black sky.
Zoom
   Sets how big the backdrop image is. The value cannot be smaller than 0.01.
   The max value has no limit.
Offset
   Change the screen space position of the backdrop.
Move :kbd:`Alt-MMB`
   Changes the positon of the backdrop on the Compostitor backgound grid.
Fit
   Automatically scales the backdrop to fit the size of the compositor editor.
Reset Backdrop
   Switches back to the default values of Zoom (1) and Offset (0).


Annotations
-----------

You can select the Annotate tool in the Toolbar (press :kbd:`T` to show the toolbar)
to make some annotations in the Compositor window.
See :doc:`Annotate Tool </interface/annotate_tool>` for more info.


Options
=======

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Sidebar region --> Options`


Performance
-----------

.. figure:: /images/compositing_properties_options.png
   :width: 200px
   :align: right

   Performance panel.

This panel help you to tweak the performance of the Compositor.

Render
   Sets the quality when doing the final render. Can be high, medium or low.
Edit
   Sets the quality when making edits. Can be high, medium or low.
Chunk Size
   Max size of a tile (smaller values give a better distribution of multiple threads, but more overhead).
OpenCL
   This allows the use of an OpenCL platform to aid in rendering.
   Generally, this should be enabled unless your hardware does not have good OpenCL support.
Buffer Groups
   Enables buffering of group nodes to increase the speed at the cost of more memory.
Two Pass
   Use two pass execution during editing: the first pass calculates fast nodes, the second pass calculates all nodes.
Viewer Border
   This allows to set an area of interest for the backdrop.
   Press :kbd:`Ctrl-B` and select a rectangular area in the preview.
   This area will become your next preview in the backdrop.
   :kbd:`Ctrl-Alt-B` discards the region back to a full preview.
   This is only a preview option, final compositing during a render ignores this region.
Auto Render
   Re-render and composite changed layer when edits to the 3D scene are made.
