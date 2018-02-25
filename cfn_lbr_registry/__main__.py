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

from . import parameters

def run_make(action, args, other_args):
    make_args = []
    make_args += parameters.get_make_args(action, args, other_args)
    with pkg_resources.resource_stream(__name__, 'Makefile') as fp:
        return subprocess.call(['make', '-f', '-'] + make_args + [action], stdin=fp)

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('action', choices=['deploy', 'package', 'template', 'clean']) #TODO: insert
    parameters.add_parameter_args(parser)
    
    args, other_args = parser.parse_known_args()
    
    sys.exit(run_make(args.action, args, other_args))

if __name__ == '__main__':
    main()