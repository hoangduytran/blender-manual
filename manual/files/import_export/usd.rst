
***************************
Universal Scene Description
***************************


Importing USD Files
===================

`USD <https://graphics.pixar.com/usd/release/index.html>`__ files typically represent the scene as
a hierarchy of primitives, or `prims <https://graphics.pixar.com/usd/release/glossary.html#USDGlossary-Prim>`__.
Individual prims contain data to describe scene entities, such as geometry, lights, cameras and transform hierarchies.
Blender's USD importer converts USD prims to a hierarchy of Blender objects. Like the USD exporter,
the importer does not yet handle more advanced USD concepts, such as layers and references.

The following USD data types can be imported as Blender objects:

- Cameras
- Curves
- Lights
- Materials
- Meshes
- Primitive Shapes
- Volume

For more information on how the various data types are handled,
see the following descriptions of the `Import Options`_.

.. note::

   When importing a `USDZ archive <https://openusd.org/release/spec_usdz.html>`__, it is
   important to carefully consider the :ref:`Import Textures <usd-import-textures>` option to determine
   whether and how to copy texture files from the zip archive.


Xform and Scope Primitives
--------------------------

USD provides an ``Xform`` prim type, containing transform data, which can be
used to represent transform hierarchies and to organize the scene.
Such ``Xform`` prims are imported as Blender empty objects.

USD also supports ``Scope`` primitives, which are entities
that do not contain transform data, but which serve to group other element of the scene.
Blender doesn't have an exact counterpart to the concept of a scope,
so such primitives are imported as Blender empties located at the origin.
This is an imperfect representation, because empty objects have a transform and ``Scopes`` do not,
but this approach nonetheless helps preserve the structure of the scene hierarchy.


PointInstancer Primitives
-------------------------

USD provides a ``UsdGeomPointInstancer`` prim type,
containing instances that are scattered on a primitive's points.

These are imported into Blender as Point Clouds using a
:doc:`/modeling/modifiers/generate/geometry_nodes`
and the :doc:`/modeling/geometry_nodes/instances/instance_on_points`.


Animations
----------

The importer supports two types of animation:

- **Animating transforms**: If a USD primitive has time-varying transform data,
  a :doc:`Transform Cache </animation/constraints/transform/transform_cache>` constraint
  will be added to the imported Blender object.
- **Animating geometry**: Animating mesh and curve geometry is supported by adding
  a :doc:`Mesh Sequence Cache </modeling/modifiers/modify/mesh_sequence_cache>` modifier to the imported data.
  Geometry attribute (`USD Primvar <https://graphics.pixar.com/usd/release/glossary.html#USDGlossary-Primvar>`__)
  animation is currently supported only for Color Attributes and UVs.
  Note that USD file sequences (i.e. a unique file per frame) are not yet supported.


Materials
---------

If a USD mesh or geometry subset has a bound material, the importer will assign to
the Blender object a material with the same name as the USD material.
If a Blender material with the same name already exists in the scene, the existing material may be used,
depending on the :ref:`Material Name Collision <usd-material-name-collision>` option.
Otherwise, a new material will be created.

If the USD material has
a `USD Preview Surface <https://graphics.pixar.com/usd/release/spec_usdpreviewsurface.html>`__ shader source,
the :ref:`render-materials-settings-viewport-display` color, metallic, and roughness are set to
the corresponding USD Preview Surface input values.

There is also an *Import USD Preview* option to convert USD Preview Surface shaders
to Blender :doc:`Principled BSDF </render/shader_nodes/shader/principled>` shader nodes.
This option can be lossy, as it does not yet handle converting all shader settings and types,
but it can generate approximate visualizations of the materials.


Coordinate System Orientation
-----------------------------

If the imported USD is Y up, a rotation will be automatically applied to
root objects to convert to Blender's Z up orientation.


Import Options
==============

The following options are available when importing from USD:


General
-------

