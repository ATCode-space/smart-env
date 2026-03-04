"""
MIT License

Copyright (c) 2022 ATCode Solutions inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import itertools
import json
import os
import threading

from six import with_metaclass

from .decoders import SUPPORTED_DECODERS
from .exceptions import DecodeError
from .exceptions import EncodeError
from .exceptions import UnsupportedAction
from .iterator import EnvIterator


__all__ = ('ENV',)


class ClassProperty(type):
    """Metaclass for enabling properties on class"""

    __immutable_fields__ = ('enable_automatic_type_cast',
                            'disable_automatic_type_cast',
                            '_env_lock',
                            '_context_stack')
    __mutable_fields__ = ('_auto_type_cast', '_type_hints')

    __own_fields__ = __immutable_fields__ + __mutable_fields__
    
    _env_lock = threading.RLock()
    _context_stack = threading.local()
    _type_hints = {}

    @staticmethod
    def __decode(value):
        """Decodes data from environment variable if possible,
        or return the source value otherwise"""
        if value is None:  # Variable was not set in environment
            return value

        if not isinstance(value, str):
            raise TypeError("Value {} must be str, not {}".format(value,
                                                                  type(value)))

        for decoder in SUPPORTED_DECODERS:
            try:
                return decoder.decode(value)
            except DecodeError:
                pass
        else:
            return value

    def __encode(cls, value):
        """Encodes data as text"""

        if isinstance(value, str):
            return value

        for decoder in SUPPORTED_DECODERS:
            try:
                return decoder.encode(value)
            except EncodeError:
                pass
        else:
            raise ValueError("'{}' value is not serializable".format(value))

    def __getattr__(cls, item):
        if item in cls.__own_fields__:
            return cls.__dict__[item]
        
        with cls._env_lock:
            value = os.environ.get(item, None)
            
            if cls._auto_type_cast:
                decoded = cls.__decode(value)
                
                if item in cls._type_hints:
                    expected_type = cls._type_hints[item]
                    if decoded is not None and not isinstance(decoded, expected_type):
                        raise TypeError(
                            "Variable '{}' expected {}, got {}".format(
                                item, expected_type.__name__, type(decoded).__name__
                            )
                        )
                
                return decoded
            
            return value

    def __delattr__(cls, item):
        """Unset environment variable"""

        if item in cls.__own_fields__:
            raise AttributeError(
                "Own attribute '{}' cannot be deleted".format(item)
            )

        with cls._env_lock:
            try:
                del os.environ[item]
            except KeyError:
                pass

    def __setattr__(cls, key, value):
        """Sets a new or updates existing environment variable"""

        if key in cls.__immutable_fields__:
            raise AttributeError(
                "Own attribute '{}' cannot be reinitialized".format(key))

        if key in cls.__mutable_fields__:
            if value is None:
                raise AttributeError(
                    "Protected attribute '{}' cannot be unset".format(key)
                )

            super(ClassProperty, cls).__setattr__(key, value)
            return

        if value is None:
            delattr(cls, key)
            return

        with cls._env_lock:
            os.environ[key] = cls.__encode(value)

    def __contains__(cls, item):
        """Check if environment variable is set"""

        if item in cls.__own_fields__:
            return False

        with cls._env_lock:
            return os.environ.get(item, None) is not None

    def __str__(cls):
        """Returns a string representation of os.environ object.

        In this case, values are not decoded from their string equivalents
        in the OS environment. For convenience, json.dumps() is used.
        """
        with cls._env_lock:
            return json.dumps(dict(os.environ))

    def __repr__(cls):
        """Returns a string with sorted list of environment variables"""
        with cls._env_lock:
            return str(sorted(os.environ.keys()))

    def __iter__(self):
        with cls._env_lock:
            return EnvIterator(sorted(os.environ.keys()))

    def __dir__(self):
        """Returns list of environment variables + own fields"""
        with cls._env_lock:
            return sorted(
                itertools.chain(
                    self.__own_fields__,
                    os.environ.keys()
                )
            )

    def __enter__(self):
        """Enables automatic type cast"""
        if not hasattr(self._context_stack, 'stack'):
            self._context_stack.stack = []
        
        self._context_stack.stack.append(self._auto_type_cast)
        self._auto_type_cast = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._context_stack, 'stack') and self._context_stack.stack:
            self._auto_type_cast = self._context_stack.stack.pop()
        return False


class ENV(with_metaclass(ClassProperty)):
    """Environment wrapper"""

    _auto_type_cast = False

    @classmethod
    def enable_automatic_type_cast(cls):
        """Enable automatic type cast"""
        cls._auto_type_cast = True

    @classmethod
    def disable_automatic_type_cast(cls):
        """Disable automatic type cast"""
        cls._auto_type_cast = False

    @classmethod
    def is_auto_type_cast(cls):
        """Shows if automatic type cast is enabled"""
        return cls._auto_type_cast

    @classmethod
    def set_type_hints(cls, **hints):
        """Register expected types for environment variables
        
        When type hints are set, the decoder will validate that decoded values
        match the expected type. If the type doesn't match, TypeError is raised.
        
        Args:
            **hints: Variable names mapped to expected Python types
        
        Example:
            ENV.set_type_hints(
                PORT=int,
                DEBUG=bool,
                ADMIN_USER=str,
                DATABASE_CONFIG=dict,
                ALLOWED_HOSTS=list
            )
            
            ENV.enable_automatic_type_cast()
            port = ENV.PORT  # Guaranteed to be int or raises TypeError
            debug = ENV.DEBUG  # Guaranteed to be bool or raises TypeError
        """
        cls._type_hints.update(hints)

    @classmethod
    def clear_type_hints(cls):
        """Clear all registered type hints"""
        cls._type_hints.clear()

    @classmethod
    def get_type_hints(cls):
        """Get currently registered type hints"""
        return dict(cls._type_hints)

    def __init__(self):
        raise UnsupportedAction('Instantiating of ENV substance')
