
*****
Cache
*****

The Cache is used to save preview frames in memory,
so they can later be displayed much faster than if they were rendered from scratch.
Cache capacity can be set in the :doc:`System tab </editors/preferences/system>` of the Preferences.

In order for this tab to be visible,
enable :ref:`Developer Extras <bpy.types.PreferencesView.show_developer_ui>`.

.. seealso::

   Which frames are cached can be visualized by enabling :ref:`Show Cache <bpy.types.SequenceEditor.show_cache>`.


Cache Settings
==============

.. reference::

   :Panel:     :menuselection:`Sidebar --> Cache --> Cache Settings`

In this panel, you can select the preview rendering stages at which strip images should be cached.
These settings apply to all strips.

Cache
   Raw
      Cache raw images right after they're read from the drive, for faster tweaking of strip parameters
      at the cost of memory usage.
   Pre-processed
      Cache strip images after applying cropping, scaling, saturation and so on,
      for faster tweaking of effects at the cost of memory usage.
   Composite
      Cache strip images after blending with lower channels and applying effects,
      for faster tweaking of stacked strips at the cost of memory usage.
   Final
      Cache the final rendered frame.


Strip Cache
===========

.. reference::

   :Panel:     :menuselection:`Sidebar --> Cache --> Cache Settings`

This panel sets the types of images that will be cached for the active strip.
When enabled, these properties override the above `Cache Settings`_.

Cache
   Raw
      Cache raw images read from drive, for faster tweaking of strip parameters at the cost of memory usage.
   Preprocessed
      Cache preprocessed images, for faster tweaking of effects at the cost of memory usage.
   Composite
      Cache intermediate composited images, for faster tweaking of stacked strips at the cost of memory usage.