Path Mask
   Import only the subset of the USD scene rooted at the given primitive.

Include
   Visible Primitives Only
      Do not import invisible USD primitives. Only applies to primitives with a non-animated
      `visibility <https://graphics.pixar.com/usd/release/glossary.html#USDGlossary-Visibility>`__ attribute.
      Primitives with animated visibility will always be imported.
   Defined Primitives Only
      When disabled this allows importing USD primitives
      which are not defined, such as those with an override specifier.

Set Frame Range
   Update the scene's start and end frame to match those of the USD stage.
Create Collection
   Add all imported objects to a new collection.
Relative Path
   Select the file relative to the blend-file.

Scale
   Value by which to scale the imported objects in relation to the world's origin.
Light Intensity Scale
   Scale for the intensity of imported lights.

Custom Properties
   Behavior when importing USD attributes as :ref:`Custom Properties <files-data_blocks-custom-properties>`.

   :None: Does not import USD custom attributes.
   :User:
      Imports USD attributes in the ``userProperties`` namespace as custom properties.
      The namespace will be stripped from the property names.
   :All Custom:
      Imports all USD custom attributes as custom properties.
      Namespaces will be retained in the property names.


Object Types
------------

Cameras
   Import cameras (perspective and orthographic).
Curves
   Import curve primitives, including USD basis and NURBS curves.
   (Note that support for Bézier basis is not yet fully implemented.)
Lights
   Import lights. Does not currently include USD dome, cylinder or geometry lights.
Materials
   Import materials.
Meshes
   Import meshes.
Volumes
   Import USD OpenVDB field assets.
Point Clouds
   Imports USD ``UsdGeomPoints`` as a :doc:`/modeling/point_cloud` object.
USD Shapes
   Imports USD primitive shapes (cubes, spheres, cones, ect) as Blender meshes.

Display Purpose
   Render
      Include primitives with purpose ``render``.
   Proxy
      Include primitives with purpose ``proxy``.
   Guide
      Include primitives with
      `purpose <https://graphics.pixar.com/usd/release/glossary.html#USDGlossary-Purpose>`__ ``guide``.

Material Purpose
   Attempt to import materials with the given purpose.
   If no material with this purpose is bound to the primitive, fall back on loading any other bound material.

   :All Purpose: Attempt to import ``allPurpose`` materials.
   :Preview: Attempt to import ``preview`` materials. Load ``allPurpose`` materials as a fallback.
   :Full: Attempt to import ``full`` materials. Load ``allPurpose`` or ``preview`` materials, in that order, as a fallback".


Geometry
--------

UV Coordinates
   Read mesh UV coordinates.
Color Attributes
   Convert the USD mesh ``displayColor`` values to Blender's Color Attributes.
Mesh Attributes
   Read USD ``Primvars`` as mesh attributes.
Subdivision
   Create Subdivision Surface modifiers based on the USD ``SubdivisionScheme`` attribute.

Validate Meshes
   Check the imported mesh for corrupt data and fix it if necessary.
   When disabled, erroneous data may cause crashes displaying or editing the meshes.
   This option will make the importing slower but is recommended, as data errors are not always obvious.


Rigging
-------

Shape Keys
   Imports USD blend shapes as Blender's :doc:`/animation/shape_keys/index`.
Armatures
   Imports USD skeletons as Blender's :doc:`/animation/armatures/index`.


Materials
---------

Import All Materials
   Also import materials that are not used by any geometry.
   Note, when this option is false, materials referenced by geometry will still be imported.

Import USD Preview
   Convert USD Preview Surface shaders to Principled BSDF shader networks.

Create World Material
   Converts the first discovered USD dome light to a :doc:`world background shader </render/lights/world>`.

Set Material Blend
   If the *Import USD Preview* option is enabled, the material blend method will automatically be set based on
   the ``opacity`` and ``opacityThreshold`` shader inputs, allowing for visualization of transparent objects.

.. _usd-material-name-collision:

