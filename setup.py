import os
import sys
import re
import setuptools

# Read the contents of your requirements.txt file
with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

# Read the contents of your README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import astropy

def get_version_info():
    """Reads version and release from graxpert/version.py - since we now build in an isolated env."""
    version_file_path = os.path.join("graxpert", "version.py")
    with open(version_file_path, "r", encoding="utf-8") as f:
        version_file_content = f.read()

    version_match = re.search(r"^version\s*=\s*['\"]([^'\"]*)['\"]", version_file_content, re.M)
    release_match = re.search(r"^release\s*=\s*['\"]([^'\"]*)['\"]", version_file_content, re.M)

    if version_match and release_match:
        return version_match.group(1), release_match.group(1)
    
    raise RuntimeError("Unable to find version and release strings in graxpert/version.py.")

version, release = get_version_info()

# Shared build options for setuptools.setup and cx_Freeze.setup
setup_options = {
    'name':"graxpert",
    'version':version,
    'description':"GraXpert is an astronomical image processing program for extracting and removing gradients in the background of your astrophotos",
    'license':"GLP-3.0",

    # A long description that will be displayed on PyPI
    'long_description':long_description,
    'long_description_content_type':"text/markdown",

    # Find all packages automatically
    'packages': setuptools.find_packages(),

    # The dependencies that are required for the package to run
    'install_requires': install_requires
}

# import cx_Freeze only when needed ---
cx_freeze_commands = {'build_exe', 'bdist_msi', 'bdist_rpm'}
if cx_freeze_commands.intersection(sys.argv):
    import cx_Freeze

    sys.setrecursionlimit(15_000)

    astropy_path = os.path.dirname(os.path.abspath(astropy.__file__))

    directory_table = [("ProgramMenuFolder", "TARGETDIR", "."), ("GraXpert", "ProgramMenuFolder", "GraXpert")]

    msi_data = {
        "Directory": directory_table,
        "ProgId": [("Prog.Id", None, None, "GraXpert is an astronomical image processing program for extracting and removing gradients in the background of your astrophotos", "IconId", None)],
        "Icon": [("IconId", "./img/Icon.ico")],
    }

    msi_summary_data = {"author": "GraXpert Development Team", "comments": "<info@graxpert.com>"}

    bdist_msi_options = {
        "add_to_path": True,
        "data": msi_data,
        "summary_data": msi_summary_data,
        "upgrade_code": "{d0ba2b1d-e18e-42c9-9ded-beb9cadad494}",
        "target_name": "GraXpert",
        "install_icon": "./img/Icon.ico",
    }

    bidst_rpm_options = {"release": release, "vendor": "GraXpert Development Team <info@graxpert.com>", "group": "Unspecified"}

    build_options = {
        "includes": ["astropy.constants.codata2018", "astropy.constants.iau2015", "imageio.plugins.pillow", "skimage.draw.draw", "skimage.exposure.exposure", "skimage.filters._gaussian"],
        "include_files": [
            ["./img", "./lib/img"],
            ["./graxpert-dark-blue.json", "./lib/graxpert-dark-blue.json"],
            ["./locales/", "./lib/locales/"],
            [os.path.join(astropy_path, "units", "format", "generic_parsetab.py"), "./lib/astropy/units/format/generic_parsetab.py"],
            [os.path.join(astropy_path, "units", "format", "generic_lextab.py"), "./lib/astropy/units/format/generic_lextab.py"],
        ],
        "excludes": [],
        "include_msvcr": True,
    }

    base = "Win32GUI" if sys.platform == "win32" else None

    executables = [cx_Freeze.Executable("./graxpert/main.py", base=base, icon="./img/Icon.ico", target_name="GraXpert", shortcut_name="GraXpert {}".format(version), shortcut_dir="GraXpert")]

    # Add the cx_Freeze options to the setup arguments dictionary
    setup_options['executables'] = executables
    setup_options['options'] = {
        "build_exe": build_options,
        "bdist_msi": bdist_msi_options,
        "bdist_rpm": bidst_rpm_options
    }

    cx_Freeze.setup(**setup_options)
else:
    setuptools.setup(**setup_options)
