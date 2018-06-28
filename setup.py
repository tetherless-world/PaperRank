from distutils.core import setup

setup(
    name='PaperRank',
    author='Rukmal Weerawarana',
    author_email='rukmal.weerawarana@gmail.com',
    description='Computing PageRank for Academic literature citation graphs.',
    version='0.1dev',
    license='MIT License',
    long_description=open('README.md').read(),
    package_dir={
        'PaperRank': 'PaperRank'
    }
)