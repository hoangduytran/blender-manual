.. index:: Modeling Modifiers; Volume Displace

************************
Volume Displace Modifier
************************

The *Volume Displace* modifier displaces existing volume grids based on a 3D texture.
It uses the red, green and blue components of the texture to displace the volume into the x, y and z direction.

.. note::

   Greyscale textures lead to stretching along one axis.
   It's best to use a color texture.

Options
=======

Texture
   The texture that is evaluated at every voxel to determine how far and in what direction to displace.

Strength
   Controls how far voxels are displaced.

Sample Radius
   Smaller values result in better performance, but might cut off the volume outside.

Mid Level
   This should be modified if the texture offsets the entire volume in one direction and you want to center it again.
   For performance reasons, the displaced volume should stay close to its original position.
