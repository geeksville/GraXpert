import os
import sys
import re
import setuptools

author_name = "GraXpert Development Team"
author_email = "info@graxpert.com"
author_full = f"{author_name} <{author_email}>"

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
    'license':"GPL-3.0",

    'url':"https://graxpert.com",
    'project_urls': {
        "Source Code":"https://github.com/geeksville/GraXpert" # FIXME change when merged upstream
    },

    'author':author_name,
    'author_email':author_email,

    'python_requires':">=3.11",

    # Name the executable for pip/pipx installs
    'entry_points':{
        'console_scripts': [
            'graxpert = graxpert.main:main',
        ],
    },

    # A long description that will be displayed on PyPI
    'long_description':long_description,
    'long_description_content_type':"text/markdown",

    # Find all packages automatically (used by cx_Freeze and setuptools)
    'packages': setuptools.find_packages(),

    # The dependencies that are required for the package to run
    'install_requires': install_requires,

    'extras_require': {
        "rocm": ["onnxruntime-rocm>=1.22.2"],
        "openvino": ["onnxruntime-openvino>=1.22.0"],
    },

    'classifiers': [
        # Development Status: Choose the one that fits best.
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",

        # Audience & Topic: Who is it for and what does it do?
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Multimedia :: Graphics :: Editors",

        # Supported Python versions: List all versions you test against.
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # Operating System: Specify which OSs are supported.
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",

        # Environment: This clarifies it's a graphical application.
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Environment :: X11 Applications",
        
        # Natural Language
        "Natural Language :: English",
        "Natural Language :: German"
    ]
}

# import cx_Freeze only when needed
cx_freeze_commands = {'build_exe', 'bdist_msi', 'bdist_rpm', 'bdist_appimage', 'bdist_deb', 'bdist_mac', 'install' }
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

    msi_summary_data = {"author": author_name, "comments": author_email}

    bdist_msi_options = {
        "add_to_path": True,
        "data": msi_data,
        "summary_data": msi_summary_data,
        "upgrade_code": "{d0ba2b1d-e18e-42c9-9ded-beb9cadad494}",
        "target_name": "GraXpert",
        "install_icon": "./img/Icon.ico",
    }

    # Not yet used, possibly never used if AppImage is sufficient
    bdist_rpm_options = {
        "release": release,
        "vendor": author_full,
        "group": "Unspecified"
    }

    bdist_appimage_options = {
        "target_name": "graxpert"
    }

    bdist_deb_options = {
        "depends": [
            "libice6",
            "libsm6",
            "x11-common"
        ]
    }

    bdist_mac_options = {
        # Not yet used
    }

    build_options = {
        "includes": ["astropy.constants.codata2018", "astropy.constants.iau2015", "imageio.plugins.pillow", "skimage.draw.draw", "skimage.exposure.exposure", "skimage.filters._gaussian"],
        "include_files": [
            ["./img", "./lib/img"],
            ["./graxpert-dark-blue.json", "./lib/graxpert-dark-blue.json"],
            ["./locales/", "./lib/locales/"],
            [os.path.join(astropy_path, "units", "format", "generic_parsetab.py"), "./lib/astropy/units/format/generic_parsetab.py"],
            [os.path.join(astropy_path, "units", "format", "generic_lextab.py"), "./lib/astropy/units/format/generic_lextab.py"],
        ],
        "excludes": [
            "setuptools",
            "twine"
        ],
        "include_msvcr": True
    }

    # console allows passing in command line
    base = "Win32GUI" if sys.platform == "win32" else "console"

    executables = [cx_Freeze.Executable("./graxpert/main.py", base=base,
                                        icon="./img/Icon", # leave off extension so it will be autocorrected for any OS
                                        target_name="graxpert",
                                        shortcut_name="GraXpert {}".format(version), shortcut_dir="GraXpert")]

    # Add the cx_Freeze options to the setup arguments dictionary
    setup_options['executables'] = executables
    setup_options['options'] = {
        "build_exe": build_options,
        "bdist_msi": bdist_msi_options,
        "bdist_rpm": bdist_rpm_options,
        "bdist_appimage": bdist_appimage_options,
        "bdist_deb": bdist_deb_options,
        "bdist_mac": bdist_mac_options
    }

    cx_Freeze.setup(**setup_options)
else:
    setuptools.setup(**setup_options)
