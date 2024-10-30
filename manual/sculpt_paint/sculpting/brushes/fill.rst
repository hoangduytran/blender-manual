
****
Fill
****

.. reference::

   :Mode:      Sculpt Mode
   :Brush:     :menuselection:`Sidebar --> Tool --> Brush Settings --> Advanced --> Brush Type`

Similar to the :doc:`Flatten </sculpt_paint/sculpting/brushes/flatten>` brush,
but only pushes surfaces upwards to the medium height.

Although :kbd:`Ctrl` can be held to invert the effect to a Scrape brush,
if *Invert to Scrape* is enabled.
When disabled, the inverted direction will push surfaces away.


Brush Settings
==============

General
-------

.. note::

   More info at :ref:`sculpt-tool-settings-brush-settings-general` brush settings
   and on :ref:`sculpt-tool-settings-brush-settings-advanced` brush settings.


Unique
------

.. _bpy.types.Brush.invert_to_scrape_fill:

Invert to Scrape
   When enabled, holding :kbd:`Ctrl` while sculpting
   changes the brush behavior to be the same as the *Scrape* brush.
   When disabled, holding :kbd:`Ctrl` while sculpting,
   will push vertices below the cursor downward.
