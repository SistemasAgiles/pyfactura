#!/usr/bin/python
# -*- coding: utf-8 -*-

"Aplicativo Factura Electronica Libre"

from __future__ import with_statement   # for python 2.5 compatibility

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2015- Mariano Reingart"
__license__ = "LGPL 3.0"
__version__ = "0.7b"

# Documentación: http://www.sistemasagiles.com.ar/trac/wiki/PyFactura

import datetime     # base imports, used by some controls and event handlers
import decimal
import os
import time
import traceback
import sys
from ConfigParser import SafeConfigParser

import gui          # import gui2py package (shortcuts)

from pyafipws.padron import PadronAFIP
from pyafipws.rg1361 import RG1361AFIP
from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1
from pyafipws.pyfepdf import FEPDF
from pyafipws.pyemail import PyEmail

# set default locale to handle correctly numeric format (maskedit):
import wx, locale
if sys.platform == "win32":
    locale.setlocale(locale.LC_ALL, 'Spanish_Argentina.1252')
elif sys.platform == "linux2":
    locale.setlocale(locale.LC_ALL, 'es_AR.utf8')
loc = wx.Locale(wx.LANGUAGE_DEFAULT, wx.LOCALE_LOAD_DEFAULT)


# --- gui2py designer generated code starts ---

