# Changes

### 2022-12-28 - v1.0.5

* Added support for Python 3.10 and 3.11
* Fixed bug with initialization of _auto_type_cast field
* Fixed SyntaxError bug when parsing strings while casting is on
* Updated copyright and code ownership notes

### 2022-05-16 - v1.0.4

* Added prevention for instantiating ENV class
* Improved test coverage
* Added support for Python 3.9

### 2022-01-13 - v1.0.3

* ENV now is a context manager (enabling auto type cast within)
* Fixed a bug of setting _auto_type_cast
* Added missed py35 configuration in tox.ini
* Fixed .gitignore about coverage files
* Fixed tests (cleanup)
* Added test for ENV as context manager


### 2020-02-15 - v1.0.2

* Added support for operator "in"
* Added support for dir(ENV)
* Implemented str(ENV) and repr(ENV)
* Added support for iterating ENV
* Increased test coverage on Python 3 to 97%

### 2020-02-29 - v1.0.1

* Bugfixes and some refactoring
