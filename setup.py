import ast
import os
import os.path
import sys
try:
    import urllib2
except ImportError:
    from urllib import request as urllib2
try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

from setuptools import setup


table_url = 'http://www.currency-iso.org/dam/downloads/table_a1.xml'


def download_table(table_url, table_filename):
    response = urllib2.urlopen(table_url)
    try:
        f = open(table_filename, 'w')
        try:
            f.write(response.read())
        finally:
            f.close()
    finally:
        response.close()


table_filename = os.path.join(os.path.dirname(__file__),
                              'iso4217', 'table_a1.xml')
download_flag = os.environ.get('ISO4217_DOWNLOAD')
download = (
    (
        download_flag not in('0', 'false', 'no') and
        not os.path.isfile(table_filename)
    ) or download_flag in ('1', 'true', 'yes')
)
if download:
    download_table(table_url, table_filename)


def get_install_requires():
    install_requires = ['setuptools']
    if 'bdist_wheel' not in sys.argv and sys.version_info < (3, 4):
        install_requires.append('enum34')
    return install_requires


def get_extras_require():
    """Generate conditional requirements with environ marker."""
    for pyversion in '2.5', '2.6', '2.7', '3.2', '3.3':
        yield ':python_version==' + repr(pyversion), ['enum34']


def get_version():
    module_path = os.path.join(os.path.dirname(__file__),
                               'iso4217', '__init__.py')
    module_file = open(module_path)
    try:
        module_code = module_file.read()
    finally:
        module_file.close()
    tree = ast.parse(module_code, module_path)
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, = node.targets
        if isinstance(target, ast.Name) and target.id == '__version_prefix__':
            version = '.'.join(str(e.n) for e in node.value.elts)
            break
    else:
        raise ValueError('could not find __version_prefix__')
    try:
        raw_xml = etree.parse(table_filename)
    except IOError:
        return version
    version += '.' + raw_xml.getroot().attrib['Pblshd'].replace('-', '')
    return version


setup(
    name='iso4217',
    version=get_version(),
    author='Hong Minhee',
    author_email='hongminhee' '@' 'member.fsf.org',
    license='Public Domain',
    packages=['iso4217'],
    package_data={'iso4217': ['table_a1.xml']},
    install_requires=get_install_requires(),
    extras_require=dict(get_extras_require()),
    keywords='internationalization i18n currency iso4217',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Internationalization',
    ]
)