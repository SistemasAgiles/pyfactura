#!/usr/bin/python
# -*- coding: utf-8 -*-

"Aplicativo Factura Electronica Libre"

from __future__ import with_statement   # for python 2.5 compatibility

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2014- Mariano Reingart"
__license__ = "GPL 3.0+"
__version__ = "0.10b"

# Documentación: http://www.sistemasagiles.com.ar/trac/wiki/PyFactura

import datetime     # base imports, used by some controls and event handlers
import decimal
import os
import pprint
import time
import traceback
import sys
from ConfigParser import SafeConfigParser

import gui          # import gui2py package (shortcuts)

from pyafipws.padron import PadronAFIP
from pyafipws.ws_sr_padron import WSSrPadronA4
from pyafipws.sired import SIRED
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

# configuración general

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
        on_nro_doc_change(evt)
    else:
        mask = '########'
    panel['cliente']['nro_doc'].mask = mask
    panel['cliente']['nro_doc'].value = value

def on_nro_doc_change(evt):
    ctrl = panel['cliente']['nro_doc']
    doc_nro = ctrl.value
    tipo_doc = panel['cliente']['tipo_doc'].value
    cat_iva = None
    doc_nro = doc_nro.replace("-", "") if doc_nro else 0
    if doc_nro:
        if padron.Buscar(doc_nro, tipo_doc):
            panel['cliente']['nombre'].value = padron.denominacion
            panel['cliente']['domicilio'].value = ""
            try:
                cat_iva = int(padron.cat_iva)
            except ValueError:
                pass
            padron.ConsultarDomicilios(doc_nro, tipo_doc)
            # tomar el primer domicilio:
            for domicilio in padron.domicilios:
                panel['cliente']['domicilio'].value = domicilio
                break
        # si está disponible el webservice, consultar con AFIP y actualizar:
        if padron_a4:
            try:
                padron_a4.Consultar(doc_nro)
                panel['cliente']['nombre'].value = padron_a4.denominacion
                if padron_a4.domicilios:
                    panel['cliente']['domicilio'].value = padron_a4.domicilio
                if padron_a4.cat_iva:
                    cat_iva = int(padron_a4.cat_iva)
            except Exception as ex:
                ## gui.alert(unicode(ex), "Excepción consultando Padron AFIP")
                # forzar selección de categoría por el usuario:
                cat_iva = 5     # consumidor final?
        panel['cliente']['email'].value = padron.email or ""
    else:
        panel['cliente']['nombre'].value = ""
        panel['cliente']['domicilio'].value = ""
        panel['cliente']['email'].value = ""
    panel['cliente']['cat_iva'].value = cat_iva

def on_cat_iva_change(evt):
    ctrl = evt.target
    panel = ctrl.get_parent().get_parent()
    cat_iva = ctrl.value
    if cat_iva_emisor == 1:
        if cat_iva == 1:
            tipo_cbte = 1  # factura A
        else:
            tipo_cbte = 6  # factura B
    else:
        tipo_cbte = 11
    panel['tipo_cbte'].value = tipo_cbte

def on_tipo_cbte_change(evt):
    panel = evt.target.get_parent()
    # solo cambiar si es no es de solo lectura (por ej cargando desde bd)
    if panel['nro_cbte'].editable:
        tipo_cbte = panel['tipo_cbte'].value
        pto_vta = panel['pto_vta'].value = pto_vta_emisor
        if tipo_cbte and pto_vta:
            nro_cbte = wsfev1.CompUltimoAutorizado(tipo_cbte, pto_vta)
            print wsfev1.Excepcion, wsfev1.ErrMsg
        else:
            nro_cbte = -1
        nro_cbte = int(nro_cbte) + 1
        panel['nro_cbte'].value = nro_cbte

def on_servicios_change(evt):
    # habilitar fechas de servicio solo si corresponde:
    panel['periodo'].enabled = evt.target.value
    

def limpiar(evt, confirmar=False):
    if confirmar:
        if not gui.confirm(u"¿Se perderán todos los campos?", "Limpiar"):
            return
    today = datetime.datetime.today()
    desde = today - datetime.timedelta(today.day - 1)
    hasta = desde + datetime.timedelta(today.day + 31)
    hasta = hasta -  datetime.timedelta(hasta.day)
    panel['cliente']['nro_doc'].value = ""
    panel['cliente']['nombre'].value = ""
    panel['cliente']['domicilio'].value = ""
    panel['cliente']['email'].value = ""
    panel['cliente']['cat_iva'].value = None
    panel['tipo_cbte'].value = None
    panel['fecha_cbte'].value = today
    panel['nro_cbte'].value = 0
    panel['periodo']['fecha_venc_pago'].value = today
    panel['periodo']['fecha_desde'].value = desde
    panel['periodo']['fecha_hasta'].value = hasta
    panel['aut']['cae'].value = ""
    panel['aut']['fecha_vto_cae'].value = None
    panel['notebook']['obs']['generales'].value = ""
    panel['notebook']['obs']['comerciales'].value = ""
    panel['notebook']['obs']['afip'].value = ""
    panel['notebook']['tributos']['grilla'].items.clear()
    grilla.items.clear()
    recalcular()
    habilitar(True)

def habilitar(valor=True):
    panel['tipo_cbte'].enabled = valor
    panel['pto_vta'].enabled = valor
    panel['nro_cbte'].enabled = valor
    panel['fecha_cbte'].enabled = valor
    panel['cliente'].enabled = valor
    panel['conceptos'].enabled = valor
    panel['periodo'].enabled = valor
    panel['grabar'].enabled = valor
    panel['notebook']['tab_art'].enabled = valor
    panel['notebook']['alicuotas_iva'].enabled = valor
    panel['notebook']['tributos'].enabled = valor
    panel['notebook']['obs'].enabled = valor
    panel['aut']['obtener'].enabled = not valor
    panel['aut']['imprimir'].enabled = False
    panel['aut']['enviar'].enabled = False
    panel['nro_cbte'].editable = valor

def on_grid_cell_change(evt):
    grid = evt.target
    value = evt.detail
    col_name = grid.columns[evt.col].name
    if col_name == "codigo":
        grid.items[evt.row]['ds'] = datos.articulos.get(value, "")
    recalcular()

def on_agregar_click(evt):
    grilla.items.append({'qty': 1, 'precio': 0., 'iva_id': 5})

def on_borrar_click(evt):
    if grilla.items:
        del grilla.items[-1]

