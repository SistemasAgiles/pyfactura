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

CONFIG_FILE = "rece.ini"
HOMO = WSAA.HOMO or WSFEv1.HOMO
import datos


# --- here go your event handlers ---

def on_tipo_doc_change(evt):
    ctrl = evt.target
    value = ""
    if ctrl.value == 80:
        mask = '##-########-#'
    elif ctrl.value == 99:
        mask = '#'
        value = "0"
        #on_nro_doc_change(evt)
    else:
        mask = '########'
    panel['criterios']['nro_doc'].mask = mask
    panel['criterios']['nro_doc'].value = value

def buscar(evt):
    rg1361 = RG1361AFIP()
    listado = mywin['panel']['listado']
    listado.items.clear()

    # obtengo criterio de busqueda:
    tipo_doc = panel['criterios']['tipo_doc'].value
    nro_doc = panel['criterios']['nro_doc'].value
    nombre_cliente = panel['criterios']['nombre_cliente'].value        
    tipo_cbte = panel['criterios']['tipo_cbte'].value
    pto_vta = panel['criterios']['pto_vta'].value
    nro_cbte_desde = panel['criterios']['nro_cbte_desde'].value
    nro_cbte_hasta = panel['criterios']['nro_cbte_hasta'].value
    fecha_cbte_hasta = panel['criterios']['fecha_cbte_hasta'].value
    fecha_cbte_desde = panel['criterios']['fecha_cbte_desde'].value
    cae = panel['criterios']['cae'].value

    for reg in rg1361.Consultar(tipo_cbte=1):
        # convertir a fecha el formato de AFIP
        if not isinstance(reg['fecha_cbte'], datetime.date):
            reg['fecha_cbte'] = datetime.datetime.strptime(reg['fecha_cbte'], "%Y%m%d").date()
        # aplico filtros
        if nro_doc is not None:
            if reg['nro_doc'] != nro_doc and reg['tipo_doc'] != tipo_doc:
                continue                
        if nro_doc is not None:
            if reg['nro_doc'] != nro_doc and reg['tipo_doc'] != tipo_doc:
                continue
        if nombre_cliente and not reg['nombre_cliente'].startswith(nombre_cliente):
            print "filtrado por nombre"
            continue
        if tipo_cbte and reg['tipo_cbte'] != tipo_cbte:
            print "filtrado por tipo_cbte"
            continue
        if pto_vta and reg['punto_vta'] != pto_vta:
            print "filtrado por punto_vta", pto_vta, reg['punto_vta']
            continue
        if nro_cbte_desde and not reg['cbte_nro'] >= nro_cbte_desde:
            print "filtrado por cbte_nro_desde", nro_cbte_desde, reg['cbte_nro']
            continue
        if nro_cbte_hasta and not reg['cbte_nro'] <= nro_cbte_hasta:
            print "filtrado por cbte_nro_hasta", nro_cbte_hasta, reg['cbte_nro']
            continue
        if fecha_cbte_desde and not reg['fecha_cbte'] >= fecha_cbte_desde:
            print "filtrado por fecha_cbte_desde", fecha_cbte_desde, reg['fecha_cbte']
            continue
        if fecha_cbte_hasta and not reg['fecha_cbte'] <= fecha_cbte_hasta:
            print "filtrado por fecha_cbte_hasta", fecha_cbte_hasta, reg['fecha_cbte']
            continue
        if cae and reg['cae'] != cae:
            print "filtrado por cae", cae, reg['cae']
            continue
        # agrego el registro al listado:
        for it in reg['ivas']:
            reg['imp_iva_%d' % it['iva_id']] = it['importe']
        listado.items[reg['id']] = reg


