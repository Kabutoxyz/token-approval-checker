from setuptools import setup, find_packages
setup(
    name='token-approval-checker',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['requests>=2.28', 'rich>=13.0', 'click>=8.0'],
    entry_points={'console_scripts': ['approval-check=approvals.cli:main']},
    author='Kabutoxyz',
    description='Check and manage token approvals for security',
    python_requires='>=3.9',
)