def on_agregar_tributo_click(evt):
    base_imp = recalcular()
    listado = panel['notebook']['tributos']['grilla']
    listado.items.append({'tributo_id': 99, 'desc': '', 
                          'alicuota': 0., 'base_imp': base_imp, })

def on_borrar_tributo_click(evt):
    listado = panel['notebook']['tributos']['grilla']
    if listado .items:
        del listado .items[-1]
        recalcular()


def recuperar(tipo_cbte=None, punto_vta=None, cbte_desde=None, cbte_hasta=None):
    "Consultar y rearmar comprobantes registrados en el Webservice de AFIP"
    title = __doc__
    facturas = []
    if not tipo_cbte:
        gui.alert("Debe completar el tipo de comprobante", title)
        ##tipo_cbte = 1
    if not punto_vta:
        gui.alert("Debe completar el punto de venta", title)
        ##punto_vta = 1
    if not cbte_desde:
        gui.alert("Debe completar el número de comprobante inicial", title)
        ##cbte_desde = 1
    if not cbte_hasta:
        gui.alert("Debe completar el número de comprobante final", title)
        ##cbte_hasta = cbte_desde + 1
    if all([tipo_cbte, punto_vta, cbte_desde, cbte_hasta]):
        for cbte_nro in range(cbte_desde, cbte_hasta + 1):
            print "Recuperando", tipo_cbte, punto_vta, cbte_nro, 
            ok = wsfev1.CompConsultar(tipo_cbte, punto_vta, cbte_nro)        
            print wsfev1.Resultado, wsfev1.CAE, wsfev1.Excepcion, wsfev1.ErrMsg
            if not ok:
                continue
            factura = wsfev1.factura.copy()
            if ok and factura:
                pprint.pprint(factura)
                factura["id"] = len(facturas) + 1
                factura["cbte_nro"] = factura["cbt_desde"]
                factura["nombre_cliente"] = ""
                factura["id_impositivo"] = ""
                factura["email"] = ""
                factura["cat_iva"] = ""
                factura["domicilio_cliente"] = ""
                factura["obs_generales"] = ""
                factura["obs_comerciales"] = ""
                factura["forma_pago"] = ""
                factura["motivo_obs"] = wsfev1.Obs
                factura["fecha_vto"] = datetime.datetime.strptime(
                                         wsfev1.Vencimiento, "%Y%m%d").date()
                # obtener datos del cliente desde el padrón
                if padron.Buscar(factura["nro_doc"], factura["tipo_doc"]):
                    factura["nombre_cliente"] = padron.denominacion
                    try:
                        factura["cat_iva"] = int(padron.cat_iva)
                    except ValueError:
                        pass
                    if padron_a4:
                        try:
                            padron_a4.Consultar(factura["nro_doc"])
                            factura["nombre_cliente"] = padron_a4.denominacion
                            factura["domicilio_cliente"] = padron_a4.domicilio
                        except:
                            pass
                    factura["email"] = padron.email or ""

                # rearmar campos no informados en este Webservice:
                factura["detalles"] = []
                for i, iva in enumerate(factura["iva"]):
                    it = {'ds': "Art. %s" % (i + 1), "umed": 0, 'codigo': "",
                      'qty': 1, 'precio': iva["base_imp"], 'bonif': 0,
                      'iva_id': iva["iva_id"], 'imp_iva': iva["importe"], 
                      'subtotal': iva["base_imp"] + iva["importe"]}
                    factura["detalles"].append(it)
                facturas.append(factura)
    return facturas

def on_consultas(evt):
    import consultas
    # Workaround: recreate gui objects if the window was closed (TODO: Fix)
    try:
        gui.get("consultas").title
    except:
        reload(consultas)
    consultas.main(callback=cargar_factura, recuperar_fn=recuperar)    

def recalcular(evt=None):
    tipo_cbte = panel['tipo_cbte'].value
    neto_iva = {}
    imp_iva = {}
    tasas_iva = {1: None, 2: None, 3: 0, 4: 10.5, 5: 21, 6: 27, 8: 5, 9: 2.5}
    total = 0.
    for it in grilla.items:
        iva_id = it['iva_id']
        qty = it['qty']
        precio = it['precio']
        subtotal = qty * precio
        it['subtotal'] = subtotal
        total += subtotal
        it['imp_iva'] = None
        if iva_id in tasas_iva:
            if not iva_incluido or tasas_iva[iva_id] is None:
                neto_item = subtotal
            else:
                neto_item = round(subtotal / (100. + tasas_iva[iva_id]) * 100., 2)
            neto_iva[iva_id] = neto_iva.get(iva_id, 0.) + neto_item
            if tasas_iva[iva_id] is not None and not tipo_cbte in datos.CLASE_C:
                iva_liq = neto_item * tasas_iva[iva_id] / 100.
                imp_iva[iva_id] = imp_iva.get(iva_id, 0.) + iva_liq
                it['imp_iva'] = iva_liq
    imp_trib = 0.00
    listado = panel['notebook']['tributos']['grilla']
    for it in listado.items:
        base_imp = it['base_imp'] or 0.00
        alic = it['alic'] or 0.00
        importe = it["importe"] = round(base_imp * alic / 100., 2)
        imp_trib += importe
    listado = panel['notebook']['alicuotas_iva']['listado']
    listado.items.clear()
    for iva_id, iva_liq in imp_iva.items():
        listado.items[str(iva_id)] = {'iva_id': iva_id, 'importe': iva_liq,
                                       'base_imp': neto_iva[iva_id],
                                       'alicuota': tasas_iva[iva_id]}
    # excluir exento y no gravado del calculo del neto:
    neto = sum([nt for iva_id, nt in neto_iva.items() 
                    if tasas_iva.get(iva_id) is not None])
    panel['notebook']['alicuotas_iva']['imp_neto'].value = neto
    panel['notebook']['alicuotas_iva']['imp_tot_conc'].value = neto_iva.get(1, 0)
    panel['notebook']['alicuotas_iva']['imp_op_ex'].value = neto_iva.get(2, 0)
    panel['imp_iva'].value = sum(imp_iva.values(), 0.)
    panel['imp_trib'].value = imp_trib
    if not iva_incluido:
        total += sum(imp_iva.values(), 0.)
    total += imp_trib
    panel['imp_total'].value = total 
    # calcular subtotal general (neto sin IVA, incluyendo exento y no gravado):
    subtotal_neto = sum([nt for iva_id, nt in neto_iva.items()])
    return subtotal_neto