with gui.Window(name='mywin', 
                title=u'Aplicativo Facturaci\xf3n Electr\xf3nica', 
                resizable=True, height='571px', left='181', top='52', 
                width='794px', image='', ):
    with gui.MenuBar(name='menubar_83_155', ):
        with gui.Menu(name='menu_114', ):
            gui.MenuItemSeparator(name='menuitemseparator_130', )
    gui.StatusBar(name='statusbar_15_91', 
                  text=u'Servicio Web Factura Electr\xf3nica mercado interno (WSFEv1)', )
    with gui.Panel(label=u'', name='panel', image='', ):
        gui.Image(name='image_507_571', height='36', left='17', top='535', 
                  width='238', filename='sistemas-agiles.png', )
        gui.Image(name='image_33_540', height='50', left='665', top='532', 
                  width='100', filename='logo-pyafipws.png', )
        with gui.ListView(name='listado', height='353', left='7', top='168', 
                          width='775', item_count=0, sort_column=-1, ):
            gui.ListColumn(name=u'tipo_cbte', text="tipo cbte")
            gui.ListColumn(name=u'pto_vta', text="pto vta")
            gui.ListColumn(name=u'nro_cbte', text="nro cbte")
            gui.ListColumn(name=u'fecha_cbte', text="fecha cbte")
            gui.ListColumn(name=u'tipo_doc', text="tipo doc")
            gui.ListColumn(name=u'nro_doc', text="nro doc")
            gui.ListColumn(name=u'cliente', text="cliente")
            gui.ListColumn(name=u'imp_op_ex', text="imp op ex")
            gui.ListColumn(name=u'imp_tot_conc', text="imp conc")
            gui.ListColumn(name=u'imp_neto', text="imp neto")
            gui.ListColumn(name=u'imp_iva', text="imp iva")
            gui.ListColumn(name=u'imp_trib', text="imp trib")
            gui.ListColumn(name=u'imp_total', text="imp tot")
        gui.Button(label=u'Buscar', name=u'buscar', left='350', top='542', 
                   width='75', fgcolor=u'#4C4C4C', )
        gui.Label(name='label_22_147', left='12', top='144', 
                  text=u'Resultados:', )
        with gui.Panel(label=u'Criterios de B\xfasqueda:', name='cliente', 
                       height='135', left='6', top='9', width='778', 
                       bgcolor=u'#F9F9F8', fgcolor=u'#4C4C4C', image='', ):
            gui.Label(name='label_182_163', height='21', left='16', top='31', 
                      width='38', text=u'Cliente:', )
            gui.ComboBox(name='tipo_doc', text=u'CF', left='75', top='23', 
                         width='78', 
                         items=[u'CUIT', u'DNI', u'CI Extranjera', u'CF', u'Pasaporte'], 
                         selection=3, value=u'CF', )
            gui.TextBox(mask='##-########-#', name='nro_doc', left='164', 
                        top='24', width='110', text=u'20-26756539-3', 
                        value=u'20-26756539-3', )
            gui.Label(name='label_268_164', height='31', left='295', top='28', 
                      width='61', text=u'Nombre:', )
            gui.TextBox(name='nombre', left='367', top='22', width='240', 
                        text=u'Mariano Reingart', value=u'Mariano Reingart', )
            gui.Label(name='label_24_16', height='17', left='12', top='66', 
                      width='146', text=u'Tipo Comprobante:', )
            gui.ComboBox(name=u'tipo_cbte', left='151', top='58', width='170', 
                         items=[u'Factura A', u'Nota de D\xe9bito A', u'Nota de Cr\xe9dito A', u'Recibo A', u'Factura B', u'Nota de D\xe9bito B', u'Nota de Cr\xe9dito B', u'Recibo B', u'Factura C', u'Nota de D\xe9bito C', u'Nota de Cr\xe9dito C', u'Recibo C'], )
            gui.Label(name='label_356_21_178', height='17', left='262', 
                      top='96', width='20', text=u'Hasta:', )
            gui.TextBox(mask='##', name=u'pto_vta', alignment='right', 
                        left='365', top='59', width='47', value=99, )
            gui.Label(name='label_356_21_155', height='17', left='15', 
                      top='96', width='60', text=u'Fecha:', )
            gui.Label(id=2293, name='label_356_21_178_2293', height='17', 
                      left='329', top='65', width='29', text=u'P.V.:', )
            gui.Label(id=2591, name='label_356_21_178_2591', height='17', 
                      left='72', top='96', width='47', text=u'Desde:', )
            gui.TextBox(id=2794, mask='date', name=u'fecha_cbte_hasta', 
                        height='29', left='308', top='91', width='122', 
                        bgcolor=u'#F2F1F0', fgcolor=u'#4C4C4C', 
                        value=datetime.date(2014, 5, 27), )
            gui.TextBox(id=290, mask='date', name=u'fecha_cbte_desde', 
                        height='29', left='131', top='91', width='122', 
                        bgcolor=u'#F2F1F0', fgcolor=u'#4C4C4C', 
                        value=datetime.date(2014, 5, 27), )
            gui.TextBox(id=2361, mask='########', name=u'nro_cbte_hasta', 
                        alignment='right', height='27', left='654', top='59', 
                        width='92', bgcolor=u'#FFFFFF', fgcolor=u'#000000', 
                        value=12345678, )
            gui.TextBox(mask='########', name=u'nro_cbte_desde', 
                        alignment='right', height='27', left='481', top='59', 
                        width='92', bgcolor=u'#FFFFFF', fgcolor=u'#000000', 
                        value=12345678, )
            gui.Label(name='label_26_372_2499_2861', height='17', left='439', 
                      top='100', width='39', text=u'CAE:', )
            gui.TextBox(name='cae', left='480', top='93', width='274', 
                        editable=False, text=u'123456789012345', 
                        tooltip=u'CAE o c\xf3digo de barras', 
                        value=u'123456789012345', )
            gui.Label(id=1243, name='label_356_21_178_2591_1243', height='17', 
                      left='423', top='62', width='47', text=u'Desde:', )
            gui.Label(id=1343, name='label_356_21_178_1343', height='17', 
                      left='593', top='63', width='44', text=u'Hasta:', )
        gui.Button(label=u'Reimprimir', name=u'reimprimir', left='430', 
                   top='542', width='93', fgcolor=u'#4C4C4C', )
        gui.Button(label=u'Exportar', name=u'exportar', left='528', top='542', 
                   width='75', fgcolor=u'#4C4C4C', )

# --- gui2py designer generated code ends ---


# obtener referencia a la ventana principal:
mywin = gui.get("mywin")

if __name__ == "__main__":
        mywin.show()
        rg1361 = RG1361AFIP()
        listado = mywin['panel']['listado']
        listado.items.clear()
        for reg in rg1361.Consultar(tipo_cbte=1):
            listado.items[reg['id']] = dict([(k, unicode(v)) for k,v in reg.items()])
        gui.main_loop()
