********************
System Configuration
********************

Blender Settings
================

By default, Blender integrates with automatic color management in operating
systems and saves images and videos with color space metadata. This helps
make image viewed in Blender look the same when saved and opened in other
applications on the same computer. Particularly image viewers, video players
and browsers that also use automatic color management.

Traditionally, VFX software has relied on more manual configuration. Turn
off display emulation for more manual control.

.. _bpy.types.ColorManagedDisplaySettings.emulation:

Display Emulation
-----------------

:Automatic:
   Display images consistent with most other applications, to preview images and video
   for export.

   The choice of display in Blender specifies the target display color space for
   rendered images and video files (or game assets to export). Colors will be clipped
   to the gamut and HDR range of the chosen target display.
   
   For example, if you have a P3 HDR monitor, you can preview what the image will
   look like when saved as sRGB, Display P3 or HDR.

:Off:
   Directly output image as produced by OpenColorIO. For accurate results, this requires
   the choice of display in Blender to match the system configuration and actual display
   device. A mismatch will give inaccurate results.

Emulation is not supported with older :ref:`OpenColorIO configurations <ocio-config>`.

.. _color-management-system-configuration:

Operating Systems
=================

Enabling Wide Gamut and HDR
---------------------------

For viewing wide gamut and HDR colors, a monitor with those capabilities is
required.

* macOS: Available on any Apple Silicon device.
* Linux: Use Wayland, and set the Vulkan backend in the Blender system preferences.
* Windows:

  * For wide gamut, enable "Automatically manage color for apps" in the Windows
    display settings.
  * For HDR, enable "Use HDR" in the Windows display settings.
  * Set the Vulkan backend in the Blender system preferences.

Wide Gamut
----------

On Windows and Linux, monitors are not always calibrated for accuracy by default.
Instead, sRGB colors may be mapped to the P3 gamut of the monitor, which makes all
colors more vibrant.

Enabling "Automatically manage color for apps" on Windows or a good display
profile can correct for this.

HDR & Tone Mapping
------------------

While HLG and PQ standards support up to 1000 nits and 10000 nits respectively,
physical monitors only have a limited range. When HDR colors in the video exceed
the limits of the display, video players apply tone mapping to bring the video
into the available range. Blender does not currently perform automatic HDR tone
mapping, and simply clips the colors.

HLG and PQ standards are defined in absolute nits. This makes sense in a controlled
cinema environment. On a computer monitor or TV, brightness can be adjusted and
relative headroom above reference white is the more important metric. This is how
much brighter a color can be compared to an SDR white color. As the display
brightness is lowered, more headroom becomes available.

In Blender, 100 nits is reference white. That means that an HDR view transform with
1000 nits requires 10x headroom to be displayed fully, before tone mapping or
clipping kicks in.

For accurate viewing conditions, HDR monitors can be calibrated to absolute nits.
On macOS, the "HDR Video" display preset locks display brightness to a specific
value for the PQ standard.

Gamma Discrepancies
-------------------

Transfer functions exist to efficiently store and display 8 bit colors,
as linear colors work poorly with few bits. Common transfer functions are
sRGB, Gamma 2.2 and Gamma 2.4.

Ideally, encoding and decoding of images would always use matching transfer
functions. And this is how it works in many cases.

However, on computers there is a peculiar convention where images are
encoded as sRGB, while usually monitors decode with gamma 2.2. This depends
on the specific hardware, operating system and configuration, and it is not
true in general. But many images, games and websites have been created to be
viewed under these conditions.

As long as SDR content is both created and viewed on such computers, there is
no problem. However, when creating content for TV or cinema, or when creating
HDR content, what you see on your computer may not match your target.

Manual Color Management
^^^^^^^^^^^^^^^^^^^^^^^

Traditionally, for accurately viewing content for TV or cinema on a computer
there are a few solutions.

* Keep the monitor at Gamma 2.2, and use a Gamma 2.2 display in OpenColorIO.
* Calibrate the monitor for sRGB, and keep using the default sRGB display in OpenColorIO.
* Change both the monitor calibration and OpenColorIO display to Gamma 2.4.

All involve carefully matching the OpenColorIO display to the monitor transfer
function, so they cancel out exactly. In Blender, this involves turning off
Display Emulation so the transfer function is used as-is.

Automatic Color Management
^^^^^^^^^^^^^^^^^^^^^^^^^^

Modern color management on operating systems does not simply pass on colors
directly from the application to the monitor. Rather both the application and
the monitor are matched to an absolute reference, and the operating system
performs the appropriate conversions.

Blender display emulation is designed to be consistent with other applications
that also integrate with automatic color management. For accurate results, it
is then the operating system and monitor that must be configured.

For HDR, automatic color management is required. Each operating system has
different behavior for HDR and gamma.

* On Windows, enabling "Use HDR" makes the transfer functions cancel out. This
  means HDR content is displayed accurately, and may also be helpful for viewing
  SDR content for TV or cinema. But it does mean the appearance of all applications
  and images is changed.
* On macOS, the default "XDR" display preset can display both SDR and HDR content.
  However for accurately viewing HDR content the "HDR Video" display preset has to
  be used, which will cancel out the transfer functions. Like HDR mode on Windows,
  this changes the appearance of all applications.
* On Linux, Wayland color management supports displaying both SDR and HDR content,
  similar to macOS. Because Wayland does not have a distinct HDR mode, Blender
  automatically switches between sRGB and gamma 2.2 image encoding depending on
  whether an SDR or HDR display was chosen, so that both can be accurate with the
  same system configuration.

