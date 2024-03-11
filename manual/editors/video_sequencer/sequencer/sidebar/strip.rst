
*****
Strip
*****

Header
======

Type
   Strip type, represented by an icon.

.. _bpy.types.Sequence.name:

Name
   A text field to adjust the name of the strip, which is shown on the strip in the timeline.

   .. _bpy.ops.sequencer.strip_color_tag_set:

   Color Tag
      The color of the strip in the timeline.
      By default, strips are given a :ref:`Default Color <sequencer-strip-colors>` based on the type of strip.
      The color tag can change the color to an alternative predefined color.

      This can be useful to help organize your sequence by for example,
      giving a special color to all graphic overlays and a different color for footage.

Mute
   Toggles the strip from producing an output.


Compositing
===========

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Compositing`

Blend
   The method for blending the current strip with strips in lower channels.
   See :term:`Blend Modes` for more information.
Opacity
   The transparency (:term:`alpha <Alpha Channel>`) of the strip.

   When this property is animated, the opacity is drawn as an overlay on the strip.
   The overlay will look like a dark section that follows the animation curve.
   This can be hidden by disabling the :ref:`F-Curves <bpy.types.SequencerTimelineOverlay.show_fcurves>`.


.. _bpy.types.SequenceTransform:

Transform
=========

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Transform`

.. _bpy.types.SequenceTransform.filter:

Filter
   The technique used to estimate the values of pixels at non-integer coordinates within the image.

   :Auto:
      Automatically choose filter based on scaling factor.

      - No scale, no rotation, integer positions: *Nearest*
      - Scaling up by more than 2x: *Cubic Mitchell*
      - Scaling down by more than 2x: *Box*
      - Otherwise: Bilinear
   :Nearest: No interpolation; uses nearest neighboring pixel (fastest).
   :Bilinear: Interpolate between 2×2 samples.
   :Cubic Mitchell: Cubic Mitchell filter on 4×4 samples.
   :Cubic B-Spline: Cubic B-Spline filter (blurry but no ringing) on 4×4 samples.
   :Box: Averages source image samples that fall under destination pixel.

.. _bpy.types.SequenceTransform.offset:

Position X, Y
   Used to move the frames along the X and Y axis.

.. _bpy.types.SequenceTransform.scale:

Scale X, Y
   Scale the image on the X and Y axis.

.. _bpy.types.SequenceTransform.rotation:

Rotation
   Rotates the input two-dimensionally along the Z axis.

.. _bpy.types.ImageSequence.use_flip:

Mirror
   Mirrors the image along the X axis (left to right) or the Y axis (top to bottom).


.. _bpy.types.SequenceCrop:

Crop
====

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Crop`

Used to crop the source image. Use *Top*, *Left*,
*Bottom*, and *Right* to control the number of pixels that are cropped.


Video
=====

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Video`

Strobe
   Display every nth frame.
   For example, if you set this to 10,  the strip will only display frames 1, 11, 21, 31, 41... of the source.

   It is important to realize that this property is a float value.
   This allows you to strobe effect synced exactly to a beat.

Reverse Frames
   Plays the strip backwards starting from the last frame in the sequence.


Color
=====

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Color`

Saturation
   Adjusts the vividness of colors in the image.
Multiply
   Multiplies the colors by this value. This will increase the brightness.
Multiply Alpha
   Multiply alpha along with color channels when using the *Multiply* option.
Convert to Float
   Converts input to float data.


.. _vse_sidebar_strip_sound:

Sound
=====

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Sound`

Working with sound is documented further at :ref:`bpy.types.SoundSequence`.

.. _bpy.types.SoundSequence.volume:

Volume
   Adjusts the perceived loudness or intensity of the sound

   When this property is animated, the volume is drawn as an overlay on the strip.
   The overlay will look like a dark section that follows the animation curve.
   This can be hidden by disabling the :ref:`F-Curves <bpy.types.SequencerTimelineOverlay.show_fcurves>`.
   The value is also reflected in the waveform.

.. figure:: /images/vse_setup_project_striptypes_sound-pan.png
   :align: right
   :width: 220px

.. _bpy.types.SoundSequence.pan:

