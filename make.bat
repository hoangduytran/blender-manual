@ECHO OFF

REM Command file for Sphinx documentation

REM Use virtual environment if it exists.
set SPHINX_BIN_PATH=.venv\Scripts\
if not exist "%SPHINX_BIN_PATH%" (
  set SPHINX_BIN_PATH=
)
if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=%SPHINX_BIN_PATH%sphinx-build
)
if "%SPHINXAUTOBUILD%" == "" (
	set SPHINXAUTOBUILD=%SPHINX_BIN_PATH%sphinx-autobuild
)
set SOURCEDIR=.\manual
set BUILDDIR=build
if "%BF_LANG%" == "" set BF_LANG=en
set SPHINXOPTS=-j auto -D language=%BF_LANG%

REM Check if sphinx-build is available and fallback to Python version if any
%SPHINXBUILD% 1>NUL 2>NUL
if errorlevel 9009 goto sphinx_python
goto sphinx_ok

:sphinx_python

set SPHINXBUILD=python -m sphinx.__init__
%SPHINXBUILD% 2> nul
if not "%1" == "setup" (
	if errorlevel 9009 (
		echo.
		echo The 'sphinx-build' command was not found. Make sure you have Sphinx
		echo installed, then set the SPHINXBUILD environment variable to point
		echo to the full path of the 'sphinx-build' executable. Alternatively you
		echo may add the Sphinx directory to PATH.
		echo.
		echo If you don't have Sphinx installed, grab it from
		echo http://sphinx-doc.org/
		rem Exit with errorlevel 1
		exit /b 1
	)
)

:sphinx_ok

REM Default to livehtml
if "%1" == "" (
	goto livehtml
)

if "%1" == "help" (
	echo.
	echo Sphinx
	echo ======
	%SPHINXBUILD% -M help "%SOURCEDIR%" "%BUILDDIR%" %SPHINXOPTS% %O%
	echo.
	echo Custom Targets
	echo ==============
	echo Convenience targets provided for building docs
	echo.
	echo - livehtml [default]   to auto build on file changes and host on localhost
	echo.
	echo Translations
	echo ------------
	echo.
	echo - update_po            to update PO message catalogs
	echo - report_po_progress   to check the progress/fuzzy strings [optionally specify locale]
	echo.
	echo Checking
	echo --------
	echo.
	echo - check_structure      to check the structure of all .rst files
	echo - check_syntax         to check the syntax of all .rst files
	echo - check_spelling       to check spelling for text in RST files
	echo.
	echo Utilities
	echo ---------
	echo.
	echo - update               to update the repository to the most recent version.
	goto EOF
)

if "%1" == "setup" (
	python -m venv ".venv"
	".venv/Scripts/pip" install -r "requirements.txt" --upgrade
	goto EOF
)

if "%1" == "livehtml" (
	:livehtml
	%SPHINXAUTOBUILD% --open-browser --delay 0 "%SOURCEDIR%" "%BUILDDIR%\html" %SPHINXOPTS% %O%
	if errorlevel 1 exit /b 1
	goto EOF
)

if "%1" == "latexpdf" (
	%SPHINXBUILD% -b latex %SPHINXOPTS% %O% "%SOURCEDIR%" "%BUILDDIR%\latex"
	cd "%BUILDDIR%\latex"
	make all-pdf
	cd %~dp0
	echo To view, run:
	echo   start "%BUILDDIR%\html\blender_manual.pdf"
	goto EOF
)

if "%1" == "check_syntax" (
	python tools\check_source\check_syntax.py --kbd --long
	goto EOF
)

if "%1" == "checkout_locale" (
	python build_files\utils\checkout_locale.py
	goto EOF
)

if "%1" == "update_po" (
	python tools/utils_maintenance\update_po.py
	goto EOF
)

if "%1" == "report_po_progress" (
	IF NOT EXIST %cd%\locale GOTO MISSING_LOCALE
	python tools\translations\report_translation_progress.py locale\%2 --quiet
	goto EOF

)

if "%1" == "check_spelling" (
	python tools\check_source\check_spelling.py
	goto EOF
)

if "%1" == "check_structure" (
	python tools\check_source\check_images.py
	python tools\check_source\check_structure.py
	goto EOF

if "%1" == "update" (
	python build_files\utils\make_update.py
	goto EOF

) else (
	%SPHINXBUILD% -M %1 "%SOURCEDIR%" "%BUILDDIR%" %SPHINXOPTS% %O%
	goto EOF
)

:MISSING_LOCALE
echo.
echo The locale directory is missing.
echo.
echo To correct this, checkout one or more translation repositories.
echo   Details can be found at: 
echo   https://docs.blender.org/manual/en/latest/about/contribute/translations/contribute.html
rem Exit with errorlevel 1
exit /b 1

:EOF