Material Name Collision
   Behavior when the name of an imported material conflicts with an existing material.

   :Make Unique: Import each USD material as a unique Blender material.
   :Reference Existing: If a material with the same name already exists, reference that instead of importing.


Textures
--------

When importing a USDZ package, the following options specify whether and how texture asset dependencies
of the USD should be copied from the zip archive so they can be loaded into Blender.

.. _usd-import-textures:

Import Textures
   Behavior when importing textures from a USDZ archive.

   :None: Don't import textures. Note that, with this option, material textures may fail to be resolved in Blender.
   :Packed: Import textures as packed data in the Blender file.
   :Copy: Copy files to the directory specified in the **Textures Directory** option.

Textures Directory
   Path to the directory where imported textures will be copied, when the **Import Textures** mode is **Copy**.

   Note that the default textures directory is the relative path ``//textures``, which requires the
   Blender file to have been saved before importing, so the relative path can be resolved.

File Name Collision
   Behavior when the name of an imported texture file conflicts with an existing file.

   :Use Existing: If a file with the same name already exists, use that instead of copying.
   :Overwrite: Overwrite existing files.


Particles and Instancing
------------------------

Scene Instancing
   Import USD scene graph instances as collection instances, otherwise they are imported as copies.


Exporting to USD Files
======================

Universal Scene Description (USD) files can contain complex layering, overriding, and references to other files.
Blender's USD Exporter takes a much simpler approach. When exporting, all visible, supported objects in
the scene are exported, optionally limited by their selection state. Blender does not (yet) support exporting
invisible objects, USD layers, variants, etc.

The following objects can be exported to USD:

- Meshes (of different kinds, see below).
- Cameras (perspective cameras only at the moment, not orthogonal ones).
- Light (all types except area lights).
- Hair (exported as curves, and limited to parent strands).
- Volume (both static and animated volumes).
- Armatures

When exporting an animation, the final, evaluated mesh is written to USD.
This means that the following meshes can be exported:

- Static meshes.
- Deforming meshes; here the topology of the mesh does not change,
  but the locations of the vertices change over time. Examples are animated characters or
  bouncing (but not cracking) objects.
- Arbitrarily animated meshes; here the topology does change.
  An example is the result of a fluid simulation, where splashes of fluid can break off the main body.
- Metaballs are exported as animated meshes.

.. note::

   To export the Blender scene as a `USDZ archive <https://openusd.org/release/spec_usdz.html>`__, set
   the file extension of the output file to ``.usdz``.  The exported USDZ package will be a zip archive
   containing the USD and its texture file dependencies.

.. figure:: /images/files_import-export_usd_example.png

   Shot from `Spring <https://studio.blender.org/films/spring/>`__ exported to USD and opened in USDView.


.. _bpy.ops.wm.usd_export:

Export Options
==============

The following options are available when exporting to USD:


General
-------

Root Prim
   If set, add a transform primitive with the given path to the stage as the parent of all exported data.

Include
   Selection Only
      When checked, only selected objects are exported.
      Instanced objects, for example collections that are instanced in the scene,
      are considered 'selected' when their instancer is selected.
   Visible Only
      Only exports objects that are not :doc:`hidden </scene_layout/object/editing/show_hide>`.
      Invisible parents of exported objects are exported as empty transforms.
   Animation
      When checked, the entire scene frame range is exported.
      When unchecked, only the current scene frame is exported.

Blender Data
   Custom Properties
      Exports :ref:`Custom Properties <files-data_blocks-custom-properties>` as USD attributes.
      The *Namespace* property is used to determine the namespace that the attributes are written to.
   Namespace
      If set, add the given namespace as a prefix to exported custom property names.
      This only applies to property names that do not already have a prefix
      (e.g., it would apply to name ``bar`` but not ``foo:bar``) and does not apply to Blender
      object and data names which are always exported in the ``userProperties:blender`` namespace.

      By default, ``userProperties`` namespace is used.
   Blender Names
      Author USD custom attributes containing the original Blender object and object data names.

