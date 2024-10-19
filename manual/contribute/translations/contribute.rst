.. highlight:: sh

**********
Contribute
**********

On this page French (``fr``) is used for examples. However, it can be replaced with other
`languages codes <https://www.gnu.org/software/gettext/manual/html_node/Usual-Language-Codes.html>`__.
So, be sure to change the ``/fr`` suffixes in this guide to the language you are translating!

To see which languages are currently available, you can check the
`online interface <https://translate.blender.org/projects/blender-manual/manual/>`__,
or browse the `underlying git repository <https://projects.blender.org/blender/blender-manual-translations>`__.


===================
Simple Contribution
===================

The preferred way to contribute to the translation effort is to use the
`web-based interface <https://translate.blender.org/projects/blender-manual/manual>`__,
currently a Weblate instance.

Simple enhancement suggestions can be contributed by any user, even without logging in.
Suggestions will be reviewed by the translating team before they get published.

Weblate also comes with new helping tools to improve coherence of translations, like the
`glossary <https://translate.blender.org/projects/blender-manual/glossary/>`__.


===================
Advanced Operations
===================

If for some reasons the web-based translation interface does not work well for you,
you can still download the PO file from it, and upload it back later.

.. warning::

   You will have to deal with potential conflicts yourself if some updates happened in the meantime.
   Direct commit to the git repository for translations is not possible anymore.

.. note::

   There is a known issue with the current tool behind the web interface,
   which will make heavy processing like upload and integration of a PO file
   take several minutes, with the web page staying in refresh mode for the whole time.
   If it takes more than ten minutes, it will even apparently fail
   with a server timeout error message.
   There is usually no actual problem though, so no need to re-try uploading the PO file then,
   refreshing the page after a few minutes should be enough
   to see the contribution in the web interface.

.. note::

   First of all, it is assumed that you have the manual already building.
   If you have not done this already go back to
   the :ref:`Getting Started <about-getting-started>` section.


Installing
==========

Language Files
--------------

From the directory containing your checkout of the manual run::

   make checkout_locale

You will be prompted to type in the language folder you want to download.
In the case of this example we will use ``fr``. Pressing :kbd:`Return` will confirm this selection.

It will take a few minutes to download but once complete it will create a ``locale/fr`` subdirectory.

You should have a directory layout like this::

   blender-manual
      |- locale/
      |  |- fr/
      |  |  |- LC_MESSAGES/
      |- manual/

.. note::

   When running Git from the command line (such as updating),
   you will need to change directory to ``locale`` first rather than the ``blender-manual`` directory.


The PO language files themselves can also be downloaded from the web interface, ``Files`` menu,
on each dedicated language page of the ``Manual`` component.


A PO Editor
-----------

To edit the PO files you will need to install a PO editor.
We recommend that you use `Poedit <https://poedit.net/>`__,
however any PO editor will do.

.. note::

   For Linux users, you will need to check with
   your distribution's software center for a version of Poedit.
   This editor is only a recommendation. There are others, such as Kate and Kwrite, which could offer syntax highlighting and basic tools for text editing, e.g. letter case transposes.
   Other platforms can use some text editors supporting the syntax highlighting for PO files,
   or allowing you to create a custom one (such as Notepad++ on Windows).


Building with Translations
==========================

Building
--------

Now you can build the manual with the translation applied:

On Linux and macOS run::

   make -e BF_LANG=fr

On Windows run::

   set BF_LANG=fr
   make html

Now you will have a version of the manual with translations applied.


Editing Translation Files
=========================

Now you can edit the PO translation files, in the ``LC_MESSAGES`` folder you have two files:

- ``blender_manual.po`` -- This is the main translation file that you will be editing.
- ``sphinx.po`` -- This translation file is much smaller and contains translations for the website theme.

To edit these files open them up in your translation editor, i.e. Poedit.
Once in your editor you will see a list of texts, each of these items represent some part of the user manual.
You may need to adjust your editor to sort the list in a way that makes sense for example "by source".

You can now select an untranslated string and your editor will have an input box to add the translation.
The modified ``.po`` files can now be submitted back to the web-based interface.

.. tip::

   Make sure that you `Building with Translations`_ to catch any syntax errors you may make while translating.
   These errors will be displayed as warnings during the build process.


Maintenance
===========

.. _translations-fuzzy-strings:

Keeping Track of Fuzzy Strings
------------------------------

When the manual is updated, those translations which are outdated will be marked as fuzzy.
To keep track with that, you can use a tool we created for that task.

You can do this by running::

   make report_po_progress

This will only give a quick summary however, you can get more information by running::

   python tools/translations/report_translation_progress.py locale/fr/

You should get a list of all the files with information about the number of empty and fuzzy strings.
For more options see::

   python tools/translations/report_translation_progress.py --help


Updating PO Files
-----------------

As the original manual changes, the templates will need updating.
Note, doing this is not required,
as administrator usually update the files for all languages at once.
This allows all languages to be on the same version of the manual.
However, if you need to update the files yourself, it can be done as follows::

   make update_po

The updated templates can then be committed to the repository.

.. seealso::

   A guide how to add a new language can be found in the :doc:`/contribute/translations/add_language`.
