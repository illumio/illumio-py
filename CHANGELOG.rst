Changelog
=========

Version 0.8.4 (2022-05-27)
-------------

* add CRUD operation functions for pairing profile objects to the PCE interface
* add pairing profile tests
* improve mock test scaffolding
* change IllumioEnum to metaclass and replace has_value with contains builtin

Version 0.8.3 (2022-05-16)
-------------

* add retry logic to PCE requests session

Version 0.8.2 (2022-03-14)
-------------

* add tests for PCE URL parsing
* improve documentation
    * add README and CONTRIBUTING docs
    * add copyright and license header to all modules
    * add docstrings for PolicyComputeEngine functions, improve URL parsing
* add UnmodifiableObject class for PolicyVersion (create only)
* change IllumioObject to inherit from Reference
* update parsing in traffic query blocks to simplify builder
* raise IllumioException if invalid protocol name is passed to BaseService subclass
* deprecate convert_protocol function in favour of baking proto conversion into service post_init
* add PolicyObjectType enum
* add parse_url function to improve handling of PCE url arg
* default to draft version of rulesets when creating rules

Version 0.8.1 (2022-03-09)
-------------

* overhaul complex type decoding by centralizing logic in JsonObject
* update test cases
* add changelog

Version 0.8.0 (2022-03-03)
-------------

* add deprecation decorator
* deprecate get_by_name in favor of broader collection get logic
* add get_ruleset function
* add create_ip_list function
* add ip list tests
* overhaul tests to improve mock logic
* remove duplication in async job calls

Version 0.7.3 (2022-02-22)
-------------

* fix get_workloads to correctly use max_results
* update_workload_enforcement_modes can now batch process any number of requested workloads
* fix LabelSet internal type as workload repr can use full Label objects
* improve logic for traffic analysis timestamp conversion
* add classifiers to setup config
* fix license copyright

Version 0.7.2 (2022-01-25)
-------------

* update dependencies to remove dataclass req for python versions above 3.6
* fix exception thrown when HTTP error responses don't contain content-type header

Version 0.7.1 (2022-01-07)
-------------

* update core json decode functionality to allow for arbitrary parameters not represented in the dataclass definitions for forward compatibility
* change builder function to properly represent traffic query blocks for src/dst/services
* fix representation of selectively_enforced_services param and add num_enforcement_boundaries

Version 0.7.0 (2022-01-06)
-------------

* add basic test shells for rules/rulesets
* fix type of service binding workload param
* change json encode default behaviour to improve recursive encoding in cases with complex nested objects
* change connection check to use /health endpoint

Version 0.6.5 (2021-12-20)
-------------

* improve get_workloads logic and add check_connection function
* fix traffic flow state error message and incorrect value for timeout state

Version 0.6.4 (2021-11-29)
-------------

* add get_workloads function and refactor how default header/params are set

Version 0.6.3 (2021-11-21)
-------------

* update Rule builder to allow multiple ingress_service input types

Version 0.6.2 (2021-11-20)
-------------

* add set_proxies function to set request session proxies

Version 0.6.1 (2021-11-19)
-------------

* allow unix timestamps as valid inputs for start/end dates in traffic analysis queries
* fix x_by reference nesting

Version 0.6.0 (2021-11-18)
-------------

* add Rule object builder function and improve HREF regex
* add helper function to convert draft href to active
* move base classes to jsonutils module to avoid circular refs
* fix get_by_name function and improve request error logic
* ignore DS_Store files on mac

Version 0.5.5 (2021-11-18)
-------------

* remove get_by_name duplication and simplify calls by working around active/draft duplicate results
* add submodule shortcuts back to root imports
* add update_workload_enforcement_modes function

Version 0.5.4 (2021-11-17)
-------------

* add enforcement boundary PCE functions and fix issues with get_by_name and create_service_binding functions
* update rule ingress_services decoding to correctly identify between Service/ServicePort
* add draft and active policy version constants
* improve create_service_binding logic and add create_service_bindings function for batch creation

Version 0.5.3 (2021-11-17)
-------------

* separate out base rule class for use with enforcement boundaries
* flesh out Service object structure
* fix IP list convenience functions
* move caps property to ModifiableObject class; add missing type decoding to Rules

Version 0.5.2 (2021-11-16)
-------------

* add Reference class for simple href representations in more complex objects
* add IP list convenience methods and create_rule PCE function
* add actor submodule to rules module exports

Version 0.5.1 (2021-11-16)
-------------

* fix test imports
* move secpolicy to package root and remove root shortcuts for submodule imports; clean up project imports

Version 0.5.0 (2021-11-16)
-------------

* flesh out rules and rulesets and add create_ruleset PCE function
* add SecurityPrincipal policy object skeleton

Version 0.4.2 (2021-11-16)
-------------

* remove UserObject in favour of the more generic ModifiableObject as workloads and other objects can be created/modified by non-user entities (e.g. agents)

Version 0.4.1 (2021-11-16)
-------------

* add missing fields needed to decode workload objects; implement get_workload PCE function
* remove custom fields for workload open_service_ports objects in favour of new class
* change Network class to IllumioObject subtype
* add VisibilityLevel enum

Version 0.4.0 (2021-11-16)
-------------

* fix policy provisioning and add PolicyVersion object
* flesh out IPList class and add get_ip_list PCE function
* move common external_data_set and external_data_reference params into IllumioObject base class
* move modification params to UserObject
* add missing fields for ServiceBinding and PortOverride classes
* add create_service_binding function and dependent objects
* fix PCE functions to send objects rather than JSON strings
* provide more detailed error messages in case of API exceptions
* remove name requirement for virtual service init; change apply_to default to None
* fix broken build function and add error case
* add policy provision API call and dependent objects
* add LabelSet object type
* move enums to constants util module and improve validation logic

Version 0.3.0 (2021-11-11)
-------------

* create more descriptive modules and move submodules from policyobjects
* change core object structure to use IllumioObject base class
* move JsonObject class to jsonutils
* standardize formatting for complex type decoding
* use IllumioEncoder rather than directly calling to_json

Version 0.2.0 (2021-11-10)
-------------

* add async traffic flow function and builder function for traffic queries
* flesh out traffic analysis flow objects and add decode test
* flesh out workload object definition and subclasses
* add containercluster and vulnerabilityreport module stubs
* define extendable base enum class for package-wide use
* add Network and Vulnerability stubs for workloads
* add params to Service to accommodate Workload open_service_ports object definition
* add delete_type param to base PolicyObject
* add _validate function called from post_init in base JsonObject class
* add virtualserver stub module
* shift date validation to the API so we don't have to worry about ISO format conversion (fromisoformat isn't introduced until 3.9) or timezones
* simplify creation of query objects
* add validation for start and end dates
* add query_name field for async queries
* add traffic analysis query structure dataclasses
* add workload and iplist module stubs
* use UserObject base class and simplify init logic for simple reference cases
* combine service objects into single module and simplify class structures
* add User object and separate UserObject base class for user-created policy objects
* use socket lib function rather than custom protocol enum for conversion to int
* move JsonObject base class into policyobject module
* add pytest cache to gitignore

Version 0.1.1 (2021-11-07)
-------------

* improve virtual service tests
* overhaul policy object structures and improve json encoding/decoding
* remove api module

Version 0.1.0 (2021-11-04)
-------------

* initial commit
