# How to contribute

## GitHub workflow  

Suggested contribution workflow (feature branching):

1. Create your own fork of the project
2. Create a new branch on the fork
3. Develop the change in your local branch
4. When you're ready to create a pull request, merge the upstream main branch into your local main
5. Merge any changes to the local main branch into your feature branch
6. Merge your feature branch into local main
7. Submit a pull request from your local main branch  

### Open a Pull Request  

Pull requests please follow the standard github PR process.  

### Sign the CLA  

When submitting a pull request, you will be prompted to to sign the Illumio [Contributor License Agreement](CLA.md). The signature is then stored remotely so the process only needs to be completed once.  

## Testing  

Make sure to add unit tests to cover any new functionality. When making changes to existing code, add any necessary regression tests, and/or change existing tests where needed.  

Run tests against all supported python versions with ```make test```. Tests are run using the `tox` library. It's recommended to install python environments with [`pyenv`](https://github.com/pyenv/pyenv) and install the [`tox-pyenv` library](https://pypi.org/project/tox-pyenv/) to test against multiple versions at once.  

## Documentation  

### Project documentation  

* Update the [README](../README.md) if the feature or change adds new functionality to the client  
* Update the [CHANGELOG](../CHANGELOG.rst)  

### Code documentation  

This project follows the [Google python style guide](https://google.github.io/styleguide/pyguide.html) - please make sure to document interface functions and any complex functionality.  
