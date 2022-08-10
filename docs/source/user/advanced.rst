.. _advanced:

.. currentmodule:: illumio

Advanced Usage
==============

Proxy Settings
--------------

If you need to use a proxy to communicate with the PCE, HTTP/S proxies can be
configured using the :meth:`set_proxies <PolicyComputeEngine.set_proxies>`
function::

    >>> pce.set_proxies(
    ...     http_proxy='http://my.proxyserver.com:8080',
    ...     https_proxy='http://my.proxyserver.com:8080'
    ... )

If not set in the session, the ``requests`` library will pull proxy settings
from environment variables, see the ``requests`` `proxy documentation <https://requests.readthedocs.io/en/latest/user/advanced/#proxies>`_
for details.

Asynchronous Collection Requests
--------------------------------

:meth:`get_async <PolicyComputeEngine._PCEObjectAPI.get_async>`


the ``get_async`` call abstracts the job poll-wait loop from the caller
in order to provide a simpler synchronous interface. If your implementation
requires control over the poll requests (if you have a strict job timeout,
for example), you will need to use ``post`` and ``get``
