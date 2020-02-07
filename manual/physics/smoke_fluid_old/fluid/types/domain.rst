
************
Fluid Domain
************

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Fluid`
   :Type:      Domain

The bounding box of the object serves as the boundary of the simulation.
All fluid objects **must** be in the domain. Fluid objects outside the domain will not bake.
No tiny droplets can move outside this domain;
it's as if the fluid is contained within the 3D space by invisible force fields.
There can be only a single fluid simulation domain object in the scene.

The shape of the object does **not** matter because it will *always* be treated like a box
(The lengths of the bounding box sides can be different).
So, usually there will not be any reason to use another shape than a box.
If you need obstacles or other boundaries than a box to interfere with the fluid flow,
you need to insert additional obstacle objects *inside* the domain boundary.

This object will be *replaced* by the fluid during the simulation.

.. tip:: Baking is done on the Domain object

   When you calculate the fluid simulation, you bake the simulation on the domain object.
   For this reason all the baking options are visible only when selecting the Domain Object.

   For baking options, see :doc:`Baking </physics/fluid/baking>`.


Settings
========

Resolution
   Render resolution
      The granularity at which the actual fluid simulation is performed.
      This is probably the most important setting for the simulation as it
      determines the amount of details in the fluid, the memory and disk usage as well as computational time.

      .. list-table::

         * - .. figure:: /images/physics_fluid_types_domain_resolution-low.jpg

                10cm mug at Resolution 70.

           - .. figure:: /images/physics_fluid_types_domain_resolution-high.jpg

                10cm mug at Resolution 200.

   .. note::

      The amount of required memory quickly increases: a resolution of 32 requires ca. 4MB,
      64 requires ca. 30MB, while 128 already needs more than 230MB. Make sure to set the resolution low enough,
      depending on how much memory you have, to prevent Blender from crashing or freezing. Remember also that many
      operating systems limit the amount of memory that can be allocated by a single *process*, such as Blender,
      even if the *machine* contains much more than this. Find out what limitations apply to your machine.

   .. note:: Resolution and Real-size of the Domain

      Be sure to set the resolution appropriate to the real-world size of the domain
      (see the *Real World Size* in the `Fluid World`_).
      If the domain is not cubic, the resolution will be taken for the longest side.
      The resolutions along the other sides will be reduced according to their lengths
      (therefore, a non-cubic domain will need less memory than a cubic one, resolutions being the same).

   Preview resolution
      This is the resolution at which the preview surface meshes will be generated.
      So it does not influence the actual simulation.
      Even if "there is nothing to see" in the preview,
      there might be a thin fluid surface that cannot be resolved in the preview.

Display
   How to display a baked simulation in the 3D View (menu *Viewport Display*)
   and for rendering (menu *Render Display*):

   Geometry
      Use the original geometry (before simulation).
   Preview
      Use the preview mesh.
   Final
      Use the final high definition mesh.

   When no baked data is found, the original mesh will be displayed by default.

   After you have baked a domain, it is displayed (usually) in the Blender window as the preview mesh.
   To see the size and scope of the original domain box, select *Geometry* in the left selector.

Speed
   Fluid motion rate. The speed option can be animated to slow down or speed up time.
Reverse Frames
   The simulation is calculated backward.
Offset
   Time offset when reading backed cache.


Fluid Viscosity
===============

.. admonition:: Reference
   :class: refbox

   :Type:      Domain
   :Panel:     :menuselection:`Physics --> Fluid --> Viscosity`

Viscosity Presets
   The "thickness" of the fluid and actually the force needed to move an object of a certain surface area through it
   at a certain speed.

   For manual entry, please note that the normal real-world viscosity (the so-called dynamic viscosity)
   is measured in Pascal-seconds (Pa.s), or in Poise units (P, equal to 0.1 Pa.s, pronounced *pwaz*,
   from the Frenchman Jean-Louis Poiseuille, who discovered the laws on "the laminar flow of viscous fluids"),
   and commonly centiPoise units (cP, equal to 0.001 Pa.s, *sentipwaz*).
   Blender, on the other hand, uses the kinematic viscosity
   (which is dynamic viscosity in Pa.s, divided by the density in kg.m\ :sup:`-3`, unit m\ :sup:`2`.s\ :sup:`-1`).
   The table below gives some examples of fluids together with their dynamic and kinematic viscosities.

   .. list-table::
      Blender viscosity unit conversion.
      :header-rows: 1

      * - Fluid
        - Dynamic viscosity (in cP)
        - Kinematic viscosity (Blender, in m\ :sup:`2`.s\ :sup:`-1`)
      * - Water (20° C)
        - 1.002×10\ :sup:`0` (1.002)
        - 1.002×10\ :sup:`-6` (0.000001002)
      * - Oil SAE 50
        - 5.0×10\ :sup:`2` (500)
        - 5.0×10\ :sup:`-5` (0.00005)
      * - Honey (20° C)
        - 1.0×10\ :sup:`4` (10,000)
        - 2.0×10\ :sup:`-3` (0.002)
      * - Chocolate Syrup
        - 3.0×10\ :sup:`4` (30,000)
        - 3.0×10\ :sup:`-3` (0.003)
      * - Ketchup
        - 1.0×10\ :sup:`5` (100,000)
        - 1.0×10\ :sup:`-1` (0.1)
      * - Melting Glass
        - 1.0×10\ :sup:`15`
        - 1.0×10\ :sup:`0` (1.0)

   Manual entries are specified by a floating point number and an exponent.
   These floating point and exponent entry fields (scientific notation)
   simplify entering very small or large numbers. The viscosity of water at room temperature is 1.002 cP,
   or 0.001002 Pa.s; the density of water is about 1000 kg.m\ :sup:`-3`, which gives a kinematic viscosity of
   0.000001002 m\ :sup:`2`.s\ :sup:`-1` -- so the entry would be 1.002 times 10 to the minus six
   (1.002×10\ :sup:`-6` in scientific notation). Hot glass and melting iron are fluids, but very thick;
   you should enter something like 1.0×10\ :sup:`0` (= 1.0) as its kinematic viscosity
   (indicating a value of 1.0×10\ :sup:`6`\ cP).

   Note that the simulator is not suitable for non-fluids, such as materials that do not "flow".
   Simply setting the viscosity to very large values will not result in rigid body behavior,
   but might cause instabilities.

   .. note:: Viscosity varies

      The default values in Blender are considered typical for those types of fluids and "look right" when animated.
      However, actual viscosity of some fluids,
      especially sugar-laden fluids like chocolate syrup and honey, depend highly on temperature and concentration.
      Oil viscosity varies by SAE rating.
      Glass at room temperature is basically a solid, but glass at 1500 degrees Celsius flows (nearly) like water.