Pan
   Used to pan the audio between speakers in multichannel audio.
   Only mono sources can be panned, if the source file is not mono enable *Mono* to mix the channels together.

   This value basically represents the angle at
   which it's played if you multiply the value by 90 degrees.

   For stereo output panning works from left (-1) to right (1);
   where 0 means front/center, -1 means to the left and 1 to the right.

   To address rear speakers, you can pan to those with the higher values;
   where -2 is back left, and 2 is back right.

   .. tip::

      For smooth animation you can assign values outside the soft bounds,
      since the angle wraps around over multiple rotations.

   .. note::

      The number of audio channels can be configured in the
      :ref:`Audio Output <render-output-video-encoding-audio>` settings.

.. _bpy.types.SoundSequence.show_waveform:

Display Waveform
   Display an approximate waveform of the sound file inside of the Sound strip.
   The waveform reflects strip volume and its animation using :doc:`keyframes </animation/keyframes/introduction>`.

   Clipping audio, i.e. values over 100% amplitude, will be shown in red in the waveform.

.. _bpy.types.Sound.use_mono:

Mono
   Mixdown all audio channels into a single channel.


.. _sequencer-strips-properties-time:

Time
====

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Time`

The Time panel is used to control source and timeline position of the strip.

Lock (padlock icon)
   Prevents the strip from being moved (found in the panel header).

.. _bpy.types.Sequence.show_retiming_keys:

Show Retiming Keys
   Toggle visibility and selectability of :ref:`Retiming keys <sequencer-editing-retiming>`.

.. _bpy.types.Sequence.channel:

Channel
   Changes the channel number, or row, of the strip.

.. _bpy.types.Sequence.frame_start:

Start
   Changes the starting frame number of the strip, which is the same as selecting and moving the strip.

.. _bpy.types.Sequence.frame_final_duration:

Duration
   Changes the length, in frames of the strip. This works by changing the end frame,
   which is the same as selecting and moving the strip's right handle.
End
   Specifies the ending time and ending frame number for the strip.

.. _bpy.types.Sequence.frame_offset_start:
.. _bpy.types.Sequence.frame_offset_end:

Strip Offset Start/End
   Can be used to either extend the strip beyond the end frame by repeating the last frame.
   Or it can be used to shorten the strip, as if you were cropping the end frame.
   This is the same as adjusting the strip handles.

.. _bpy.types.MovieSequence.animation_offset_start:
.. _bpy.types.MovieSequence.animation_offset_end:
.. _sequencer-duration-hard:

Hold Offset Start/End
   Offset of the uncut strip content.
Current Frame
   The frame number relative to the start of the active strip.


Source
======

.. reference::

   :Panel:     :menuselection:`Sidebar --> Strip --> Source`

The Source panel is used to control sources of the strip
such as filename and file path and various methods of interpreting these files.

Path
   The directory that contains the source file.
   When the file is moved, the path can be updated instead of recreating the strip.
File
   The file name of the source file.
   For image strips showing an image sequence, this will be different for each frame.
Change Data/Files
   Same as the *Path* and *File* fields, but this time combined to open the File Browser in order to
   find the file(s) you search. Same as :menuselection:`Strip --> Inputs --> Change Paths/Files`.

Color Space
   To specify the color space of the source file.

   The list of color spaces depends on the active :ref:`OCIO config <ocio-config>`.
   The default supported color spaces are described in detail here:
   :ref:`Default OpenColorIO Configuration <ocio-config-default-color-spaces>`
Alpha Mode
   If the source file has an Alpha (transparency) channel, you can choose:

   :term:`Straight Alpha` or :term:`Premultiplied Alpha`
Stream Index :guilabel:`Movie Strip`
   For files with several movie streams, use the stream with the given index.
Deinterlace
   Removes fields in a video file.
   For example, if it is an analog video and it has even or odd interlacing fields.

Source Information
   Displays information about the strip's media.

   Resolution
      Resolution of the active strip image output.
   FPS :guilabel:`Movie Strip`
      The frame rate encoded into the video file.
      If this value does not match the scene :ref:`Frame Rate <bpy.types.RenderSettings.fps>`
      the perceived speed of the media will be wrong unless the speed is
      :ref:`changed <video_editing-change_fps>` to account for the difference in frame rate.


Options for Sound Strips
------------------------

Sound
   :ref:`Data-block menu <ui-data-block>` to select a sound.
Path
   Path to the sound file used by this :ref:`data-block <ui-data-block>` menu.
Pack
   Pack sound into the blend-file.

.. _bpy.types.Sound.use_memory_cache:

Caching
   Sound file is decoded and loaded into the RAM.

Source Information
   Displays information about the strip's media.

   Samplerate
      The number of samples per second the audio is encoded at.
   Channels
      The number of audio channels encoded into the audio stream.
