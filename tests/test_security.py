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

import threading
import time
import unittest

from smart_env import ENV
from smart_env.decoders import CollectionDecoder
from smart_env.decoders import JSONDecoder
from smart_env.exceptions import DecodeError


__all__ = ('CollectionDecoderSecurityTestCase', 'JSONDecoderSecurityTestCase',
           'ThreadSafetyTestCase', 'ContextManagerTestCase')


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


class ThreadSafetyTestCase(unittest.TestCase):
    """Test cases for thread safety in ENV operations"""

    def setUp(self):
        if 'TEST_THREAD_VAR' in ENV:
            del ENV.TEST_THREAD_VAR
        if 'TEST_COUNTER' in ENV:
            del ENV.TEST_COUNTER

    def tearDown(self):
        if 'TEST_THREAD_VAR' in ENV:
            del ENV.TEST_THREAD_VAR
        if 'TEST_COUNTER' in ENV:
            del ENV.TEST_COUNTER

    def test_concurrent_reads(self):
        """Test that concurrent reads don't cause race conditions"""
        ENV.TEST_THREAD_VAR = 'test_value'
        results = []
        errors = []

        def reader():
            try:
                for _ in range(100):
                    value = ENV.TEST_THREAD_VAR
                    results.append(value)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=reader) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertTrue(all(v == 'test_value' for v in results))

    def test_concurrent_writes(self):
        """Test that concurrent writes are thread-safe"""
        errors = []

        def writer(thread_id):
            try:
                for i in range(50):
                    ENV.TEST_THREAD_VAR = 'thread_{}_value_{}'.format(thread_id, i)
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(ENV.TEST_THREAD_VAR)

    def test_concurrent_read_write(self):
        """Test that concurrent reads and writes don't corrupt state"""
        ENV.TEST_THREAD_VAR = 'initial'
        errors = []
        read_values = []

        def reader():
            try:
                for _ in range(50):
                    value = ENV.TEST_THREAD_VAR
                    if value is not None:
                        read_values.append(value)
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)

        def writer():
            try:
                for i in range(50):
                    ENV.TEST_THREAD_VAR = 'value_{}'.format(i)
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)

        threads = []
        threads.extend([threading.Thread(target=reader) for _ in range(3)])
        threads.extend([threading.Thread(target=writer) for _ in range(2)])

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertTrue(len(read_values) > 0)

    def test_concurrent_delete_operations(self):
        """Test that concurrent delete operations are safe"""
        errors = []

        def deleter():
            try:
                for i in range(50):
                    ENV.TEST_THREAD_VAR = 'value_{}'.format(i)
                    del ENV.TEST_THREAD_VAR
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=deleter) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)

    def test_concurrent_contains_check(self):
        """Test that concurrent 'in' checks are thread-safe"""
        ENV.TEST_THREAD_VAR = 'value'
        results = []
        errors = []

        def checker():
            try:
                for _ in range(100):
                    result = 'TEST_THREAD_VAR' in ENV
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=checker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertTrue(len(results) > 0)


class ContextManagerTestCase(unittest.TestCase):
    """Test cases for ENV context manager safety"""

    def setUp(self):
        ENV.disable_automatic_type_cast()
        if 'TEST_VAR' in ENV:
            del ENV.TEST_VAR

    def tearDown(self):
        ENV.disable_automatic_type_cast()
        if 'TEST_VAR' in ENV:
            del ENV.TEST_VAR

    def test_basic_context_manager(self):
        """Test basic context manager usage"""
        self.assertFalse(ENV.is_auto_type_cast())
        
        with ENV:
            self.assertTrue(ENV.is_auto_type_cast())
        
        self.assertFalse(ENV.is_auto_type_cast())

    def test_nested_context_managers(self):
        """Test that nested context managers work correctly"""
        self.assertFalse(ENV.is_auto_type_cast())
        
        with ENV:
            self.assertTrue(ENV.is_auto_type_cast())
            
            with ENV:
                self.assertTrue(ENV.is_auto_type_cast())
            
            self.assertTrue(ENV.is_auto_type_cast())
        
        self.assertFalse(ENV.is_auto_type_cast())

    def test_context_manager_with_enabled_type_cast(self):
        """Test context manager when type cast is already enabled"""
        ENV.enable_automatic_type_cast()
        self.assertTrue(ENV.is_auto_type_cast())
        
        with ENV:
            self.assertTrue(ENV.is_auto_type_cast())
        
        self.assertTrue(ENV.is_auto_type_cast())
        ENV.disable_automatic_type_cast()

    def test_context_manager_exception_handling(self):
        """Test that exceptions don't corrupt context manager state"""
        self.assertFalse(ENV.is_auto_type_cast())
        
        try:
            with ENV:
                self.assertTrue(ENV.is_auto_type_cast())
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        self.assertFalse(ENV.is_auto_type_cast())

    def test_nested_context_with_exception(self):
        """Test nested contexts with exception in inner context"""
        self.assertFalse(ENV.is_auto_type_cast())
        
        with ENV:
            self.assertTrue(ENV.is_auto_type_cast())
            
            try:
                with ENV:
                    self.assertTrue(ENV.is_auto_type_cast())
                    raise RuntimeError("Inner exception")
            except RuntimeError:
                pass
            
            self.assertTrue(ENV.is_auto_type_cast())
        
        self.assertFalse(ENV.is_auto_type_cast())

    def test_context_manager_thread_safety(self):
        """Test that context managers work correctly across threads"""
        results = []
        errors = []

        def thread_worker():
            try:
                initial_state = ENV.is_auto_type_cast()
                
                with ENV:
                    inside_state = ENV.is_auto_type_cast()
                    time.sleep(0.01)
                
                final_state = ENV.is_auto_type_cast()
                results.append({
                    'initial': initial_state,
                    'inside': inside_state,
                    'final': final_state
                })
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=thread_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 10)
        
        for result in results:
            self.assertTrue(result['inside'])
            self.assertEqual(result['initial'], result['final'])

    def test_deeply_nested_contexts(self):
        """Test many levels of nested contexts"""
        self.assertFalse(ENV.is_auto_type_cast())
        
        depth = 10
        for i in range(depth):
            ENV.__enter__()
            self.assertTrue(ENV.is_auto_type_cast())
        
        for i in range(depth):
            ENV.__exit__(None, None, None)
        
        self.assertFalse(ENV.is_auto_type_cast())

    def test_context_manager_returns_self(self):
        """Test that __enter__ returns self for 'as' syntax"""
        with ENV as env:
            self.assertIs(env, ENV)
