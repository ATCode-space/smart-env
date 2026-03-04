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

import abc
import ast
import json

from six import with_metaclass

from .exceptions import DecodeError
from .exceptions import EncodeError


__all__ = ('IDecoder',
           'JSONDecoder',
           'BooleanDecoder',
           'CollectionDecoder',
           'SUPPORTED_DECODERS')


class IDecoder(with_metaclass(abc.ABCMeta)):
    """Interface for defining all decoder classes"""

    @classmethod
    @abc.abstractmethod
    def decode(cls, value):
        """Decode value using specified algorithm"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def encode(cls, value):
        """Encode value using specified algorithm"""
        raise NotImplementedError


class JSONDecoder(IDecoder):
    """JSON-based decoder"""

    @classmethod
    def decode(cls, value):
        """Try to decode value assuming it's a JSON-like string

        Supported values:
            - int
            - float
            - str
            - list (of JSON-compatible values)
            - dict (with double quotes used for strings)
            - "null" string (means None)
            - "true" string (means True)
            - "false" string (means False)
        """

        try:
            return json.loads(value)
        except (TypeError, ValueError):
            raise DecodeError

    @classmethod
    def encode(cls, value):
        """Encodes JSON-compatible object as string

        Supported values:
            - int
            - float
            - str
            - list (of JSON-compatible values)
            - dict (with JSON-compatible values)
            - bool
        """
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            raise EncodeError


class BooleanDecoder(IDecoder):
    """Decoder for boolean-like values"""

    @classmethod
    def decode(cls, value):
        """Try to decode value assuming it's boolean-like string

        Supported values:
            - "True"
            - "False"
            - "true"
            - "false"
        """

        if value in ("True", "true"):
            return True
        if value in ("False", "false"):
            return False
        raise DecodeError

    @classmethod
    def encode(cls, value):
        """Encodes boolean value into string representation

        Supported values:
            - True (bool)
            - False (bool)

        For convenience, it converts boolean constants into
        JSON-compatible string representations:

        True -> true
        False -> false
        """
        try:
            if not isinstance(value, bool):
                raise TypeError(
                    "Expected boolean value, got '{}' instead".format(
                        type(value)
                    )
                )
            return json.dumps(value)
        except (TypeError, ValueError):
            raise EncodeError


class CollectionDecoder(IDecoder):
    """Decoder for collection-like values"""

    MAX_INPUT_SIZE = 1024 * 1024  # 1MB
    MAX_NESTING_DEPTH = 20
    MAX_TOTAL_ITEMS = 10000

    @classmethod
    def _validate_input_size(cls, value):
        """Validate input size to prevent memory exhaustion attacks"""
        if len(value) > cls.MAX_INPUT_SIZE:
            raise DecodeError(
                "Input too large: {} bytes (max: {})".format(
                    len(value), cls.MAX_INPUT_SIZE
                )
            )

    @classmethod
    def _count_nesting_depth(cls, node, current_depth=0):
        """Recursively count the maximum nesting depth of AST node
        
        This prevents DoS attacks via deeply nested structures.
        """
        if current_depth > cls.MAX_NESTING_DEPTH:
            raise DecodeError(
                "Nesting too deep: exceeds maximum depth of {}".format(
                    cls.MAX_NESTING_DEPTH
                )
            )

        if isinstance(node, (ast.List, ast.Tuple)):
            if not node.elts:
                return current_depth
            return max(
                cls._count_nesting_depth(child, current_depth + 1)
                for child in node.elts
            )
        elif isinstance(node, ast.Set):
            if not node.elts:
                return current_depth
            return max(
                cls._count_nesting_depth(child, current_depth + 1)
                for child in node.elts
            )
        elif isinstance(node, ast.Dict):
            max_depth = current_depth
            for key_node in node.keys:
                max_depth = max(
                    max_depth,
                    cls._count_nesting_depth(key_node, current_depth + 1)
                )
            for value_node in node.values:
                max_depth = max(
                    max_depth,
                    cls._count_nesting_depth(value_node, current_depth + 1)
                )
            return max_depth
        else:
            return current_depth

    @classmethod
    def _validate_result_size(cls, obj):
        """Validate the total number of items in parsed structure
        
        This provides defense-in-depth by checking result size even after
        successful parsing, preventing memory exhaustion from large structures.
        """
        def count_items(obj, count=0):
            if count > cls.MAX_TOTAL_ITEMS:
                raise DecodeError(
                    "Result too large: exceeds {} items".format(
                        cls.MAX_TOTAL_ITEMS
                    )
                )
            
            if isinstance(obj, dict):
                count += len(obj)
                for key, value in obj.items():
                    count = count_items(key, count)
                    count = count_items(value, count)
            elif isinstance(obj, (list, tuple, set, frozenset)):
                count += len(obj)
                for item in obj:
                    count = count_items(item, count)
            else:
                count += 1
            return count
        
        count_items(obj)

    @classmethod
    def decode(cls, value):
        """Try to decode value assuming it's list-like string

        Supported values:
            - list-like string
            - set-like string
            - tuple-like string
            - dict-like string
            
        Security: Input is validated for size and nesting depth before parsing
        to prevent resource exhaustion attacks.
        """
        try:
            cls._validate_input_size(value)
            tree = ast.parse(value, mode='eval')
            cls._count_nesting_depth(tree.body)
            result = ast.literal_eval(value)
            cls._validate_result_size(result)
            
            return result
        except (ValueError, SyntaxError, RecursionError):
            raise DecodeError
        except DecodeError:
            # Re-raise our own validation errors
            raise

    @classmethod
    def encode(cls, value):
        """Encodes collections into JSON-compatible string

        Supported values:
            - dict
            - set
            - frozenset
            - tuple
            - list

        In case of set and frozenset, they're first converted
        into list for JSON compatibility.
        """

        try:
            if isinstance(value, (set, frozenset)):
                value = list(value)
            return json.dumps(value)
        except TypeError:
            raise EncodeError


SUPPORTED_DECODERS = (
    JSONDecoder,
    BooleanDecoder,
    CollectionDecoder,
)
