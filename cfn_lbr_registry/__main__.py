"""Main script for cfn-lbr-registry

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

import subprocess
import pkg_resources
import sys
import argparse

def run_make(action='deploy', stack_name=None, make_args=[]):
    with pkg_resources.resource_stream(__name__, 'Makefile') as fp:
        args = ['make', '-f', '-', 'LBR_PYTHON_VERSION={0}.{1}'.format(*sys.version_info), action]
        if stack_name:
            args.append('STACK_NAME={}'.format(stack_name))
        return subprocess.call(args + make_args, stdin=fp)

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('action', choices=['deploy', 'package', 'template', 'clean']) #TODO: insert
    parser.add_argument('--stack-name')
    
    args, other_args = parser.parse_known_args()
    
    sys.exit(run_make(args.action, args.stack_name, other_args))

if __name__ == '__main__':
    main()