def exportar(evt):
    from pyafipws.formatos.formato_csv import desaplanar, aplanar, escribir
    # adapto los datos al formato de pyrece:
    items = [item.copy() for item in listado.items]
    for item in items:
        item['cbt_numero'] = item['cbte_nro']
        item['fecha_cbte'] = item['fecha_cbte'].strftime("%Y%m%d")
        if not 'tributos' in items:
            item['tributos'] = []
        if not 'ivas' in items:
            item['ivas'] = []
    filas1 = aplanar(items)   
    print filas1
    # elejir nombre de archivo:
    result = gui.save_file(title='Guardar', filename="facturas-exportar.csv",
        wildcard='|'.join(["Archivos CSV (*.csv)|*.csv"]))
    if result:
        filename = result[0]
        escribir(filas1, filename)

def reporte(evt):
    # elejir nombre de archivo:
    result = gui.save_file(title='Guardar', filename="facturas-reporte.html",
        wildcard='|'.join(["Archivos HTML (*.html)|*.html"]))
    if result:
        filename = result[0]
        f = open(filename, "w")
        f.write("<HTML><BODY><TABLE>\n")
        f.write("<TR>\n")
        for col in listado:
            f.write("<TH>%s</TH>\n" % col.text)
        f.write("</TR>\n")
        for it in listado.items:
            f.write("<TR>")
            for col in listado:
                if it[col.name] is None:
                    v = ""
                elif callable(col.represent):
                    v = col.represent(it[col.name])
                elif col.represent:
                    v = col.represent % it[col.name]
                else:
                    v = it[col.name]
                f.write("<TD>%s</TD>" % v)
            f.write("</TR>\n")
        f.write("</TR></TABLE></BODY></HTML>\n")
        f.close()
        

# --- gui2py designer generated code starts ---

