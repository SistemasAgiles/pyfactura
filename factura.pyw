#!/usr/bin/python
# -*- coding: utf-8 -*-

"Aplicativo Factura Electronica Libre"

from __future__ import with_statement   # for python 2.5 compatibility

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2014- Mariano Reingart"
__license__ = "LGPL 3.0"

# images were taken from Pythoncard's proof and widgets demos
# for more complete examples, see each control module

import datetime     # base imports, used by some controls and event handlers
import decimal
import time

import gui          # import gui2py package (shortcuts)

# set default locale to handle correctly numeric format (maskedit):
import wx, locale
#locale.setlocale(locale.LC_ALL, u'es_ES.UTF-8')
#loc = wx.Locale(wx.LANGUAGE_DEFAULT, wx.LOCALE_LOAD_DEFAULT)

# --- here go your event handlers ---



# --- gui2py designer generated code starts ---

with gui.Window(name='mywin', 
                title=u'Aplicativo Facturaci\xf3n Electr\xf3nica', 
                resizable=True, height='457px', left='181', top='52', 
                width='653px', bgcolor=u'#F9F9F8', fgcolor=u'#4C4C4C', 
                image='', ):
    with gui.MenuBar(name='menubar_83_155', fgcolor=u'#000000', ):
        with gui.Menu(name='menu_114', fgcolor=u'#000000', ):
            gui.MenuItemSeparator(id=130, name='menuitemseparator_130', )
    gui.StatusBar(name='statusbar_15_91', 
                  text=u'Servicio Web Factura Electr\xf3nica mercado interno (WSFEv1)', )
    with gui.Panel(id=156, label=u'Cliente:', name='panel_136_156', 
                   height='107', left='8', top='39', width='633', image='', ):
        gui.TextBox(id=158, name='textbox_400_158', left='383', top='21', 
                    width='240', value=u'Mariano Reingart', )
        gui.TextBox(id=160, name='textbox_428_160', multiline=True, 
                    height='45', left='112', top='53', width='189', 
                    value=u'Castagna 4942', )
        gui.Label(id=163, name='label_182_163', height='25', left='11', 
                  top='25', width='38', text=u'Documento:', )
        gui.Label(id=164, name='label_268_164', height='31', left='316', 
                  top='25', width='61', text=u'Nombre:', )
        gui.Label(id=165, name='label_322_165', left='10', top='54', 
                  width='72', text=u'Domicilio', )
        gui.Label(id=167, name='label_530_167', left='321', top='60', 
                  width='58', text=u'IVA:', )
        gui.TextBox(id=157, mask='##-########-#', name='textbox_228_157', 
                    left='192', top='21', width='110', bgcolor=u'#FFFFFF', 
                    fgcolor=u'#000000', value=u'20-26756539-3', )
        gui.ComboBox(name='combobox_416_70', text=u'Responsable Inscripto', 
                     left='383', top='53', width='190', 
                     data_selection=u'Responsable Inscripto', 
                     items=[u'Consumidor Final', u'Responsable Inscripto', u'Exento', u'Monotributo'], 
                     selection=1, string_selection=u'Responsable Inscripto', )
        gui.ComboBox(id=647, name='combobox_416_70_647', text=u'CF', 
                     left='111', top='20', width='78', bgcolor=u'#FFFFFF', 
                     data_selection=u'CF', fgcolor=u'#4C4C4C', 
                     items=[u'CUIT', u'DNI', u'CF'], selection=2, 
                     string_selection=u'CF', )
    gui.Label(name='label_24_16', height='17', left='13', top='15', 
              width='80', text=u'Comprobante:', )
    gui.Label(id=155, name='label_356_21_155', height='17', left='467', 
              top='16', width='60', text=u'Fecha:', )
    gui.Label(id=178, name='label_356_21_178', height='17', left='290', 
              top='14', width='20', text=u'N\xb0:', )
    gui.Image(name='image_507_571', height='36', left='394', top='494', 
              width='238', filename='sistemas-agiles.png', )
    gui.Image(name='image_33_540', height='50', left='17', top='492', 
              width='100', filename='logo-pyafipws.png', )
    gui.TextBox(id=166, mask='##', name=u'pto_vta', alignment='right', 
                left='318', top='10', width='47', bgcolor=u'#FFFFFF', 
                fgcolor=u'#000000', value=99, )
    gui.TextBox(id=177, mask='########', name=u'nro_cbte', alignment='right', 
                left='366', top='10', width='92', bgcolor=u'#FFFFFF', 
                fgcolor=u'#000000', value=12345678, )
    gui.TextBox(id=156, mask='date', name=u'fecha_cbte', alignment='center', 
                left='257', top='410', width='111', bgcolor=u'#FFFFFF', 
                fgcolor=u'#4C4C4C', value=datetime.date(2014, 2, 11), )
    gui.TextBox(mask='#####.##', name=u'total', alignment='right', left='520', 
                top='450', width='115', bgcolor=u'#FFFFFF', 
                fgcolor=u'#000000', value=1000.0, )
    gui.ComboBox(name=u'tipo_cbte', text=u'Factura A', left='115', top='10', 
                 width='170', bgcolor=u'#FFFFFF', fgcolor=u'#4C4C4C', 
                 items=[u'Factura A', u'Nota de Credito A', u'Nota de Cr\xe9dito A', u'Factura B', u'Nota de D\xe9bito B', u'Nota de Cr\xe9dito B', u'Factura C', u'Nota de D\xe9bito C', u'Nota de Cr\xe9dito C', u'Factura C', u'Nota de D\xe9bito B', u'Nota de Cr\xe9dito A', u'Nota de D\xe9bito A', u'', u'Nota de Cr\xe9dito B', u'', u''], 
                 string_selection=u'', )
    with gui.Notebook(id=780, name='notebook', height='197', left='7', 
                      top='150', width='631', selection=0, ):
        with gui.TabPanel(id=807, name='tab_art', selected=True, 
                          text=u'Art\xedculos', ):
            with gui.ListView(name=u'lv_articulos', height='118', left='4', 
                              top='6', width='617', bgcolor=u'#FFFFFF', 
                              fgcolor=u'#3C3C3C', item_count=1, sort_column=2, ):
                gui.ListColumn(align='right', name=u'qty', represent=u'%0.2f', 
                               text=u'Cant.', width=50, )
                gui.ListColumn(name=u'codigo', represent='%s', 
                               text=u'C\xf3digo', width=75, )
                gui.ListColumn(name=u'ds', represent='%s', 
                               text=u'Descripci\xf3n', width=200, )
                gui.ListColumn(align='right', name=u'precio', 
                               represent=u'%0.2f', text=u'Precio Unitario', 
                               width=125, )
                gui.ListColumn(align='center', name=u'iva_id', represent='%s', 
                               text=u'IVA', width=50, )
                gui.ListColumn(align='right', name=u'subtotal', 
                               represent=u'%0.2f', text=u'Subtotal', 
                               width=125, )
            gui.Button(label=u'Agregar', name='button_36_161', left='6', 
                       top='127', width='85px', fgcolor=u'#4C4C4C', )
            gui.Button(id=493, label=u'Borrar', name='button_588_157_493', 
                       left='94', top='127', width='85px', )
            gui.Button(label=u'Modificar', name='button_588_157', left='183', 
                       top='128', width='85px', fgcolor=u'#4C4C4C', )
        gui.TabPanel(id=850, name='tabpanel_850', selected=False, 
                     text=u'Al\xedcuotas IVA', )
        gui.TabPanel(id=869, name='tabpanel_869', selected=False, 
                     text=u'Otros tributos', )
        with gui.TabPanel(id=638, name='tabpanel_638', selected=False, 
                          text=u'Observaciones', ):
            gui.TextBox(id=715, name='textbox_715', height='65', left='147', 
                        top='87', width='468', )
            gui.Label(id=1324, name='label_1324', left='15', top='87', 
                      text=u'Obs. Comerciales:', )
            gui.TextBox(id=1534, name='textbox_715_1534', height='65', 
                        left='147', top='18', width='467', )
            gui.Label(id=1938, name='label_1324_1938', height='17', left='14', 
                      top='18', width='106', text=u'Obs. Generales:', )
        gui.TabPanel(id=2129, name='tabpanel_2129', selected=False, 
                     text=u'Servicios', )
    gui.TextBox(id=1052, mask='#####.##', name=u'total_1052', 
                alignment='right', left='520', top='420', width='115', 
                bgcolor=u'#FFFFFF', fgcolor=u'#000000', value=1000.0, )
    gui.TextBox(id=1438, mask='#####.##', name=u'total_1052_1438', 
                alignment='right', left='520', top='390', width='115', 
                bgcolor=u'#FFFFFF', fgcolor=u'#000000', value=1000.0, )
    gui.Label(id=1892, name='label_469_345_1892', alignment='right', 
              height='17', left='466', top='423', width='41', 
              bgcolor=u'#F2F1F0', fgcolor=u'#4C4C4C', text=u'IVA:', )
    gui.Label(id=226, name='label_469_345_226', alignment='right', 
              height='17', left='468', top='454', width='41', 
              bgcolor=u'#F2F1F0', fgcolor=u'#4C4C4C', text=u'Total:', )
    gui.Label(name='label_469_345', alignment='right', height='17', 
              left='406', top='396', width='110', bgcolor=u'#F2F1F0', 
              fgcolor=u'#4C4C4C', text=u'Otros Tributos:', )
    gui.TextBox(id=2377, mask='#####.##', name=u'total_1052_1438_2377', 
                alignment='right', left='520', top='360', width='115', 
                bgcolor=u'#FFFFFF', fgcolor=u'#000000', value=1000.0, )
    gui.Label(id=2423, name='label_469_345_2423', alignment='right', 
              height='17', left='399', top='362', width='110', 
              bgcolor=u'#F2F1F0', fgcolor=u'#4C4C4C', text=u'No Gravado:', )
    with gui.Panel(id=3072, label=u'Autorizaci\xf3n AFIP:', name='panel_3072', 
                   height='121', left='15', top='357', width='362', 
                   bgcolor=u'#F9F9F8', fgcolor=u'#4C4C4C', image='', ):
        gui.Label(id=2861, name='label_26_372_2499_2861', height='17', 
                  left='13', top='28', width='39', text=u'CAE:', )
        gui.TextBox(name='textbox_81_362', left='78', top='23', width='133', 
                    value=u'123456789012345', )
        gui.Label(name='label_26_372', left='11', top='90', width='39', 
                  text=u'Resultado:', )
        gui.TextBox(id=2201, mask='date', name=u'fecha_cbte_2201', 
                    alignment='center', left='94', top='54', 
                    bgcolor=u'#FFFFFF', fgcolor=u'#4C4C4C', 
                    value=datetime.date(2014, 2, 11), )
        gui.Button(id=508, label=u'Obtener', name=u'imprimir', left='224', 
                   top='21', width='114', fgcolor=u'#4C4C4C', )
        gui.Label(id=217, name='label_26_372_217', height='17', left='11', 
                  top='60', width='71', text=u'Venc. CAE:', )
        gui.RadioButton(id=241, label=u'Aceptado', name='radiobutton_188_241', 
                        left='95', top='88', width='100', bgcolor=u'#E0DEDC', 
                        fgcolor=u'#4C4C4C', value=True, )
        gui.RadioButton(id=188, label=u'Rechazado', name='radiobutton_188', 
                        left='199', top='88', width='100', bgcolor=u'#E0DEDC', 
                        fgcolor=u'#4C4C4C', )
        gui.Button(id=472, label=u'Imprimir', name=u'imprimir_472', 
                   left='224', top='53', width='114', fgcolor=u'#4C4C4C', )
    gui.TextBox(id=290, mask='date', name='textbox_290', left='517', top='11', 
                width='122', bgcolor=u'#FFFFFF', fgcolor=u'#4C4C4C', 
                value=datetime.date(2014, 5, 27), )

# --- gui2py designer generated code ends ---


# obtener referencia a la ventana principal:
mywin = gui.get("mywin")

# agrego item de ejemplo:
new_key = 'my_key_%s' % time.time()
mywin['notebook']['tab_art']['lv_articulos'].items[new_key] = {'qty': '1', 'codigo': '1111', 
    'ds': u"Honorarios  p/administración  de alquileres", 'precio': 1000., 'iva_id': 21, 
    'subtotal': 1210.}

if __name__ == "__main__":
    mywin.show()
    gui.main_loop()
