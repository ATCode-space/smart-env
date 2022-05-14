"""
MIT License

Copyright (c) 2020 Alex Sokolov

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

import abc

from six import with_metaclass


__all__ = ('DecodeError', 'EncodeError', 'EnvException', 'UnsupportedAction')


class EnvException(with_metaclass(abc.ABCMeta, Exception)):
    """Base class for Environment exceptions"""


class DecodeError(EnvException):
    """Error while trying to decode value with type checking"""


class EncodeError(EnvException):
    """Error while trying to encode value"""


class UnsupportedAction(EnvException):
    """An exception class for unsupported actions or operations"""

    def __init__(self, *args):
        if args:
            self._action = args[0]

    def __str__(self):
        return ("Unsupported action: {}".format(self._action)
                if hasattr(self, '_action')
                else "This action is not supported")
