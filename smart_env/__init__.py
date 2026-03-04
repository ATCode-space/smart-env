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

import sys
import warnings

if sys.version_info[0] == 2:
    warnings.warn(
        "You are using smart-env with Python 2.7, which reached end-of-life on "
        "January 1, 2020. Python 2.7 has known security vulnerabilities that will "
        "never be fixed. It is strongly recommended to upgrade to Python 3.11 or later "
        "to ensure your application remains secure. For more information, visit: "
        "https://www.python.org/doc/sunset-python-2/",
        DeprecationWarning,
        stacklevel=2
    )

from .env import ENV

__all__ = ('ENV',)
