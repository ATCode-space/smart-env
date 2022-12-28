# SmartEnv - OS Environment Wrapper Library

A flexible, easy-to-use library for managing environment variables in your Python script.

## Why yet another one?

This library comes with a few major points to use it:

* It is easy and intuitive (see examples)
* It's compatible with Python 2 (can be useful in old large systems)
* Continuous support of the library

## Getting started

This library is pretty easy to use:

```python
from smart_env import ENV

print(ENV.HOME)  # Equals print(os.environ['HOME'])

# Apply type cast wherever you need by using ENV as a context manager

with ENV:
   # assuming you set env variable MYVAR to "True" in shell
   my_var = ENV.MY_VAR  # Equals boolean True
# And here type cast is automatically disabled
my_second_var = ENV.MY_VAR  # Equals 'True' as string

# Enabling automatic type cast for all the further commands
ENV.enable_automatic_type_cast()

# assuming you set env variable MYVAR to "True" in shell
my_var = ENV.MY_VAR  # Equals boolean True

ENV.NEW_VAR = 100  # Sets a new environment variable

# Disabling automatic type cast
ENV.enable_automatic_type_cast()
```

## How to use

In a few words, the logic is next:
1. You can store a lot of serialized values in Environment variables and then deserialize them on fly using ENV class.
2. Each environment variable can be accessed as an attribute of ENV class:
    ```python
    ENV.<variable_name>
    ```
3. The internal decoding mechanism is based on **json** and **ast** packages. That means, 
you can parse even some JSON-incompatible values (for example, with single quotes used for defining strings).

### Installing

Simply run

```
pip install smart-env
```

## Running the tests

This library contains tests written using *unittest* module, so just run in the project directory

```
python -m unittest
```

It's possible to run tests using Tox as well:

```bash
tox -e <env>
```

or just

```bash
tox
```

Tests coverage is one of the important goals of this project.
For now coverage is next:
- For Python 2.7: 99%
- For Python 3.x: 97%

Supported environments:

- py27
- py35
- py36
- py37
- py38
- py39
- py310
- coverage (using Python 3)
- coverage27 (using Python 2.7)
- pep8 (style checking)

## Restrictions

1. Old versions of Python in both generations (e.g. 2.6, 3.4, etc) will never be supported. 
However, you always can implement such support in your forks.

2. Parsing set() objects is not working in Python 2. See [this](https://bugs.python.org/issue10091) for details.


## Authors

* **Olek Sokolov** - *Author* - [Albartash](https://github.com/AlBartash)

## Contacts

* Telegram channel with updates: [@bart_tools](http://t.me/bart_tools)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
