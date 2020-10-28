.. _bpy.types.MovieTrackingCamera:

******
Camera
******

This panel contains all settings of the camera used for filming the movie
which is currently being edited in the Clip editor.

Camera Presets
   Predefined settings can be used here.
   But such settings as distortion coefficients and principal point are not included in the presets and
   should be filled in even if camera presets are used.
Sensor
   Width
      Is the width of the CCD sensor in the camera. This value can be found in camera specifications.
   Pixel Aspect Ratio
      Is the pixel aspect of the CCD sensor. This value can be found in camera specifications,
      but can also be guessed. For example, you know that the footage should be 1920×1080,
      but the images themselves are 1280×1080. In this case, the pixel aspect is: 1920 / 1280 = 1.5.
Optical Center
   Is the optical center of the lens used in the camera. In most cases it is equal to the image center,
   but it can be different in some special cases. Check camera/lens specifications in such cases.
   To set the optical center to the center of image, there is a *Set Center* button below the sliders.

   .. tip:: Optical Center also know as Principal Point in photogrammetry.


Lens
====

Focal Length
   Is self-explanatory; it is the focal length with which the movie was shot.
   It can be set in millimeters or pixels.

Distortion Model
   Mathematical function to convert distorted to undistorted coordinates.

   Polynomial
      Polynomial radial distortion. Uses three distortion coefficients: K1, K2, and K3.
   Division
      It defines high distortions, which makes this model suitable much better for cameras with fisheye lenses.
      Use two distortion coefficients: K1, K2.
   Nuke
      Distortion model used by the Nuke compositor. Use two distortion coefficients K1, K2.
   Brown
      Brown-Conrady is one of most advanced mathematical lens distortion models.
      Used to model both radial and tangential distortion. Can use up to four
      radial distortion coefficients: K1-K4 and up to two tangential distortion coefficients: P1 and P2.

Coefficients
   Coefficients are used to compensate for lens distortion when the movie was shot.
   Currently these values can be tweaked by hand only (there are no calibration tools yet)
   using tools available in Distortion mode. Basically, just tweak K1 until solving is most
   accurate for the known focal length (but also take grid and annotations into account
   to prevent "impossible" distortion).

   Radial distortion coefficients (K1-K4)
      The coefficients in lens distortion models work independent from each other
      and positive values will give a barrel distortion. Negative values give pincushion distortion.
      A mixture of both negative and positive coefficients allow define more complicated
      mustache distortions or complex distortion, that is less common but not rare.

      .. figure:: /images/movie_clip_tracking_clip_properties_track_camera_lens_distortion_k.png

         Example of radial distortion for positive and negative K coefficients

   Tangential distortion coefficients (P1,P2)
      Work independent and allow compensate situations when sensor is not perpendicular to a group of lens.
      P1 is used to compensate for sensor rotation in Z (vertical) axes,
      while P2 is for compensating sensor rotation in X (horizontal) axes.
      Such distortions can be found in source from cameras with sensor stabilization system.

      .. figure:: /images/movie_clip_tracking_clip_properties_track_camera_lens_distortions_p.png

         Example of tangential distortion for P1, P2 coefficients

Optical Center (Principal Point) is important value in camera lens distortion,
it can be shifted (distorted) from sensor center in images from cameras with sensor stabilization.
And using correct values can increase quality of clip undistortion results.
