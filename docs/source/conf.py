# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

sys.path.insert(0, os.path.abspath("../.."))

from illumio import PCE_APIS, BULK_CHANGE_LIMIT

# -- Project information -----------------------------------------------------

project = 'illumio'
copyright = '2022, Illumio'
author = 'Illumio'

# The full version, including alpha/beta/rc tags
release = version('illumio')

# Simple x.y.z version number
version = '.'.join(release.split('.')[:3])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'enum_tools.autoenum',
    'sphinx.ext.viewcode'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'tests'
]

add_module_names = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'
html_theme_options = {
    'navigation_with_keys': True,
    'sidebar_hide_name': True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Include custom CSS styles.
html_css_files = ['custom.css']

# Use the Illumio logo in place of the library name.
html_logo = 'illumio_logo.svg'

# Hide the Made with Sphinx footer.
html_show_sphinx = False

# -- Autodoc Options ---------------------------------------------------------

# Exclude documentation for __new__ by default.
autodoc_default_options = {
    'exclude-members': '__init__, __new__'
}

# Override the default alphabetical ordering for member variables and methods,
# instead display them in source definition order.
autodoc_member_order = 'bysource'

# Show type hints in the description rather than the signature.
autodoc_typehints = 'description'

# Don't show class signature with the class name.
autodoc_class_signature = 'separated'

# Don't inherit docstrings from parent classes.
autodoc_inherit_docstrings = False

# -- Custom definitions ------------------------------------------------------

# Construct the dynamic API list to embed into the API documentation page.
apis_docstring = ''
for name, api in sorted(PCE_APIS.items()):
    classpath = '{}.{}'.format(
        api.object_class.__module__,
        api.object_class.__qualname__
    )
    apis_docstring += """
    :class:`{} <{}>` |br|""".format(name, classpath)

# Adds the rst string to the bottom of every page. We use this to define
# common and dynamic substitutions.
rst_epilog = """
.. |br| raw:: html

    <br/>
.. |APIList| replace:: {}
.. |BulkChangeLimit| replace:: {}
""".format(apis_docstring, BULK_CHANGE_LIMIT)
