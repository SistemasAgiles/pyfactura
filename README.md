pyfactura
=========

Visual application for electronic invoices (AFIP Argentina) 

Copyright 2014 by Mariano Reingart <reingart@gmail.com>

Licenced under GPLv3+

Documentation: http://www.sistemasagiles.com.ar/trac/wiki/PyFactura (spanish)


![screenshot](http://www.sistemasagiles.com.ar/trac/raw-attachment/wiki/PyFactura/aplicativo_factura_electronica_06b_ubuntu.png)

Features:
---------

 * Simple form to enter electronic invoice data (customer, dates, items, taxes)
 * Online autorization of the infoice agains AFIP (Argentina's Federal Tax Agency) 
 * PDF generation customizable with extra data, logo, barcode, etc.
 * Email sending with PDF attachment
 * Internal database (sqlite embedded, compatible with PostgreSQL, MySQL or ODBC -MSSQL Server and MS Access-)

Configuration:
--------------

rece.ini configuration example:

    [WSAA]
    CERT=reingart.crt
    PRIVATEKEY=reingart.key
    ##URL=https://wsaa.afip.gov.ar/ws/services/LoginCms

    [WSFEv1]
    CUIT=20267565393
    CAT_IVA=1
    PTO_VTA=97
    ENTRADA=entrada.txt
    SALIDA=salida.txt
    ##URL=https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL

    [FACTURA]
    ARCHIVO=tipo,letra,numero
    FORMATO=factura.csv
    DIRECTORIO=.
    PAPEL=legal
    ORIENTACION=portrait
    DIRECTORIO=.
    SUBDIRECTORIO=
    LOCALE=Spanish_Argentina.1252
    FMT_CANTIDAD=0.4
    FMT_PRECIO=0.3
    CANT_POS=izq
    ENTRADA=factura.txt
    SALIDA=factura.pdf

    [PDF]
    LOGO=logo.png
    EMPRESA=Empresa de Prueba
    MEMBRETE1=Direccion de Prueba
    MEMBRETE2=Capital Federal
    CUIT=CUIT 30-00000000-0
    IIBB=IIBB 30-00000000-0
    IVA=IVA Responsable Inscripto
    INICIO=Inicio de Actividad: 01/04/2006

    [MAIL]
    SERVIDOR=adan.nsis.com.ar
    PUERTO=25
    USUARIO=no.responder@nsis.com.ar
    CLAVE=noreplyauto123
    MOTIVO=Factura Electronica Nro. NUMERO
    CUERPO=Se adjunta Factura en formato PDF
    HTML=<b>Se adjunta <i>factura electronica</i> en formato PDF</b>
    REMITENTE=Facturador PyAfipWs <pyafipws@nsis.com.ar>


See User Manual: http://www.sistemasagiles.com.ar/trac/wiki/ManualPyAfipWs for more information


Requeriments:
-------------

 * Programming language: Python 2.5+
 * GUI toolkit: wxPython 2.8+
 * GUI framework: [gui2py](https://code.google.com/p/gui2py/) (pythoncard fork/spin-off)
 * Electronic invoice components: [pyafipws](https://code.google.com/p/pyafipws/)
 * SOAP Webservices lightweight library: [pysimplesoap](https://code.google.com/p/pysimplesoap/)
 * PDF generation lightweight library: [pyfpdf](https://code.google.com/p/pyfpdf/)

Detailed build and instalation instructions in https://code.google.com/p/pyafipws/wiki/InstalacionCodigoFuente
