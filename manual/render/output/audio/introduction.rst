.. _bpy.ops.sound.mixdown:

************
Introduction
************

Audio can be rendered from the :ref:`topbar-render`.


Options
=======

Relative Path
   Select the file path relative to the blend-file.

Accuracy
   Sample accuracy, important for animation data (the lower the value, the more accurate).

Container
   See :doc:`here </files/media/video_formats>`.

Channels
   Sets the audio channel count.

Format
   Some *Audio Containers* also have option to choose a codec.
   For more information see :doc:`here </files/media/video_formats>`.

Sample Rate
   Sets the audio `sampling rate <https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Sampling_rate>`__.

Split Channels
   Each audio channel will be rendered into a separate file.

.. seealso::

   - See :ref:`Scene Audio <data-scenes-audio>` settings.
   - See :ref:`Audio Output <render-output-video-encoding-audio>` settings.
   - See :ref:`Audio Preferences <prefs-system-sound>`.
