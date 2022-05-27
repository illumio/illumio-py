# illumio  

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?color=orange)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/illumio/illumio-py?label=Latest%20Release)](https://github.com/illumio/illumio-py/releases/latest)

Illumio Policy Compute Engine REST client for python 3. Exposes PCE API endpoints as functions through a simple interface.  

Compatible with Illumio Core PCE version 21.2+.  

The main entrypoint for the client is the `PolicyComputeEngine` class:  

```python
>>> from illumio import PolicyComputeEngine
>>> pce = PolicyComputeEngine('my.pce.com', port='8443', org_id='12')
>>> pce.set_credentials('<API_KEY>', '<API_SECRET>')
>>> workloads = pce.get_workloads(
...     params={
...         'managed': True,
...         'enforcement_mode': 'visibility_only'
...     }
... )
>>> workloads
[
    Workload(href='/orgs/12/workloads/c754a713-2bde-4427-af1f-bff145be509b', ...),
    ...
]
```

For more information on the Illumio APIs, see the [REST API guide](https://docs.illumio.com/core/21.5/Content/LandingPages/Guides/rest-api.htm) and the [API reference](https://docs.illumio.com/core/21.5/API-Reference/index.html) for your version of Illumio Core.  

## Installation  

The `illumio` library is now [available on pypi](https://pypi.org/project/illumio/)!  

```sh
$ python -m pip install illumio
```

To build and install from source  

```sh
$ git clone git@github.com:illumio/illumio-py.git
$ cd illumio-py
$ make
```

## Support  

The `illumio` package is released and distributed as open source software subject to the included [LICENSE](https://github.com/illumio/illumio-py/blob/main/LICENSE). Illumio has no obligation or responsibility related to the package with respect to support, maintenance, availability, security or otherwise. Please read the entire [LICENSE](https://github.com/illumio/illumio-py/blob/main/LICENSE) for additional information regarding the permissions and limitations. Support is offered on a best-effort basis through the [Illumio app integrations team](mailto:app-integrations@illumio.com) and project contributors.  

## Contributing  

See the project's [CONTRIBUTING](https://github.com/illumio/illumio-py/blob/main/.github/CONTRIBUTING.md) document for details.  

## License  

Copyright 2022 Illumio  

```
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
