from setuptools import setup

from windows_wifi_manager import __version__ as version

setup(
    name='windows-wifi-manager',
    version=version,
    packages=['windows_wifi_manager'],
    url='https://github.com/NihalAgarwal/Windows-Wi-Fi-Manager',
    license='MIT',
    author='Nihal Agarwal',
    author_email='nihal.agarwal.1426@gmail.com',
    description='Know the saved WiFi details and add WiFi profile using a'
                'simple graphical interface in windows.',
    long_description=''.join(open('README.md', encoding='utf-8').readlines()),
    long_description_content_type='text/markdown',
    keywords=['gui', 'wifi', 'netsh', 'Wi-Fi'],
    include_package_data=True,
    install_requires=['appdirs==1.4.3', 'lxml==4.4.2', 'requests==2.22.0'],
    python_requires='>=3',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Microsoft :: Windows',
    ],
    entry_points={
        'console_scripts': [
            'windowswifimanager=windows_wifi_manager.__main__:main',
            'windows-wifi-manager=windows_wifi_manager.__main__:main'
        ],
    },
)
