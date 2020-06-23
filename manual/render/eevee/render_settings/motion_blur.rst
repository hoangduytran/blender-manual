.. _bpy.types.SceneEEVEE.motion_blur:

***********
Motion Blur
***********
The Motion Blur effect in EEVEE is a combination of two techniques.

First, it uses a fast post-process vector blur using a vector motion pass.
This blurs the image between 3 time steps using pixel velocity.
This technique is fast and produce clean gradients but have issues at objects
borders or if the motion is locally too complex (too many vector variation in small areas).

This technique uses random sampling and the noise amount is proportional to the sample count found in 
:menuselection:`Properties --> Render --> Sampling --> Render Samples`.
The screenspace limit of this technique can be tweaked using :menuselection:`Max Blur`.

.. note::

   Memory usage (VRAM) will increase threefold for objects using deformation motion blur
   if using post-process blur.

.. note::

   Alpha blended surface or volumetric effects will not have the correct velocity and will not
   be correctly blurred by this technique. Use the second technique for that.


On top of that, EEVEE splits the render into multiple timesteps and accumulates the result
which is known as Accumulation Motion Blur.
This technique is precise but requires many steps for clean gradients.
This is used in combination with the post-process blur to handle the inter-step gaps.
Each step corresponds to a full scene re-evaluation and can add a lot of overhead to the rendertime.
Adding more steps also allows to reduce the maximum blur parameters as the post-process blur will need
to cover less distance.


.. note::

   When using multiple timesteps, the render sample count is rounded up to the next multiple
   of motion steps to ensure even distribution of samples accross steps.


.. _fig-render-motion-blur-properties-example:

.. list-table::

   * - .. figure:: /images/render_eevee_motion-blur_1step_nofx.png
          :width: 310px

          No motion blur.

     - .. figure:: /images/render_eevee_motion-blur_1step_fx.png
          :width: 310px

          Only post-process blur.

   * - .. figure:: /images/render_eevee_motion-blur_4step_nofx.png
          :width: 310px

          4 time steps without post-process blur.

     - .. figure:: /images/render_eevee_motion-blur_4step_fx.png
          :width: 310px

          4 time steps with post-process blur.

   * - .. figure:: /images/render_eevee_motion-blur_32step_nofx.png
          :width: 310px

          32 time steps without post-process blur.

     - .. figure:: /images/render_eevee_motion-blur_32step_fx.png
          :width: 310px

          32 time steps with post-process blur.


.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Render --> Motion Blur`

Shutter
   Time (in frames) taken between shutter open and close.

Background Separation
   Used by the post-process blur to avoid blurring background over foreground. Lower values will reduce background bleeding onto foreground elements.

Max Blur
   Maximum blur distance a pixel can spread over. A value of 0 will disable the post-process blur and only use the
   accumulation blur.

.. note::

   High maximum blur values may also reduce the quality.

Motion steps
   This controls the number of steps used by the accumulation blur and thus its accuracy. More steps means longer
   render time. 