Allow Unicode
   Preserves UTF-8 encoded characters when writing USD prim and property names
   (requires software utilizing USD 24.03 or greater when opening the resulting files).

File References
   Relative Paths
      Use relative paths to reference external files (i.e. textures, volumes) in the exported USD file,
      otherwise use absolute paths.

Convert Orientation
   Convert orientation axis to a different convention to match other applications.
   Blender uses Y Forward, Z Up (since the front view looks along the +Y direction).
   For example, its common for applications to use Y as the up axis, in that case -Z Forward, Y Up is needed.

   Forward / Up Axis
      By mapping these to different axes you can convert rotations between applications default up and forward axes.

Xform Ops
   The type of transform operators to use to transform prims.

   :Translate, Rotate, Scale: Export with translate, rotate, and scale ``Xform`` operators.
   :Translate, Orient, Scale: Export with translate, orient quaternion, and scale ``Xform`` operators.
   :Matrix: Export matrix operator.

Use Settings for
   Determines the whether to use *Viewport* or *Render* visibility of collection, modifiers,
   or any other property that can be set for both the *Viewport* and *Render*.


Object Types
------------

Meshes
   Exports :doc:`Mesh Objects </modeling/meshes/index>`
Lights
   Exports :doc:`Light Objects </render/lights/index>`
   USD does not directly support spot lights, so those are not exported.
Cameras
   Exports :doc:`Camera Objects </render/cameras>`
   Only perspective cameras are exported.
Volumes
   Exports :doc:`Volume Objects </modeling/volumes/index>`
Curves
   Exports :doc:`Curve Objects </modeling/curves/index>`
Hair
   Exports parent hair strands are exported as a curve system.
   Hair strand colors are not exported.


Geometry
--------

UV Maps
   When checked, includes UV coordinates for exported meshes.
   The name of the UV map in USD is the same as the name in Blender.

Rename UV Maps
   Exports UV maps using the USD  default name (``st``) as opposed to Blender's default name (``UVMap``).

Normals
   When checked, includes normals for exported meshes. This includes custom loop normals.

Triangulate
   Triangulates the mesh before writing. For more detail on the specific option see
   the :doc:`Triangulate modifier </modeling/modifiers/generate/triangulate>`.


Rigging
-------

Shape Keys
   Export shape keys as USD blend shapes.

   Absolute shape keys are not supported.

Armatures
   Export :doc:`Armatures </animation/armatures/index>` and meshes with
   :doc:`Armature Modifiers </modeling/modifiers/deform/armature>` as USD skeletons and skinned meshes.

   Limitations:

   - Modifiers in addition to Armature modifiers will not be applied.
   - Bendy bones are not supported.

Only Deform Bones
   Only export :ref:`deform bones <bpy.types.Bone.use_deform>` and their parents.


Materials
---------

Exports material information of the object.
By default the exporter approximates the :doc:`/render/shader_nodes/shader/principled`
node tree by converting it to USD's Preview Surface format.

When a mesh has multiple materials assigned, a geometry subset is created for each material.
The first material (if any) is always applied to the mesh itself as well
(regardless of the existence of geometry subsets),
because the Hydra viewport does not support materials on subsets.
See `USD issue #542 <https://github.com/PixarAnimationStudios/USD/issues/542>`__
for more information.

.. note::

   If *USD Preview Surface Network* and *MaterialX Network* are disabled,
   the material is set to the viewport materials of meshes.

USD Preview Surface Network
   Approximates a :doc:`/render/shader_nodes/shader/principled`
   node tree to by converting it to USD's Preview Surface format.

   .. warning::

      Not all nodes are supported; currently only Diffuse,
      Principle, Image Textures, and UVMap nodes are support.

