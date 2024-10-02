
*******
Startup
*******

There are some common causes for problems when using Blender.
If Blender fails to start, there are a few things to check for:

- See if your computer meets the `minimum requirements <https://www.blender.org/download/requirements/>`__.
- Confirm that your graphics card is supported and that the drivers are up to date (see
  :doc:`/troubleshooting/gpu/index`).
- Make sure any antivirus software is not preventing Blender from starting.

If you cannot find a solution to your problem here,
try asking the :doc:`community </getting_started/about/community>` for help.


Common Startup Messages
=======================

The *Blender Console Window* can display many different types of status and error messages.
Some messages simply inform the user what Blender is doing, but have no real impact on Blender's ability to function.
Other messages can indicate serious errors that will most likely prevent Blender carrying out a particular task and
may even make Blender non-responsive or shut down completely. The *Blender Console Window* messages can
also originate internally from within the Blender code or from external sources such as
:doc:`Python scripts </editors/preferences/extensions>`.

``found bundled python: {DIR}``
   This message indicates that Blender was able to find the :ref:`Python <scripting-index>`
   library for the Python interpreter embedded within Blender.
   If this folder is missing or unable to be found,
   it is likely that an error will occur, and this message will not appear.

``Read prefs: {DIR}/userpref.blend``
   The preferences use this path.
