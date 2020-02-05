.. _bpy.types.SmokeFlowSettings:

*****************
Smoke Flow Object
*****************

.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Smoke`
   :Type:      Flow

*Smoke Flow* objects are used to add or remove smoke and fire
to a :doc:`Smoke Domain </physics/smoke/types/domain>` object.

To define any mesh object as a *Smoke Flow* object, add smoke physics by clicking *Smoke*
in :menuselection:`Properties --> Physics`. Then select *Flow* as the *Smoke Type*.
Now you should have a default smoke flow source object. You can test this by playing the animation
:kbd:`Alt-A` from the first frame. If your source object is inside your domain, you should see smoke.

.. TODO2.8:
   .. figure:: /images/physics_smoke_types_flow-object_settings.png
      :align: right

      Smoke Flow options.


Settings
========


.. admonition:: Reference
   :class: refbox

   :Panel:     :menuselection:`Physics --> Smoke --> Settings`
   :Type:      Flow


Flow Type
---------

Fire
   Emit only fire. Note that the domain will automatically create some smoke to simulate smoke left by burnt fuel.
Smoke
   Emit only smoke.
Fire + Smoke
   Emit both fire and smoke.
Outflow
   Remove smoke and fire. Note that the shape of the outflow will use the object's :term:`bounding box`.


Initial Values
--------------

Absolute Density
   Maximum density of smoke allowed within range of the source.
Density
   Amount of smoke to emit at once.

.. _smoke-flow-temp-diff:

Temperature Difference
   Difference between the temperature of emitted smoke and the domain's ambient temperature.
   This setting's effect on smoke depends on the domain's :ref:`Temperature Difference <smoke-domain-temp-diff>`.
Smoke Color
   Color of emitted smoke. When smoke of different colors are mixed they will blend together,
   eventually settling into a new combined color.

   .. figure:: /images/physics_smoke_types_flow-object_color-blending.jpg

Flame Rate
   Amount of "fuel" being burned per second. Larger values result in larger flames,
   smaller values result in smaller flames:

   .. figure:: /images/physics_smoke_types_flow-object_flame-rate.jpg

      Example showing two fire sources.
      The object on the left has a *Flame Rate* of 5, while the one on the right has 0.3.

Sampling Subframes
   Number of subframes used to reduce gaps in emission of smoke from fast-moving sources.

   .. figure:: /images/physics_smoke_types_flow-object_subframes.jpg

      Example showing two fast-moving sources.
      The object on the left uses 0 subframes, while the one on the right uses 6.

Vertex Group
   When set, use the specified :doc:`Vertex Group </modeling/meshes/properties/vertex_groups/vertex_groups>`
   to control where smoke is emitted.
