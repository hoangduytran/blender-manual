.. index:: Geometry Nodes; Invert Matrix
.. _bpy.types.FunctionNodeInvertMatrix:

******************
Invert Matrix Node
******************

.. figure:: /images/node-types_FunctionNodeInvertMatrix.webp
   :align: right
   :alt: Invert Matrix node.

The *Invert Matrix* node returns the mathematical
`inverse matrix <https://mathworld.wolfram.com/MatrixInverse.html>`__.


Inputs
======

Matrix
   The matrix to invert.


Properties
==========

This node has no properties.


Outputs
=======

Matrix
   The inverted matrix.
Invertible
   Returns true if the matrix cannot be inverted.
   For example. this can happen when a transformation matrix has a scale of zero.
   See `Invertible matrix <https://en.wikipedia.org/wiki/Invertible_matrix>`__ for more information.

   .. important::

      When a matrix is invertible, the `identity matrix <https://en.wikipedia.org/wiki/Identity_matrix>`__
      is returned.
