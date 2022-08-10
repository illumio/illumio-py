.. illumio-py documentation master file, created by
   sphinx-quickstart on Fri Mar 11 17:22:37 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Illumio PCE Python API Client
=============================

Release v\ |version| (:ref:`Install Guide <install>`)

.. image:: https://img.shields.io/pypi/pyversions/illumio.svg
    :target: https://pypi.org/project/illumio/
    :alt: Python Version Support Badge

The **illumio** python library exposes Policy Compute Engine API endpoints
through an easy-to-use interface.

**illumio** is compatible with Illumio Core PCE versions 21.2 and up.

----------------------------------

Getting started is simple::

   >>> from illumio import PolicyComputeEngine
   >>> pce = PolicyComputeEngine('my.pce.com', port='8443', org_id='12')
   >>> pce.set_credentials('<API_KEY>', '<API_SECRET>')
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

Already have **illumio** installed and ready to get started?
Check out the :ref:`Quickstart Guide <quickstart>`.

User Guide
----------

These guides provide an introduction to using the **illumio** library,
common use-cases, and show how to manage the various policy objects and
functions in the PCE.

.. toctree::
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
   :maxdepth: 2

   api

Contributing
------------

.. toctree::
   :maxdepth: 1

   dev/changelog

* :ref:`genindex`
