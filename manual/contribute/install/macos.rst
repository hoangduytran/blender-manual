.. highlight:: sh

*********************
Installation on macOS
*********************

This guide covers the following topics:

#. `Installing Dependencies`_
#. `Downloading the Repository`_
#. `Setting up the Build Environment`_

.. note::

   This guide relies heavily on command-line tools.
   It assumes you are the least familiar with the macOS Terminal application.


Installing Dependencies
=======================

Install those packages or make sure you have them in your system.

- `Python <https://www.python.org/>`__
- `PIP <https://pip.pypa.io/en/latest/installing/>`__
- `Git <https://git-scm.com/download/mac>`__


Downloading the Repository
==========================

Simply check out the Blender Manual's repository using::

   cd ~
   git lfs install
   git clone https://projects.blender.org/blender/blender-manual.git

The repository will now be downloaded which may take a few minutes depending on your internet connection.


Setting up the Build Environment
================================

- Open a Terminal window.
- Enter the ``blender-manual`` folder which was just added by ``git clone``::

     cd ~/blender-manual

- Inside that folder is a file called ``requirements.txt`` which contains a list of all the dependencies we need.
  To install these dependencies, we can use the ``pip`` command::

     pip install -r requirements.txt

.. note::

   Every now and then you may want to make sure your dependencies are up to date using::

      pip install -r requirements.txt --upgrade
