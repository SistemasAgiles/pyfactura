#!/usr/bin/python
# -*- coding: latin-1 -*-

# Para hacer el ejecutable:
#       python setup.py py2exe 
#

"Creador de instalador para PyFactura"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2014 Mariano Reingart"

factura = __import__("factura")
__version__ = factura.__version__

from distutils.core import setup
import glob
import os
import sys


# parametros para setup:
kwargs = {}

long_desc = "Aplicativo visual para generación Facturas Electrónicas AFIP"
            
            
data_files = [
    (".", ["licencia.txt", "sistemas-agiles.png", "logo-pyafipws.png"]),
    ("conf", ["conf/rece.ini", "conf/geotrust.crt", "conf/afip_ca_info.crt", ]),
    #(".", ["reingart.crt", "reingart.key", ]),
    ("cache", glob.glob("cache/*")),
    ]

HOMO = False

# build a one-click-installer for windows:
if 'py2exe' in sys.argv:
    import py2exe
    from nsis import build_installer, Target

    # includes for py2exe
    includes=['email.generator', 'email.iterators', 'email.message', 'email.utils',  'email.mime.text', 'email.mime.application', 'email.mime.multipart']

    # optional modules:
    # required modules for shelve support (not detected by py2exe by default):
    for mod in ['socks', 'dbhash', 'gdbm', 'dbm', 'dumbdbm', 'anydbm']:
        try:
            __import__(mod)
            includes.append(mod)
        except ImportError:
            pass 

    # don't pull in all this MFC stuff used by the makepy UI.
    excludes=["pywin", "pywin.dialogs", "pywin.dialogs.list", "win32ui",
              "Tkconstants","Tkinter","tcl",
              "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk",
             ]

    # basic options for py2exe
    opts = { 
        'py2exe': {
            'includes': includes,
            'optimize': 0,
            'excludes': excludes,
            'dll_excludes': ["mswsock.dll", "powrprof.dll", "KERNELBASE.dll", 
                         "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
                         "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
                         "API-MS-Win-Security-Base-L1-1-0.dll"
                         ],
            'skip_archive': True,
            }
        }

    desc = "Instalador PyAfipWs"
    kwargs['com_server'] = []
    kwargs['console'] = []
    kwargs['windows'] = []

    # add 32bit or 64bit tag to the installer name
    import platform
    __version__ += "-" + platform.architecture()[0]
    
    # visual application
    # find pythoncard resources, to add as 'data_files'
    pycard_resources=[]
    for filename in os.listdir('.'):
        if filename.find('.rsrc.')>-1:
            pycard_resources+=[filename]

    kwargs['console'] += [
        Target(module=factura, script="factura.pyw", dest_base="factura_consola"),
        ]
    kwargs['windows'] += [
        Target(module=factura, script='factura.pyw'),
        ]
    data_files += [
        ("plantillas", ["plantillas/logo.png", "plantillas/factura.csv", "plantillas/recibo.csv",]),
        ("cache", glob.glob("cache/*")),
        #("datos", ["datos/facturas.csv", "datos/facturas.json", "datos/facturas.txt", ])
        (".", [
                "sistemas-agiles.png", "logo-pyafipws.png", "reingart.key", "reingart.crt",
                "pyafipws/padron.db", 
                ])
        ]
    data_files.append((".", pycard_resources))

    # add certification authorities (newer versions of httplib2)
    try:
        import httplib2
        if httplib2.__version__ >= "0.9":
            data_files += [("httplib2", 
                [os.path.join(os.path.dirname(httplib2.__file__), "cacerts.txt")])]
    except ImportError:
        pass

    # custom installer:
    kwargs['cmdclass'] = {"py2exe": build_installer}

    if sys.version_info > (2, 7):
        # add "Microsoft Visual C++ 2008 Redistributable Package (x86)"
        if os.path.exists(r"c:\Program Files\Mercurial"):
            data_files += [(
                ".", glob.glob(r'c:\Program Files\Mercurial\msvc*.dll') +
                     glob.glob(r'c:\Program Files\Mercurial\Microsoft.VC90.CRT.manifest'),
                )]
        sys.path.insert(0, r"C:\Python27\Lib\site-packages\pythonwin")
        data_files += [(
            ".", glob.glob(r'C:\Python27\Lib\site-packages\pythonwin\mfc*.*') +
                 glob.glob(r'C:\Python27\Lib\site-packages\pythonwin\Microsoft.VC90.MFC.manifest'),
            )]
    else:
        data_files += [(".", [
            "C:\python25\Lib\site-packages\wx-2.8-msw-unicode\wx\MSVCP71.dll",
            "C:\python25\MSVCR71.dll",
            "C:\python25\lib\site-packages\wx-2.8-msw-unicode\wx\gdiplus.dll",
            ])]

    # agrego tag de homologación (testing - modo evaluación):
    __version__ += "-homo" if HOMO else "-full"
    
else:
    desc = "Paquete PyFactura"
    kwargs['package_dir'] = {'pyafipws': '.'}
    kwargs['packages'] = ['pyafipws']
    opts = {}


setup(name="PyFactura",
      version=__version__,
      description=desc,
      long_description=long_desc,
      author="Mariano Reingart",
      author_email="reingart@gmail.com",
      url="https://code.google.com/p/pyafipws/" if 'register' in sys.argv 
          else "http://www.sistemasagiles.com.ar",
      license="GNU GPL v3",
      options=opts,
      data_files=data_files,
            classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Financial and Insurance Industry",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.5",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            #"Programming Language :: Python :: 3.2",
            "Operating System :: OS Independent",
            "Operating System :: Microsoft :: Windows",
            "Natural Language :: Spanish",
            "Topic :: Office/Business :: Financial :: Point-Of-Sale",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Object Brokering",
      ],
      keywords="webservice electronic invoice pdf traceability",
      **kwargs
      )

