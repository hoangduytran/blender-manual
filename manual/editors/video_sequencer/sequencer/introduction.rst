
************
Introduction
************

The Sequencer view is where all the video editing happens. It shows a stack of
:doc:`Channels </editors/video_sequencer/sequencer/channels>`,
which are similar to layers in an image editing program (higher channels are displayed
in front of lower ones). Within each channel, you can create one or more
:doc:`strips </video_editing/edit/montage/strips/introduction>`, which
contain either a segment of video content (a rendered scene, an external video file...)
or an :doc:`effect </video_editing/edit/montage/strips/effects/index>` (color blending,
blurring...).


:doc:`select </video_editing/edit/montage/selecting>` and
:doc:`modify </video_editing/edit/montage/editing>` strips.
There are also several built-in
that can be combined with other strips to change their appearance.

The Sequencer view is horizontally divided into
each channel can contain what is called a strip.
A strip can be an image, animation, or any number of effects.
Each channel is numbered consecutively on the Y axis,
starting from zero and allows up to 128 total channels.
The X axis represents time. Each channel can contain as many strips
as it needs as long as they do not overlap. If a strip needs to overlap another,
it needs to be placed on a channel above or below the other strip.
When strips are stacked, they stack from bottom to top where the lowest channel
forms the background and the highest the foreground.
