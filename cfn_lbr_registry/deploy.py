import subprocess
import pkg_resources
import sys

def main(args=None):
    args = args or sys.argv[1:]
    with pkg_resources.resource_stream(__name__, 'Makefile') as fp:
        sys.exit(subprocess.call(['make', '-f', '-', 'LBR_PYTHON_VERSION={0}.{1}'.format(*sys.version_info)] + args, stdin=fp))

if __name__ == '__main__':
    main()