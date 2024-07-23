.. highlight:: sh

*********************
Installation on Linux
*********************

This guide covers the following topics:

#. `Installing Dependencies`_
#. `Downloading the Repository`_
#. `Setting up the Build Environment`_


Installing Dependencies
=======================

Below are listed the installation commands for popular Linux distributions.

For the appropriate system, run the command in a terminal:

Debian/Ubuntu::

   sudo apt-get install python3 python3-pip git git-lfs
   git lfs install --skip-repo

Redhat/Fedora::

   sudo dnf install python python-pip git git-lfs
   git lfs install --skip-repo

Arch Linux::

   sudo pacman -S python python-pip git git-lfs
   git lfs install --skip-repo


Downloading the Repository
==========================

Simply check out the Blender Manual's repository using::

   cd ~
   git clone https://projects.blender.org/blender/blender-manual.git

The repository will now be downloaded which may take a few minutes depending on your internet connection.


Setting up the Build Environment
================================

.. tip::

   It is recommended to setup and activate a virtual Python environment where dependencies will be installed::

      python3 -m venv .venv
      source .venv/bin/activate

   Repeat the ``source .venv/bin/activate`` command to re-activate the virtual environment,
   whenever you open a new terminal to build the documentation.

   This step may be required on some distributions that enforce `PEP 668 <https://peps.python.org/pep-0668/>`__.


- Open a Terminal window.
- Enter the ``blender-manual`` folder which was just added by ``git clone``::

     cd ~/blender-manual

- Inside that folder is a file called ``requirements.txt`` which contains a list of all the dependencies we need.
  To install these dependencies, we can use the ``pip3`` command::

     pip3 install -r requirements.txt

.. note::

   Every now and then you may want to make sure your dependencies are up to date using::

      pip3 install -r requirements.txt --upgrade