def obtener_cae(evt):
    global id_factura
    if not id_factura:
        grabar(evt)
    tipo_cbte = panel['tipo_cbte'].value
    punto_vta = panel['pto_vta'].value
    cbte_nro = panel['nro_cbte'].value
    fecha_cbte =  panel['fecha_cbte'].value.strftime("%Y%m%d")
    concepto = 0
    if panel['conceptos']['productos'].value:
        concepto += 1
    if panel['conceptos']['servicios'].value:
        concepto += 2
    tipo_doc = panel['cliente']['tipo_doc'].value
    nro_doc = panel['cliente']['nro_doc'].value.replace("-", "")
    # Redondear valores a 2 decimales para superar validación 10056 de AFIP
    imp_neto = "%0.2f" % panel['notebook']['alicuotas_iva']['imp_neto'].value
    imp_iva = "%0.2f" % panel['imp_iva'].value
    imp_trib = "%0.2f" % panel['imp_trib'].value
    imp_op_ex = "%0.2f" % panel['notebook']['alicuotas_iva']['imp_op_ex'].value
    imp_tot_conc = "%0.2f" % panel['notebook']['alicuotas_iva']['imp_tot_conc'].value
    imp_total = "%0.2f" % panel['imp_total'].value
    # solo informar si es servicio (no informar para productos)
    if concepto > 1:
        fecha_venc_pago = panel['periodo']['fecha_venc_pago'].value.strftime("%Y%m%d")
        fecha_serv_desde = panel['periodo']['fecha_desde'].value.strftime("%Y%m%d")
        fecha_serv_hasta = panel['periodo']['fecha_hasta'].value.strftime("%Y%m%d")
    else:
        fecha_venc_pago = fecha_serv_desde = fecha_serv_hasta = None
    moneda_id = 'PES'; moneda_ctz = '1.000'
    wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
        cbte_nro, cbte_nro, imp_total, imp_tot_conc, imp_neto,
        imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
        fecha_serv_desde, fecha_serv_hasta, #--
        moneda_id, moneda_ctz)

    if False:
        tipo = 19
        pto_vta = 2
        nro = 1234
        wsfev1.AgregarCmpAsoc(tipo, pto_vta, nro)

    listado = panel['notebook']['tributos']['grilla']
    for it in listado.items:
        tributo_id = it['tributo_id']
        desc = it['desc'] or ""
        base_imp = it['base_imp']
        alic = it['alic']
        importe = it['importe']
        wsfev1.AgregarTributo(tributo_id, desc, base_imp, alic, importe)

    listado = panel['notebook']['alicuotas_iva']['listado']
    for it in listado.items:
        iva_id = it['iva_id']
        base_imp = "%0.2f" % it['base_imp']
        importe = "%0.2f" % it['importe']
        wsfev1.AgregarIva(iva_id, base_imp, importe)

    try:
        wsfev1.CAESolicitar()
        panel['aut']['cae'].value = wsfev1.CAE
        vto = datetime.datetime.strptime(wsfev1.Vencimiento, "%Y%m%d").date()
        panel['aut']['fecha_vto_cae'].value = vto
        panel['notebook']['obs']['afip'].value = wsfev1.Obs
    except:
        print wsfev1.Excepcion, wsfev1.ErrMsg
        print wsfev1.XmlRequest, wsfev1.XmlResponse
    panel['aut']['aceptado'].value = wsfev1.Resultado == "A"
    panel['aut']['rechazado'].value = wsfev1.Resultado == "R"
    if wsfev1.Excepcion:
        gui.alert(wsfev1.Excepcion, u"Excepcion")
    if wsfev1.Obs:
        gui.alert(wsfev1.Obs, u"Observaciones AFIP")
    if wsfev1.ErrMsg:
        gui.alert(wsfev1.ErrMsg, u"Mensajes Error AFIP")

    # actualizar registro
    sired.EstablecerParametro("cae", wsfev1.CAE)
    sired.EstablecerParametro("fecha_vto", wsfev1.Vencimiento)
    sired.EstablecerParametro("motivo_obs", wsfev1.Obs)
    sired.EstablecerParametro("resultado", wsfev1.Resultado)
    sired.EstablecerParametro("reproceso", wsfev1.Reproceso)
    sired.EstablecerParametro("err_code", wsfev1.ErrCode)
    sired.EstablecerParametro("err_msg", wsfev1.ErrMsg)
    sired.ActualizarFactura(id_factura)

    if wsfev1.Resultado == "A":
        panel['aut']['imprimir'].enabled = True
        panel['aut']['enviar'].enabled = True

