from distutils.core import setup

if __name__ == '__main__':
    setup(
        name='svg2sfd',
        description='Convert SVG to FontForge SFD format',
        long_description=open('README.md').read(),
        version='1.0.1',
        author='Kevin Selwyn',
        author_email='kevinselwyn@gmail.com',
        url='https://github.com/kevinselwyn/svg2sfd',
        packages=['svg2sfd'],
        license='GPLv3',
        scripts=['bin/svg2sfd']
    )