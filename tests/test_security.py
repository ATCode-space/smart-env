"""
MIT License

Copyright (c) 2026 ATCode Solutions inc.

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

import unittest

from smart_env.decoders import CollectionDecoder
from smart_env.decoders import JSONDecoder
from smart_env.exceptions import DecodeError


__all__ = ('CollectionDecoderSecurityTestCase', 'JSONDecoderSecurityTestCase')


class CollectionDecoderSecurityTestCase(unittest.TestCase):
    """Test cases for security fixes in CollectionDecoder"""

    def test_normal_list_parsing(self):
        """Test that normal list inputs still work"""
        result = CollectionDecoder.decode("[1, 2, 3]")
        self.assertEqual(result, [1, 2, 3])

    def test_normal_dict_parsing(self):
        """Test that normal dict inputs still work"""
        result = CollectionDecoder.decode("{'a': 1, 'b': 2}")
        self.assertEqual(result, {'a': 1, 'b': 2})

    def test_normal_tuple_parsing(self):
        """Test that normal tuple inputs still work"""
        result = CollectionDecoder.decode("(1, 2, 3)")
        self.assertEqual(result, (1, 2, 3))

    def test_nested_structure_within_limits(self):
        """Test that nested structures within limits work"""
        result = CollectionDecoder.decode("[[1, 2], [3, 4]]")
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_nested_dict_within_limits(self):
        """Test that nested dicts within limits work"""
        result = CollectionDecoder.decode("{'outer': {'inner': {'value': 123}}}")
        self.assertEqual(result, {'outer': {'inner': {'value': 123}}})

    def test_empty_structures(self):
        """Test that empty structures are handled correctly"""
        self.assertEqual(CollectionDecoder.decode("[]"), [])
        self.assertEqual(CollectionDecoder.decode("{}"), {})
        self.assertEqual(CollectionDecoder.decode("()"), ())

    def test_structure_at_maximum_depth(self):
        """Test that structure at exactly maximum depth (20 levels) works"""
        nested_20 = "[" * 20 + "1" + "]" * 20
        result = CollectionDecoder.decode(nested_20)
        self.assertIsNotNone(result)

    def test_oversized_input_rejected(self):
        """Test that oversized input (>1MB) is rejected"""
        large_input = "[" + "1,"*500000 + "1]"
        with self.assertRaises(DecodeError):
            CollectionDecoder.decode(large_input)

    def test_deeply_nested_structure_rejected(self):
        """Test that deeply nested structures (>20 levels) are rejected"""
        nested = "[" * 50 + "1" + "]" * 50
        with self.assertRaises(DecodeError):
            CollectionDecoder.decode(nested)

    def test_too_many_items_rejected(self):
        """Test that structures with too many items (>10,000) are rejected"""
        large_list = str(list(range(15000)))
        with self.assertRaises(DecodeError):
            CollectionDecoder.decode(large_list)

    def test_nested_dict_with_many_keys_rejected(self):
        """Test that dicts with too many total items are rejected"""
        large_dict = str({str(i): i for i in range(11000)})
        with self.assertRaises(DecodeError):
            CollectionDecoder.decode(large_dict)

    def test_moderate_nesting_allowed(self):
        """Test that moderate nesting (10 levels) is allowed"""
        nested_10 = "[" * 10 + "1" + "]" * 10
        result = CollectionDecoder.decode(nested_10)
        self.assertIsNotNone(result)

    def test_moderate_item_count_allowed(self):
        """Test that moderate item counts (5,000) are allowed"""
        moderate_list = str(list(range(5000)))
        result = CollectionDecoder.decode(moderate_list)
        self.assertEqual(len(result), 5000)

    def test_complex_valid_structure(self):
        """Test that complex but valid structures work"""
        complex_struct = "{'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}], 'count': 2}"
        result = CollectionDecoder.decode(complex_struct)
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['users']), 2)


class JSONDecoderSecurityTestCase(unittest.TestCase):
    """Test cases for security fixes in JSONDecoder"""

    def test_normal_json_int(self):
        """Test that normal integer JSON inputs still work"""
        result = JSONDecoder.decode("42")
        self.assertEqual(result, 42)

    def test_normal_json_string(self):
        """Test that normal string JSON inputs still work"""
        result = JSONDecoder.decode('"hello"')
        self.assertEqual(result, "hello")

    def test_normal_json_list(self):
        """Test that normal list JSON inputs still work"""
        result = JSONDecoder.decode('[1, 2, 3]')
        self.assertEqual(result, [1, 2, 3])

    def test_normal_json_dict(self):
        """Test that normal dict JSON inputs still work"""
        result = JSONDecoder.decode('{"a": 1, "b": 2}')
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_json_null(self):
        """Test that null is correctly decoded"""
        result = JSONDecoder.decode('null')
        self.assertIsNone(result)

    def test_json_boolean(self):
        """Test that booleans are correctly decoded"""
        self.assertEqual(JSONDecoder.decode('true'), True)
        self.assertEqual(JSONDecoder.decode('false'), False)

    def test_nested_json_within_limits(self):
        """Test that nested JSON within limits works"""
        result = JSONDecoder.decode('{"outer": {"inner": {"value": 123}}}')
        self.assertEqual(result, {"outer": {"inner": {"value": 123}}})

    def test_json_array_within_limits(self):
        """Test that arrays within limits work"""
        result = JSONDecoder.decode('[[1, 2], [3, 4]]')
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_empty_json_structures(self):
        """Test that empty JSON structures are handled correctly"""
        self.assertEqual(JSONDecoder.decode('[]'), [])
        self.assertEqual(JSONDecoder.decode('{}'), {})

    def test_json_at_maximum_depth(self):
        """Test that JSON at exactly maximum depth (20 levels) works"""
        nested = '{"a":'*19 + '{"value": 1}' + '}'*19
        result = JSONDecoder.decode(nested)
        self.assertIsNotNone(result)

    def test_oversized_json_input_rejected(self):
        """Test that oversized JSON input (>1MB) is rejected"""
        large_input = '[' + ','.join(str(i) for i in range(200000)) + ']'
        with self.assertRaises(DecodeError):
            JSONDecoder.decode(large_input)

    def test_deeply_nested_json_rejected(self):
        """Test that deeply nested JSON (>20 levels) is rejected"""
        nested = '{"a":'*50 + '1' + '}'*50
        with self.assertRaises(DecodeError):
            JSONDecoder.decode(nested)

    def test_deeply_nested_json_array_rejected(self):
        """Test that deeply nested JSON arrays (>20 levels) are rejected"""
        nested = '['*50 + '1' + ']'*50
        with self.assertRaises(DecodeError):
            JSONDecoder.decode(nested)

    def test_too_many_json_items_rejected(self):
        """Test that JSON with too many items (>10,000) is rejected"""
        large_list = '[' + ','.join(str(i) for i in range(15000)) + ']'
        with self.assertRaises(DecodeError):
            JSONDecoder.decode(large_list)

    def test_json_dict_with_many_keys_rejected(self):
        """Test that JSON dicts with too many keys are rejected"""
        large_dict = '{' + ','.join('"{0}": {0}'.format(i) for i in range(11000)) + '}'
        with self.assertRaises(DecodeError):
            JSONDecoder.decode(large_dict)

    def test_moderate_json_nesting_allowed(self):
        """Test that moderate JSON nesting (10 levels) is allowed"""
        nested = '{"a":'*10 + '1' + '}'*10
        result = JSONDecoder.decode(nested)
        self.assertIsNotNone(result)

    def test_moderate_json_item_count_allowed(self):
        """Test that moderate JSON item counts (5,000) are allowed"""
        moderate_list = '[' + ','.join(str(i) for i in range(5000)) + ']'
        result = JSONDecoder.decode(moderate_list)
        self.assertEqual(len(result), 5000)

    def test_complex_valid_json_structure(self):
        """Test that complex but valid JSON structures work"""
        complex_json = '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}], "count": 2}'
        result = JSONDecoder.decode(complex_json)
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['users']), 2)
        self.assertEqual(result['users'][0]['name'], 'Alice')