with gui.Window(name='consultas', 
                title=u'Aplicativo Facturaci\xf3n Electr\xf3nica', 
                resizable=True, height='636px', left='181', top='52', 
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
            gui.ListColumn(name=u'tipo_cbte', text='Tipo Cbte')
            gui.ListColumn(name=u'punto_vta', text='Punto Venta', 
                           represent="%s", width=50, align="right")
            gui.ListColumn(name=u'cbte_nro', text='Nro Cbte', 
                           represent="%s", align="right")
            gui.ListColumn(name=u'fecha_cbte', text='Fecha Cbte', 
                           align="center")
            gui.ListColumn(name=u'tipo_doc', text='Tipo Doc', width=50)
            gui.ListColumn(name=u'nro_doc', text='Nro Doc', width=100, 
                           represent="%s", align="right")
            gui.ListColumn(name=u'nombre_cliente', text='Cliente', width=150)
            gui.ListColumn(name=u'id_impositivo', text='Cond. IVA', width=50,
                           represent="%s", align="left")
            gui.ListColumn(name=u'imp_total', text='Total', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_op_ex', text='Exento', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_tot_conc', text='No Gravado', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_neto', text='Neto', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_iva_4', text='IVA 10.5%', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_iva_5', text='IVA 21%', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_iva_6', text='IVA 27%', width=100,
                           represent="%.2f", align="right")
            gui.ListColumn(name=u'imp_trib', text='Tributos', width=100,
                           represent="%.2f", align="right")
        gui.Button(label=u'Buscar', name=u'buscar', left='295', top='542', 
                   width='75', default=True, onclick=buscar)
        gui.Label(name='label_22_147', left='12', top='144', 
                  text=u'Resultados:', )
        with gui.Panel(label=u'Criterios de B\xfasqueda:', name='criterios', 
                       height='135', left='6', top='9', width='778', 
                       bgcolor=u'#F9F9F8', fgcolor=u'#4C4C4C', image='', ):
            gui.Label(name='label_182_163', height='21', left='16', top='31', 
                      width='38', text=u'Cliente:', )
            gui.ComboBox(name='tipo_doc', text=u'CF', left='75', top='23', 
                         width='78',  onchange=on_tipo_doc_change,
                         items=[u'CUIT', u'DNI', u'CF', u'Pasaporte'], 
                         selection=3, value=u'CF', )
            gui.TextBox(mask='##-########-#', name='nro_doc', left='164', 
                        top='24', width='110', text=u'20-26756539-3', 
                        value=u'20-26756539-3', )
            gui.Label(name='label_268_164', height='31', left='295', top='28', 
                      width='61', text=u'Nombre:', )
            gui.TextBox(name='nombre_cliente', left='367', top='23', 
                        width='240', value=u'Mariano Reingart', )
            gui.Label(name='label_24_16', height='17', left='12', top='64', 
                      width='146', text=u'Tipo Comprobante:', )
            gui.ComboBox(name=u'tipo_cbte', left='151', top='58', width='170', 
                         items=[u'Factura A', u'Factura B', u'Factura C', ], )
            gui.Label(name='label_356_21_178', height='17', left='262', 
                      top='96', width='20', text=u'Hasta:', )
            gui.TextBox(mask='##', name=u'pto_vta', alignment='right', 
                        left='365', top='59', width='47', value=99, )
            gui.Label(name='label_356_21_155', height='17', left='15', 
                      top='96', width='60', text=u'Fecha:', )
            gui.Label(id=2293, name='label_356_21_178_2293', height='17', 
                      left='329', top='64', width='29', text=u'P.V.:', )
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
                      top='98', width='39', text=u'CAE:', )
            gui.TextBox(name='cae', left='480', top='93', width='274', 
                        text=u'123456789012345',
                        tooltip=u'CAE o c\xf3digo de barras', 
                        value=u'123456789012345', )
            gui.Label(id=1243, name='label_356_21_178_2591_1243', height='17', 
                      left='423', top='63', width='47', text=u'Desde:', )
            gui.Label(id=1343, name='label_356_21_178_1343', height='17', 
                      left='593', top='64', width='44', text=u'Hasta:', )
        gui.Button(label=u'Cargar', name=u'cargar', left='379', top='542', 
                   width='73', fgcolor=u'#4C4C4C', )
        gui.Button(label=u'Exportar', name=u'exportar', left='458', top='542', 
                   width='75', fgcolor=u'#4C4C4C', onclick=exportar)
        gui.Button(id=188, label=u'Reporte', name=u'reporte', left='542', 
                   top='542', width='75', fgcolor=u'#4C4C4C',  onclick=reporte)

# --- gui2py designer generated code ends ---

# obtener referencia a la ventana principal:
mywin = gui.get("consultas")
panel = mywin['panel']
listado = panel['listado']

def main(callback=None):
        global mywin, panel, listado
        # limpiar valores del diseñador:
        panel['criterios']['tipo_doc'].items = datos.TIPO_DOC_MAP
        panel['criterios']['tipo_doc'].value = 80                   # CUIT
        panel['criterios']['nro_doc'].value = None
        panel['criterios']['nombre_cliente'].value = ""
        panel['criterios']['tipo_cbte'].items = datos.TIPO_CBTE_MAP        
        panel['criterios']['tipo_cbte'].value = None
        panel['criterios']['pto_vta'].value = None
        panel['criterios']['nro_cbte_desde'].value = None
        panel['criterios']['nro_cbte_hasta'].value = None
        panel['criterios']['fecha_cbte_hasta'].value = None
        panel['criterios']['fecha_cbte_desde'].value = None
        panel['criterios']['cae'].value = ""
        
        # mostrar la representación más amigable de los códigos de AFIP
        listado['tipo_doc'].represent = lambda x: datos.TIPO_DOC_MAP[x]
        listado['tipo_cbte'].represent = lambda x: datos.TIPO_CBTE_MAP[x]
        listado['fecha_cbte'].represent = lambda x: x.strftime("%x")

        if callback:
            panel['cargar'].onclick = lambda evt: callback(listado.get_selected_items()[0])

        mywin.show()

if __name__ == "__main__":
    main()
    gui.main_loop()

