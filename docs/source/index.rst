.. illumio-py documentation master file, created by
   sphinx-quickstart on Fri Mar 11 17:22:37 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: illumio

Illumio Core Python API Client
==============================

.. image:: https://img.shields.io/github/v/release/illumio/illumio-py?label=Latest%20Release
   :target: https://github.com/illumio/illumio-py/releases/latest
   :alt: Latest Release Badge

.. image:: https://img.shields.io/pypi/pyversions/illumio.svg
    :target: https://pypi.org/project/illumio/
    :alt: Python Version Support Badge

The **illumio** python library exposes Policy Compute Engine API endpoints
through an easy-to-use interface.

**illumio** is compatible with Illumio Core PCE versions 21.2 and up.

Already have **illumio** installed and ready to get started?
Check out the :ref:`Quickstart Guide <quickstart>`.

If not, see the :ref:`Install Guide <install>`, or just run::

   $ python -m pip install illumio

----------------------------------

Take advantage of the Illumio PCE's powerful APIs in just a few lines of code::

   >>> from illumio import PolicyComputeEngine
   >>> pce = PolicyComputeEngine('my.pce.com', port='443', org_id='1')
   >>> pce.set_credentials('api_key', 'api_secret')
   >>> workloads = pce.workloads.get(
   ...     params={
   ...         'managed': True,
   ...         'enforcement_mode': 'visibility_only'
   ...     }
   ... )
   >>> workloads
   [
      Workload(
         href='/orgs/12/workloads/c754a713-2bde-4427-af1f-bff145be509b',
         ...
      ),
      ...
   ]

User Guide
----------

These guides provide an introduction to using the **illumio** library,
common use-cases, and show how to manage the various policy objects and
functions in the PCE.

.. toctree::
   :caption: User Guide
   :maxdepth: 2

   user/install
   user/quickstart
   user/usecases
   user/advanced

API Documentation
-----------------

Full API documentation on classes, functions, and methods that make up the
`illumio` library can be found here.

.. toctree::
   :caption: illumio API
   :maxdepth: 2

   api

Development
-----------

.. toctree::
   :caption: Development
   :maxdepth: 1

   dev/changelog

* :ref:`genindex`