def crear_factura(comp, imprimir=True):
    tipo_cbte = panel['tipo_cbte'].value or 6
    punto_vta = panel['pto_vta'].value
    cbte_nro = panel['nro_cbte'].value
    fecha_cbte =  panel['fecha_cbte'].value.strftime("%Y%m%d")
    concepto = 0
    if panel['conceptos']['productos'].value:
        concepto += 1
    if panel['conceptos']['servicios'].value:
        concepto += 2
    tipo_doc = panel['cliente']['tipo_doc'].value
    nro_doc = panel['cliente']['nro_doc'].value.replace("-", "")
    imp_neto = panel['notebook']['alicuotas_iva']['imp_neto'].value
    imp_iva = panel['imp_iva'].value
    imp_trib = panel['imp_trib'].value
    imp_op_ex = panel['notebook']['alicuotas_iva']['imp_op_ex'].value
    imp_tot_conc = panel['notebook']['alicuotas_iva']['imp_tot_conc'].value
    imp_total = panel['imp_total'].value
    fecha = panel['periodo']['fecha_venc_pago'].value
    fecha_venc_pago = fecha.strftime("%Y%m%d") if fecha else None
    fecha = panel['periodo']['fecha_desde'].value
    fecha_serv_desde = fecha.strftime("%Y%m%d") if fecha else None
    fecha = panel['periodo']['fecha_hasta'].value
    fecha_serv_hasta = fecha.strftime("%Y%m%d") if fecha else None
    moneda_id = 'PES'; moneda_ctz = '1.000'
    obs_generales = panel['notebook']['obs']['generales'].value
    obs_comerciales = panel['notebook']['obs']['comerciales'].value
    nombre_cliente = panel['cliente']['nombre'].value
    email = panel['cliente']['email'].value
    cat_iva =  panel['cliente']['cat_iva'].value or None
    # dividir el domicilio en lineas y ubicar los campos (solo al imprimir)
    if imprimir:
        domicilio = panel['cliente']['domicilio'].value.split("\n")
        domicilio_cliente = domicilio and domicilio[0] or ""
    else:
        domicilio = domicilio_cliente = panel['cliente']['domicilio'].value
    pais_dst_cmp = 200  # Argentina
    id_impositivo =  panel['cliente']['cat_iva'].text
    forma_pago = panel['conceptos']['forma_pago'].text
    incoterms = 'FOB'
    idioma_cbte = 1  # español
    motivo = panel['notebook']['obs']['afip'].value
    cae = panel['aut']['cae'].value or 0
    vto = panel['aut']['fecha_vto_cae'].value
    fch_venc_cae = vto and vto.strftime("%Y%m%d") or ""
    
    comp.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
        cbte_nro, imp_total, imp_tot_conc, imp_neto,
        imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
        fecha_serv_desde, fecha_serv_hasta, 
        moneda_id, moneda_ctz, cae, fch_venc_cae, id_impositivo,
        nombre_cliente, domicilio_cliente, pais_dst_cmp, 
        obs_comerciales, obs_generales, forma_pago, incoterms, 
        idioma_cbte, motivo)

    comp.EstablecerParametro("email", email)
    comp.EstablecerParametro("cat_iva", cat_iva)

    if panel['aut']['aceptado'].value:
        resultado = "A"
    elif panel['aut']['rechazado'].value:
        resultado = "R"
    comp.EstablecerParametro("resultado", resultado)
    
    if False:
        tipo = 91
        pto_vta = 2
        nro = 1234
        comp.AgregarCmpAsoc(tipo, pto_vta, nro)

    listado = panel['notebook']['tributos']['grilla']
    for it in listado.items:
        tributo_id = it['tributo_id']
        desc = it['desc'] or ""
        base_imp = it['base_imp']
        alic = it['alic']
        importe = it['importe']
        comp.AgregarTributo(tributo_id, desc, base_imp, alic, importe)

    listado = panel['notebook']['alicuotas_iva']['listado']
    for it in listado.items:
        iva_id = it['iva_id']
        base_imp = it['base_imp']
        importe = it['importe']
        comp.AgregarIva(iva_id, base_imp, importe)
    
    for it in grilla.items:
        u_mtx = ""
        cod_mtx = ""
        codigo = it['codigo'] or ""
        ds = it['ds'] or ""
        qty = it['qty']
        umed = 7
        precio = it['precio']
        bonif = 0.00
        iva_id = it['iva_id']
        imp_iva = it['imp_iva'] or 0
        subtotal = it['subtotal'] or 0
        # no discriminar IVA si no es Factura clase A / M:
        if tipo_cbte not in (1, 2, 3, 4, 51, 52, 53, 54) and imprimir:
            if not iva_incluido:
                precio += imp_iva / qty
        # siempre mostrar subtotal c/IVA (idem AFIP):
        if imp_iva is not None and not iva_incluido and imprimir:
            subtotal += imp_iva
        despacho = ""
        comp.AgregarDetalleItem(u_mtx, cod_mtx, codigo, ds, qty, umed, 
                precio, bonif, iva_id, imp_iva, subtotal, despacho)

    # datos fijos:
    for k, v in conf_pdf.items():
        fepdf.AgregarDato(k, v)
        if k.upper() == 'CUIT':
            fepdf.CUIT = v  # CUIT del emisor para código de barras

    if len(domicilio) > 1:
        comp.AgregarDato("Cliente.Localidad", domicilio[1])
    if len(domicilio) > 2:
        comp.AgregarDato("Cliente.Provincia", domicilio[2])

def generar_pdf(evt, mostrar=True):
    crear_factura(fepdf)

    fepdf.CrearPlantilla(papel=conf_fact.get("papel", "legal"), 
                         orientacion=conf_fact.get("orientacion", "portrait"))
    if "borrador" in conf_pdf or HOMO:
        fepdf.AgregarDato("draft", conf_pdf.get("borrador", "HOMOLOGACION"))

    if "logo" in conf_pdf and not os.path.exists(conf_pdf["logo"]):
        fepdf.AgregarDato("logo", "")

    fepdf.ProcesarPlantilla(num_copias=int(conf_fact.get("copias", 1)),
                            lineas_max=int(conf_fact.get("lineas_max", 24)),
                            qty_pos=conf_fact.get("cant_pos") or 'izq')
    salida = conf_fact.get("salida", "")
    fact = fepdf.factura
    if salida:
        pass
    elif 'pdf' in fact and fact['pdf']:
        salida = fact['pdf']
    else:
        # genero el nombre de archivo según datos de factura
        d = conf_fact.get('directorio', ".")
        clave_subdir = conf_fact.get('subdirectorio','fecha_cbte')
        if clave_subdir:
            d = os.path.join(d, fact[clave_subdir])
        if not os.path.isdir(d):
            os.makedirs(d)
        fs = conf_fact.get('archivo','numero').split(",")
        it = fact.copy()
        tipo_fact, letra_fact, numero_fact = fact['_fmt_fact']
        it['tipo'] = tipo_fact.replace(" ", "_")
        it['letra'] = letra_fact
        it['numero'] = numero_fact
        it['mes'] = fact['fecha_cbte'][4:6]
        it['año'] = fact['fecha_cbte'][0:4]
        fn = u''.join([unicode(it.get(ff,ff)) for ff in fs])
        fn = fn.encode('ascii', 'replace').replace('?','_')
        salida = os.path.join(d, "%s.pdf" % fn)
    fepdf.GenerarPDF(archivo=salida)
    if mostrar:
        fepdf.MostrarPDF(archivo=salida, imprimir='--imprimir' in sys.argv)
    return salida

def grabar(evt):
    global id_factura
    tipo_doc = panel['cliente']['tipo_doc'].value
    nro_doc = panel['cliente']['nro_doc'].value.replace("-", "")
    denominacion = panel['cliente']['nombre'].value
    direccion = panel['cliente']['domicilio'].value
    cat_iva =  panel['cliente']['cat_iva'].value or None
    email = panel['cliente']['email'].value
    if not all([tipo_doc, nro_doc, denominacion]):
        gui.alert(u"Información del cliente incompleta", "Imposible Guardar")
    elif not grilla.items:
        gui.alert(u"No ingresó artículos", "Imposible Guardar")
    elif not panel['conceptos']['productos'].value and not panel['conceptos']['servicios'].value:
        gui.alert(u"Debe seleccionar productos, servicios o ambos", "Imposible Guardar")
    elif panel['imp_total'].value == 0 and not gui.confirm(u"¿Importe 0?", "Confirmar Guardar"):
        pass
    else:
        padron.Guardar(tipo_doc, nro_doc, denominacion, cat_iva, direccion, email)
        crear_factura(sired, imprimir=False)
        id_factura = sired.GuardarFactura()
        habilitar(False)

