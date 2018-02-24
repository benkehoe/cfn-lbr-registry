""" Set up a stack of Lambda functions for Lambda-backed custom resources (LBRs)

Copyright 2018 iRobot Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import absolute_import

from . import config

def _get_version():
    import pkg_resources, codecs
    if not pkg_resources.resource_exists(__name__, '_version'):
        return '0.0.0'
    return codecs.decode(pkg_resources.resource_string(__name__, '_version'),'utf-8').strip()
__version__ = _get_version()