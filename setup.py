from setuptools import setup

setup(
	name="molly-plot",
	version='0.0.1',
    
    # metadata
    author='Felipe Jimenez-Ibarra',
    author_email='felipejimenezibarra@gmail.com',
    
    python_requires='>3.8',
    install_requires = ['astropy==5', 
                        'cmd2==2.4',
                        'trm.molly @ http://github.com/WarwickAstro/trm-molly/tarball/master#egg=trm.molly-1'], #external packages as dependencies
    
   
   
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': ['mplot=mollyplot.__main__:main'
        ]
    },
)