def cargar(evt):
    if not gui.confirm(u"¿Se restableceran todos los campos?", u"Cargar última factura"):
        return
    sired.ObtenerFactura()
    f = sired.factura
    cargar_factura(f)

def cdate(s):
    if isinstance(s, (datetime.datetime, datetime.date)):
        return s
    elif s: 
        return datetime.datetime.strptime(s, "%Y%m%d").date()
    else:
        return None

def cargar_factura(f):
    # cargar datos de cliente (dispara eventos)
    nro_doc = str(f["nro_doc"])
    if f["tipo_doc"] == 80 and len(nro_doc) == 11:
        nro_doc = "%2s-%6s-%1s" % (nro_doc[0:2], nro_doc[2:10], nro_doc[10:])
    panel['cliente']['tipo_doc'].value = f["tipo_doc"]
    panel['cliente']['nro_doc'].value = nro_doc
    panel['cliente']['nombre'].value = f["nombre_cliente"]
    panel['cliente']['email'].value = f["email"]
    panel['cliente']['cat_iva'].value = f["cat_iva"] or None 
    panel['cliente']['domicilio'].value = f["domicilio_cliente"]
    # cargar datos del encabezado del comprobante
    panel['tipo_cbte'].value = f["tipo_cbte"]
    panel['pto_vta'].value = f["punto_vta"]
    panel['nro_cbte'].value = f["cbte_nro"]
    panel['nro_cbte'].editable = False      # no permit que el evento lo cambie
    panel['fecha_cbte'].value = cdate(f["fecha_cbte"])
    panel['conceptos']['productos'].value = f["concepto"] & 1
    panel['conceptos']['servicios'].value = f["concepto"] & 2
    panel['notebook']['alicuotas_iva']['imp_neto'].value = float(f["imp_neto"])
    panel['imp_iva'].value = float(f["imp_iva"])
    panel['imp_trib'].value = float(f["imp_trib"])
    panel['notebook']['alicuotas_iva']['imp_op_ex'].value = float(f["imp_op_ex"])
    panel['notebook']['alicuotas_iva']['imp_tot_conc'].value = float(f["imp_tot_conc"])
    panel['imp_total'].value = float(f["imp_total"])
    panel['periodo']['fecha_venc_pago'].value = f["fecha_venc_pago"]
    panel['periodo']['fecha_desde'].value = cdate(f["fecha_serv_desde"])
    panel['periodo']['fecha_hasta'].value = cdate(f["fecha_serv_hasta"])
    panel['notebook']['obs']['generales'].value = f["obs_generales"]
    panel['notebook']['obs']['comerciales'].value = f["obs_comerciales"]
    panel['conceptos']['forma_pago'].text = f["forma_pago"]
    panel['notebook']['obs']['afip'].value = f.get("motivo_obs") or ""
    panel['aut']['cae'].value = f.get("cae") or ""
    panel['aut']['fecha_vto_cae'].value = cdate(f.get("fecha_vto"))

    listado = panel['notebook']['alicuotas_iva']['listado']
    listado.items.clear()
    # TODO: ajustar gui2py para soportar decimal...
    #for it in f.get("ivas", []):
    #    listado.items[str(it['iva_id'])] = {'iva_id': it['iva_id'], 
    #                                   'importe': it['importe'],
    #                                   'base_imp': it["base_imp"],
    #                                   'alicuota': it.get("alicuota")}
    grilla.items.clear()
    for it in f.get("detalles", []):
        for k, v in it.items():
            if isinstance(v, decimal.Decimal):
                it[k] = round(float(v), 2)
        grilla.items.append(it)

    listado = panel['notebook']['tributos']['grilla']
    listado.items.clear()
    for it in f.get("tributos", []):
        for k, v in it.items():
            if isinstance(v, decimal.Decimal):
                it[k] = round(float(v), 2)
        listado.items.append(it)

    recalcular()
    habilitar(False)
    # habilitar reimpresión y envio si tiene CAE
    if f.get("cae") and str(f["cae"]).isdigit() and len(str(f["cae"])) == 14:
        panel['aut']['obtener'].enabled = False
        panel['aut']['imprimir'].enabled = True
        panel['aut']['enviar'].enabled = True

def enviar(evt):
    tipo_cbte = panel['tipo_cbte'].text
    punto_vta = panel['pto_vta'].value
    cbte_nro = panel['nro_cbte'].value
    cbte = "%s %04d-%08d" % (tipo_cbte, punto_vta, cbte_nro)    
    motivo = conf_mail['motivo'].replace("NUMERO", cbte)
    destinatario = panel['cliente']['email'].value
    mensaje = conf_mail['cuerpo']
    archivo = generar_pdf(evt, mostrar=False)
    
    print "Motivo: ", motivo
    print "Destinatario: ", destinatario
    print "Mensaje: ", mensaje
    print "Archivo: ", archivo
    
    pyemail = PyEmail()
    pyemail.Conectar(conf_mail['servidor'], 
                     conf_mail['usuario'], conf_mail['clave'], 
                     conf_mail['puerto'],)
    if 'cc' in conf_mail:
        pyemail.AgregarCC(conf_mail['cc'])
    if 'bcc' in conf_mail:
        pyemail.AgregarBCC(conf_mail['bcc'])
    if pyemail.Enviar(conf_mail['remitente'], 
                        motivo, destinatario, mensaje, archivo):
        gui.alert("Correo \"%s\" enviado correctamente a %s" % 
                    (motivo, destinatario), "Enviar email", icon="info")
    else:
        print pyemail.Traceback
        gui.alert(pyemail.Excepcion, "Error al enviar email", icon="error")

# --- gui2py designer generated code starts ---

