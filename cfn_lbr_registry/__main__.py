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
    
    parser.add_argument('action', choices=['deploy', 'package', 'template', 'clean'])
    parser.add_argument('--stack-name')
    
    args, other_args = parser.parse_known_args()
    
    sys.exit(run_make(args.action, args.stack_name, other_args))

if __name__ == '__main__':
    main()