MaterialX Network
   Generates material shading graphs using the `MaterialX <http://materialx.org/>`__ standard.
   This standard is designed to support a high amount of interoperability among
   :abbr:`DCCs <Digital Content Creation>`. In Blender, MaterialX supports most
   of the shader nodes and their functionality but has a few caveats (see below).

   .. admonition:: Implementation Caveats
      :class: important

      When using the Principled BSDF, the resulting graph is very usable.
      However, when using some of the other BSDFs, some of the generated
      shading graphs are difficult for other DCC's to understand.

Convert World Material
   Convert the :doc:`world material </render/lights/world>` to a USD dome light.
   Currently works for simple materials, consisting of an environment texture connected to a background shader,
   with an optional vector multiply of the texture color.

Export Textures
   Method for exporting textures.

   :Keep: Use original location of textures.
   :Preserve:
      Preserve file paths of textures from already imported USD files.
      Export remaining textures to a 'textures' folder next to the USD file.
   :New Path: Export textures to a 'textures' folder next to the USD file.

Overwrite Textures
   Allow overwriting existing texture files when exporting textures.

USDZ Texture Downsampling
   Choose a maximum size for all exported textures.

   :Keep: Keep all current texture sizes.
   :256: Resize to a maximum of 256 pixels.
   :512: Resize to a maximum of 512 pixels.
   :1024: Resize to a maximum of 1024 pixels.
   :2048: Resize to a maximum of 2048 pixels.
   :4096: Resize to a maximum of 4096 pixels.
   :Custom: Specify a custom size.

      USDZ Custom Downscale Size
         The size in pixels of the *Custom* downsampling.


Experimental
------------

Instancing
   As this is an experimental option. When unchecked,
   duplicated objects are exported as real objects, so a particle system with
   100 particles that is displayed with 100 meshes will have 100 individual meshes
   in the exported file. When checked, duplicated objects are exported as
   a reference to the original object. If the original object is not part of the export,
   the first duplicate is exported as real object and used as reference.


Exporter Limitations
====================

Single-sided and Double-sided Meshes
   USD seems to support neither per-material nor per-face-group double-sidedness,
   so Blender uses the flag from the first material to mark the entire mesh as single/double-sided.
   If there is no material it defaults to double-sided.

Mesh Normals
   The mesh subdivision scheme in USD is 'Catmull-Clark' by default,
   but Blender uses 'None' instead, indicating that a polygonal mesh is exported.
   This is necessary for USD to understand the custom normals;
   otherwise the mesh is always rendered smooth.

Vertex Velocities
   Currently only fluid simulations (not meshes in general) have explicit vertex velocities.
   This is the most important case for exporting velocities, though,
   as the baked mesh changes topology all the time, and
   thus computing the velocities at import time in a post-processing step is hard.

Materials
   When there are multiple materials, the mesh faces are stored as geometry subset
   and each material is assigned to the appropriate subset.
   If there is only one material this is skipped. Note that the geometry subsets are not time-sampled,
   so it may break when an animated mesh changes topology.

Hair
   Only the parent strands are exported, and only with a constant color.
   No UV coordinates, and no information about the normals.

Camera
   Only perspective cameras are exported.

Lights
   USD does not directly support spot lights, so those are not exported.

Particles
   Particles are only written when they are alive, which means that they are always visible.
   There is currently no code that deals with marking them as invisible outside their lifespan.

   Objects instanced by particle system are exported by suffixing the object name with
   the particle's persistent ID, giving each particle transform a unique name.

Instancing/Referencing
   This is still an experimental feature that can be enabled when exporting to USD.
   When enabled, instanced object meshes are written to USD as references to the original mesh.
   The first copy of the mesh is written for real, and the following copies are referencing the first.
   Which mesh is considered 'the first' is chosen more or less arbitrarily.

USDZ
   Due to a current limitation in the USD library, UDIM textures cannot be include in the USDZ archive.
   This limitation will likely be addressed in a future version of USD.
   (See `USD pull request #2133 <https://github.com/PixarAnimationStudios/USD/pull/2133>`__.)