with gui.Window(name='mywin', visible=False,
                title=u'Aplicativo Facturaci\xf3n Electr\xf3nica', 
                resizable=True, height='620px', left='181', top='52', 
                width='653px',
                image=''):
    with gui.MenuBar(name='menubar_83_155', ):
        with gui.Menu(name='menu_114', ):
            gui.MenuItem(name='consultas', label='Consultas', 
                         onclick=on_consultas)
            gui.MenuItemSeparator(name='menuitemseparator_130', )
    gui.StatusBar(name='statusbar_15_91', 
                  text=u'Servicio Web Factura Electr\xf3nica mercado interno (WSFEv1)', )
    with gui.Panel(name='panel'):
        with gui.Panel(label=u'Cliente:', name='cliente', 
                       height='114', left='8', top='6', width='633', image='', ):
            gui.Label(name='label_182_163', height='25', left='11', 
                      top='24', width='38', text=u'Documento:', )
            gui.ComboBox(name='tipo_doc', text=u'CF', 
                         left='111', top='20', width='78', 
                         value=80, onchange=on_tipo_doc_change,
                         items=datos.TIPO_DOC_MAP, )
            gui.TextBox(mask='##-########-#', name='nro_doc', 
                        left='192', top='20', width='110', 
                        value=u'20-26756539-3', onblur=on_nro_doc_change,
                        )
            gui.Label(name='label_268_164', height='31', left='316', 
                      top='24', width='61', text=u'Nombre:', )
            gui.TextBox(name='nombre', 
                        left='383', top='20', width='240', 
                        value=u'Mariano Reingart', )
            gui.Label(name='label_322_165', left='10', top='52', 
                      width='72', text=u'Domicilio:', )
            gui.TextBox(name='domicilio', multiline=True, 
                        height='55', left='112', top='52', width='189', 
                        value=u'Castagna 4942', )
            gui.Label(name='label_530_167', left='321', top='85', 
                      width='58', text=u'E-Mail:', )
            gui.Label(name='label_530_167_1258', height='17', left='321', 
                      top='56', width='58', text=u'IVA:', )
            gui.ComboBox(name='cat_iva', text=u'Responsable Inscripto', 
                         left='383', top='51', width='190', editable=False,
                         onchange=on_cat_iva_change,
                         items={1: u"Responsable Inscripto", 4: u"Exento", 
                                5: u"Consumidor Final", 6: u"Monotributo",
                                8: u"Proveedor del Exterior",
                                9: u"Cliente del Exterior",
                                10: u"IVA Liberado - Ley Nº 19.640",
                                12: u"Pequeño Contribuyente Eventual",
                                13: u"Monotributista Social",
                                14: u"Pequeño Contribuyente Eventual Social",
                                15: u"IVA No Alcanzado"}, 
                         )
            gui.TextBox(name='email', left='383', top='82', 
                        width='240', value=u'reingart@gmail.com', )
        gui.Label(name='label_24_16', height='17', left='13', top='130', 
                  width='80', text=u'Comprobante:', )
        gui.ComboBox(name=u'tipo_cbte', left='115', top='125', 
                     width='170', onchange=on_tipo_cbte_change,
                     items=datos.TIPO_CBTE_MAP, 
                     text=u'', editable=False)
        gui.Label(name='label_356_21_178', height='17', left='290', 
                  top='130', width='20', text=u'N\xb0:', )
        gui.TextBox(mask='####', name=u'pto_vta', alignment='right', 
                    left='318', top='125', width='47', 
                    value=99, )
        gui.TextBox(mask='########', name=u'nro_cbte', alignment='right', 
                    left='366', top='125', width='92', 
                    value=12345678, )
        gui.Label(name='label_356_21_155', height='17', left='467', 
                  top='130', width='60', text=u'Fecha:', )
        gui.TextBox(id=290, mask='date', name='fecha_cbte', left='517', top='125', 
                    width='122', 
                    value=datetime.date(2014, 5, 27), )
        with gui.Panel(label=u'Conceptos a incluir', name='conceptos', 
                       height='89', left='8', top='157', width='265', 
                       image='', ):
            gui.CheckBox(label=u'Productos', name='productos', left='13', 
                         top='24', width='99', 
                         )
            gui.CheckBox(label=u'Servicios', name='servicios', left='132', 
                         top='24', width='110', value=True, 
                         onclick=on_servicios_change,
                         )
            gui.Label(name='label_182_163', height='25', left='11', 
                      top='55', width='42', text=u'Forma Pago:', )
            gui.ComboBox(name='forma_pago', value=u'Contado', 
                         left='111', top='50', width='145', 
                         items=[u"Contado", u"Tarjeta de Débito",
                                u"Tarjeta de Crédito", u"Cuenta Corriente",
                                u"Cheque", u"Ticket", u"Otra"] )
        with gui.Panel(label=u'Per\xedodo Facturado', name='periodo', 
                       height='89', left='276', top='158', width='363', 
                       image='', ):
            gui.Label(name='label_272_30_1442_1458', height='17', 
                      left='17', top='25', width='49', text=u'Desde:', )
            gui.Label(name='label_272_30', left='192', top='25', width='49', 
                      text=u'Hasta:', )
            gui.TextBox(id=998, mask='date', name='fecha_desde', 
                        left='72', top='20', width='113', 
                        value=datetime.date(2014, 5, 28), )
            gui.TextBox(mask='date', name='fecha_hasta', left='240', top='20', 
                        width='113', 
                        value=datetime.date(2014, 5, 28), )
            gui.Label(name='label_272_30_1442', height='17', left='113', 
                      top='57', width='49', text=u'Vto. para el Pago:', )
            gui.TextBox(mask='date', name='fecha_venc_pago', 
                        left='241', top='51', width='113', 
                        value=datetime.date(2014, 5, 28), )
        with gui.Notebook(name='notebook', height='197', left='7', 
                          top='249', width='631', selection=0, ):
            with gui.TabPanel(name='tab_art', selected=True, 
                              text=u'Art\xedculos', ):
                with gui.GridView(name=u'items', height='118', left='10', 
                                  top='6', width='610', row_label="",
                                  ongridcellchanged=on_grid_cell_change):
                    gui.GridColumn(align='right', name=u'qty', type='double', 
                                   format="4,2", represent=u'%0.2f', 
                                   text=u'Cant.', width=50, )
                    gui.GridColumn(name=u'codigo', represent='%s', type='text', 
                                   text=u'C\xf3digo', width=75, )
                    gui.GridColumn(name=u'ds', represent='%s', type='combo', 
                                   text=u'Descripci\xf3n', width=275, )
                    gui.GridColumn(align='right', name=u'precio', type='double', 
                                   format="11,2", represent=u'%0.2f', text=u'Precio', 
                                   width=75, )
                    gui.GridColumn(align='center', name=u'iva_id', represent='%s', 
                                   choices={1: "no gravado", 2: "exento", 
                                            3: "0%", 4: "10.5%", 5: "21%" , 
                                            6: "27%", 8: "5%", 9: "2.5%"},
                                   text=u'IVA', type='choice', width=50, )
                    gui.GridColumn(align='right', name=u'subtotal', type='double', 
                                   represent=u'%0.2f', text=u'Subtotal', 
                                   width=75, format="15,2")
                gui.Button(label=u'Agregar', name='agregar', left='6', 
                           top='127', width='85px', onclick=on_agregar_click)
                gui.Button(id=493, label=u'Borrar', name='borrar', 
                           left='94', top='127', width='85px', onclick= on_borrar_click)
                gui.Button(label=u'Modificar', name='modificar', left='183', 
                           top='128', width='85px', visible=False)
            with gui.TabPanel(name='alicuotas_iva', selected=False, 
                              text=u'Al\xedcuotas IVA', ):
                with gui.ListView(name='listado', height='100', 
                                  left='15', top='34', width='357', item_count=0, 
                                  sort_column=1, ):
                    gui.ListColumn(name=u'iva_id', text=u'ID', width=40, 
                                   represent=lambda x: {3: "0%", 4: "10.5%", 
                                                        5: "21%", 6: "27%",
                                                        8: "5%", 9: "2.5%"}[x])
                    gui.ListColumn(name=u'alicuota', text=u'Al\xedcuota', 
                                   align="right", width=75, represent="%.2f")
                    gui.ListColumn(name=u'base_imp', text=u'Base Imp.', 
                                   width=100, represent="%.2f", align="right")
                    gui.ListColumn(name=u'importe', text=u'Importe IVA', 
                                   width=100, represent="%.2f", align="right")
                gui.Label(name='label_388', left='20', top='11', 
                          text=u'Subtotales de IVA liquidado por al\xedcuota:', )
                gui.Label(name='label_387_630', height='17', left='393', 
                          top='71', width='92', text=u'No Gravado:', )
                gui.TextBox(name='imp_tot_conc', left='519', top='67', width='92',
                            mask='#############.##', alignment='right', editable=False)
                gui.Label(name='label_387_542', height='17', left='393', 
                          top='40', width='99', text=u'Neto Gravado:', )
                gui.TextBox(name='imp_neto', mask='#############.##', alignment='right', 
                            left='519', top='36', width='92', editable=False)
                gui.Label(name='label_387', left='395', top='100', 
                          text=u'Exento:', )
                gui.TextBox(name='imp_op_ex',  mask='#############.##', alignment='right', 
                            left='519', top='97', width='92', editable=False)
            with gui.TabPanel(id=869, name='tributos', selected=False, 
                              text=u'Otros tributos', ):
                with gui.GridView(name='grilla', height='102', 
                                  left='12', top='18', width='606', item_count=0, 
                                  ongridcellchanged=recalcular,
                                  sort_column=0, ):
                    gui.GridColumn(name='tributo_id', text=u'Impuesto', 
                                   choices={1: "nacional", 2: "provincial", 
                                            3: "municipal", 4: "interno", 
                                            99: "otro"},
                                   type='choice', width=125, )
                    gui.GridColumn(name='desc', text=u'Descripci\xf3n', 
                                   width=200, type='text', )
                    gui.GridColumn(name='base_imp', text=u'Base Imp.', 
                                   width=75, type='double', format='15,2',)
                    gui.GridColumn(name='alic', text=u'Al\xedcuota', width=75,
                                   type='double', format='3,2',)
                    gui.GridColumn(name='importe', text=u'Importe', width=125,
                                   type='double', format='15,2',)
                gui.Button(label=u'Agregar', name='agregar', left='6', 
                           top='127', width='85px', 
                           onclick=on_agregar_tributo_click)
                gui.Button(id=493, label=u'Borrar', name='borrar', 
                           left='94', top='127', width='85px',
                           onclick=on_borrar_tributo_click)
                gui.Button(label=u'Modificar', name='modificar', left='183', 
                           top='128', width='85px', visible=False)
            with gui.TabPanel(name='obs', selected=False, 
                              text=u'Observaciones', ):
                gui.Label(name='label_1324', left='15', top='65', 
                          text=u'Obs. Comerciales:', )
                gui.Label(id=1938, name='label_1324_1938', height='17', left='14', 
                          top='15', width='106', text=u'Obs. Generales:', )
                gui.Label(name='label_1325', left='15', top='110', 
                          text=u'Obs. AFIP:', )
                gui.TextBox(name='generales', multiline=True, 
                            height='45', left='147', top='10', width='467', 
                            )
                gui.TextBox(name='comerciales', multiline=True, 
                            height='45', left='147', top='60', width='468', 
                            )
                gui.TextBox(name='afip', multiline=True, 
                            height='45', left='147', top='110', width='468', 
                            )
        with gui.Panel(label=u'Autorizaci\xf3n AFIP:', name='aut', 
                       height='121', left='8', top='449', width='335', 
                       image='', ):
            gui.Label(name='label_26_372_2499_2861', height='17', 
                      left='8', top='28', width='39', text=u'CAE:', )
            gui.TextBox(name='cae', left='70', top='23', width='133', 
                        value=u'123456789012345', editable=False)
            gui.Label(name='label_26_372_217', height='17', left='8', 
                      top='60', width='71', text=u'Venc. CAE:', )
            gui.TextBox(mask='date', name=u'fecha_vto_cae', 
                        alignment='center', left='80', top='54',                         
                        value=datetime.date(2014, 2, 11), editable=False)
            gui.Button(label=u'Obtener', name=u'obtener', left='224', 
                       top='21', width='75', onclick=obtener_cae)
            gui.Label(name='label_26_372', left='11', top='90', width='39', 
                      text=u'Resultado:', )
            gui.RadioButton(label=u'Aceptado', name='aceptado', 
                            left='95', top='88', width='75', 
                            value=True, enabled=False)
            gui.RadioButton(label=u'Rechazado', name='rechazado', 
                            left='199', top='88', width='100', 
                            enabled=False)
            gui.Button(label=u'Imprimir', name=u'imprimir', 
                       left='200', top='53', width='70', onclick=generar_pdf)
            gui.Button(label=u'Enviar', name=u'enviar', left='270', top='53', 
                       width='55', onclick=enviar)

        gui.Label(name='label_469_345_1892', alignment='right', 
                  height='17', left='466', top='488', width='50', 
                  text=u'IVA:', )
        gui.TextBox(mask='#############.##', name=u'imp_iva', editable=False,
                    alignment='right', left='520', top='485', width='115',)
        gui.Label(name='label_469_345', alignment='right', height='17', 
                  left='466', top='461', width='50', 
                  text=u'Tributos:', )
        gui.TextBox(mask='#############.##', name=u'imp_trib', editable=False,
                    alignment='right', left='520', top='455', width='115')
        gui.Label(name='label_469_345_226', alignment='right', 
                  height='17', left='480', top='519', width='36', 
                  text=u'Total:', )
        gui.TextBox(mask='#############.##', name=u'imp_total', alignment='right', 
                    left='520', top='515', width='115', editable=False)
        gui.Image(name='image_507_571', height='27', left='350', top='514', 
                  width='178', stretch=False, filename='sistemas-agiles.png', )
        gui.Image(name='image_33_540', height='37', left='350', top='460', 
                  width='75', stretch=False, filename='logo-pyafipws.png', )
        gui.Button(label=u'Grabar', name=u'grabar', 
                   left='350', top='542', width='75', onclick=grabar)
        gui.Button(label=u'Limpiar', name=u'limpiar', left='430', top='542', 
                   width='75', onclick=lambda evt: limpiar(evt, True))
        gui.Button(label=u'Cargar', name=u'cargar', left='510', top='542', 
                   width='75', onclick=cargar)


