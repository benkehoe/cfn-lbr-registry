import subprocess
import pkg_resources
import sys
import argparse

def run_make(action='deploy', make_args=[]):
    with pkg_resources.resource_stream(__name__, 'Makefile') as fp:
        return subprocess.call(['make', '-f', '-', 'LBR_PYTHON_VERSION={0}.{1}'.format(*sys.version_info), action] + make_args, stdin=fp)

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('action', choices=['deploy', 'package', 'template', 'clean'])
    
    args, other_args = parser.parse_known_args()
    
    sys.exit(run_make(args.action, other_args))

if __name__ == '__main__':
    main()