# --- gui2py designer generated code ends ---


# obtener referencia a la ventana principal:
mywin = gui.get("mywin")
panel = mywin['panel']
grilla = panel['notebook']['tab_art']['items']


if __name__ == "__main__":
    try:
        if len(sys.argv)>1 and not sys.argv[1].startswith("-"):
            CONFIG_FILE = sys.argv[1]
        new_conf = os.path.join("conf", CONFIG_FILE)
        if not os.path.exists(CONFIG_FILE) and os.path.exists(new_conf):
            CONFIG_FILE = new_conf
        config = SafeConfigParser()
        config.read(CONFIG_FILE)
        if not len(config.sections()):
            if os.path.exists(CONFIG_FILE):
                gui.alert(u"Error al cargar configuración: %s" % CONFIG_FILE)
            else:
                gui.alert(u"No existe archivo de configuración: %s" % CONFIG_FILE)
            sys.exit(1)
        cert = config.get('WSAA','CERT')
        privatekey = config.get('WSAA','PRIVATEKEY')
        cuit_emisor = config.get('WSFEv1','CUIT')
        cat_iva_emisor = int(config.get('WSFEv1','CAT_IVA')) # 1: RI
        pto_vta_emisor = int(config.get('WSFEv1','PTO_VTA'))
        if config.has_option('WSFEv1','IVA_INCLUIDO'):
            iva_incluido = config.get('WSFEv1','IVA_INCLUIDO').lower() == "true"
        else:
            iva_incluido = False
        
        if config.has_section('FACTURA'):
            conf_fact = dict(config.items('FACTURA'))
        else:
            conf_fact = {}
        
        conf_pdf = dict(config.items('PDF'))
        conf_mail = dict(config.items('MAIL'))
          
        if config.has_option('WSAA','URL') and not HOMO:
            wsaa_url = config.get('WSAA','URL')
        else:
            wsaa_url = None

        if config.has_option('WSFEv1','URL') and not HOMO:
            wsfev1_url = config.get('WSFEv1','URL')
        else:
            wsfev1_url = None

        if config.has_option('WSFEXv1','URL') and not HOMO:
            wsfexv1_url = config.get('WSFEXv1','URL')
        else:
            wsfexv1_url = None

        if config.has_option('WS-SR-PADRON-A4','URL') and not HOMO:
            ws_sr_padron_a4_url = config.get('WS-SR-PADRON-A4', 'URL')
        else:
            ws_sr_padron_a4_url = None

        DEFAULT_WEBSERVICE = "wsfev1"
        if config.has_section('PYRECE'):
            DEFAULT_WEBSERVICE = config.get('PYRECE','WEBSERVICE')

        if config.has_section('PROXY'):
            proxy_dict = dict(("proxy_%s" % k,v) for k,v in config.items('PROXY'))
            proxy_dict['proxy_port'] = int(proxy_dict['proxy_port'])
        else:
            proxy_dict = {}

        id_factura = None

        import datos

        # inicializo los componenetes de negocio:

        padron = PadronAFIP()
        sired = SIRED()
        wsaa = WSAA()
        wsfev1 = WSFEv1()
        ta = wsaa.Autenticar("wsfe", cert, privatekey, wsaa_url, cache="cache")
        if not ta:
            gui.alert(wsaa.Excepcion, u"Imposible autenticar con WSAA AFIP")
        else:
            wsfev1.SetTicketAcceso(ta)
        wsfev1.Cuit = cuit_emisor
        wsfev1.Conectar("cache", wsfev1_url)
        # intento autenticar el servicio de padron, se usa si está disponible
        ta = wsaa.Autenticar("ws_sr_padron_a4", cert, privatekey, wsaa_url, cache="cache")
        if ta:
            padron_a4 = WSSrPadronA4()
            padron_a4.LanzarExcepciones = True
            padron_a4.SetTicketAcceso(ta)
            padron_a4.Cuit = cuit_emisor
            padron_a4.Conectar("cache", ws_sr_padron_a4_url)
        else:
            padron_a4 = None

        fepdf = FEPDF()
        # cargo el formato CSV por defecto (factura.csv)
        fepdf.CargarFormato(conf_fact.get("formato", "factura.csv"))
        # establezco formatos (cantidad de decimales) según configuración:
        fepdf.FmtCantidad = conf_fact.get("fmt_cantidad", "0.2")
        fepdf.FmtPrecio = conf_fact.get("fmt_precio", "0.2")
        # configuración general del PDF:
        fepdf.CUIT = cuit_emisor
        
        fepdf.AgregarCampo("draft", 'T', 100, 250, 0, 0,
                           size=70, rotate=45, foreground=0x808080, priority=-1)
            
        # ajustar opciones de articulos:
        if config.has_section('ARTICULOS'):
            datos.articulos = dict([(k, unicode(v, "latin1", "replace"))
                                    for k,v in config.items('ARTICULOS')])
        grilla.columns[2].choices = datos.articulos.values()
        limpiar(None)

        # agrego item de ejemplo:
        if '--prueba' in sys.argv:
            panel['cliente']['nro_doc'].value = "20-00000051-6"
            if padron_a4:
                on_nro_doc_change(None)
            panel['cliente']['cat_iva'].value = 1
            grilla.items.append({'qty': 1, 'codigo': '1111', 
            'ds': u"Honorarios  p/administración  de alquileres", 'precio': 1000., 
            'iva_id': 5, 'subtotal': 1210.})
            recalcular()

        mywin.show()
        gui.main_loop()
    except:
        ex = traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)
        msg = ''.join(ex)
        print msg
        gui.alert(msg, 'Excepcion')
