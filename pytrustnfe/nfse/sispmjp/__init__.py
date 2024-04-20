# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import os
import sys
import ssl 
from pytrustnfe.xml import render_xml, sanitize_response
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key
from requests.packages.urllib3 import disable_warnings
from pytrustnfe.nfse.sispmjp.assinatura import Assinatura
from lxml import etree
from requests import Session
from zeep.transports import Transport
from zeep import Client, Settings, xsd
import logging.config
import urllib


def _render(certificado, method, **kwargs):
    path = os.path.join(os.path.dirname(__file__), "templates")
    parser = etree.XMLParser(
        remove_blank_text=True, remove_comments=True, strip_cdata=False
    )
    signer = Assinatura(certificado.pfx, certificado.password)

    xml_string_send = render_xml(path, "%s.xml" % method, True, **kwargs)

    # xml object
    xml_send = etree.fromstring(
        xml_string_send, parser=parser)

    if method == "RecepcionarLoteRps" \
        or method == "RecepcionarLoteRpsSincrono":
        for item in kwargs["nfse"]["lista_rps"]:
            reference = "rps:{0}{1}".format(
                item.get('numero'), item.get('serie'))

            xml_signed_send = signer.assina_xml(xml_send, reference)
    elif method == "CancelarNfse":
        xml_signed_send = signer.assina_xml(xml_send,"rps:%s" %str(kwargs["nfse"]["rps"]["numero"]))
    else:
        xml_signed_send = etree.tostring(xml_send)

    return xml_signed_send

def _send(certificado, method, **kwargs):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'verbose': {
                'format': '%(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'zeep.transports': {
                'level': 'DEBUG',
                'propagate': True,
                'handlers': ['console'],
            },
        }
    })
    path = os.path.join(os.path.dirname(__file__), "templates")

    if kwargs["ambiente"] == "homologacao":
        url = "https://nfsehomolog.joaopessoa.pb.gov.br:8443/sispmjp/NfseWSService"
    else:
        url = "https://sispmjp.joaopessoa.pb.gov.br:8443/sispmjp/NfseWSService"

    xml_send = kwargs["xml"]
    path = os.path.join(os.path.dirname(__file__), "templates")
    soap = render_xml(path, "SoapRequest.xml", False, False, soap_body=xml_send, method=method)

    disable_warnings()
    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)
        
    session = Session()
    session.cert = (cert, key)
    action = "http://nfse.abrasf.org.br/%s" %(method)
    transport = Transport(session=session)

    client = Client(wsdl=url + '?wsdl', transport=transport)


    response = client.service[method](xml_send)
    response, obj = sanitize_response(response)
    return {"sent_xml": str(soap), "received_xml": str(response.encode('utf-8')), "object": obj }

def xml_recepcionar_lote_rps(certificado, **kwargs):
    return _render(certificado, "RecepcionarLoteRps", **kwargs)

def recepcionar_lote_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_recepcionar_lote_rps(certificado, **kwargs)
    return _send(certificado, "RecepcionarLoteRps", **kwargs)

def xml_recepcionar_lote_rps_sincrono(certificado, **kwargs):
    return _render(certificado, "RecepcionarLoteRpsSincrono", **kwargs)

def recepcionar_lote_rps_sincrono(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_recepcionar_lote_rps(certificado, **kwargs)
    if len(kwargs["xml"]["nfse"]["lista_rps"]) > 2:
        return {}
    return _send(certificado, "RecepcionarLoteRpsSincrono", **kwargs)

def gerar_nfse(certificado, **kwargs):
    return _send(certificado, "GerarNfse", **kwargs)

def envio_lote_rps_assincrono(certificado, **kwargs):
    return _send(certificado, "RecepcionarLoteRps", **kwargs)

def envio_lote_rps(certificado, **kwargs):
    return _send(certificado, "RecepcionarLoteRpsSincrono", **kwargs)

def xml_cancelar_nfse(certificado, **kwargs):
    return _render(certificado, "CancelarNfse", **kwargs)

def cancelar_nfse(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_cancelar_nfse(certificado, **kwargs)
    response = _send(certificado, "CancelarNfse", **kwargs)
    xml = None

    try:
        #Conversão a objeto e Busca pelo elemento Nfse
        res, xml_obj = sanitize_response(response['object']['CancelarNfseResponse']['return'].text)
        #Caso haja algum erro, as mensagens serão retornadas
        if xml_obj.find(".//ListaMensagemRetorno") is not None:
            xml_obj = xml_obj.find(".//ListaMensagemRetorno")
        #Conversão de volta a string
        xml = etree.tostring(xml_obj)
        if sys.version_info[0] > 2:
            from html.parser import HTMLParser
            xml = xml.encode(str)
        else:
            from HTMLParser import HTMLParser
            xml = xml.encode('utf-8','ignore')
        #unescape
        xml = HTMLParser().unescape(xml)
    except Exception as err:
        pass

    return xml

def xml_consultar_lote_rps(certificado, **kwargs):
    return _render(certificado, "ConsultarLoteRps", **kwargs)

def consultar_lote_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_consultar_lote_rps(certificado, **kwargs)
    response = _send(certificado, "ConsultarLoteRps", **kwargs)
    xml = None

    try:
        xml_clean = re.sub(r'\<\?xml.+\?\>\n?','',response['object']['ConsultarLoteRpsResponse']['return'].text)
        res, xml_obj = sanitize_response(xml_clean)
        xml = etree.tostring(xml_obj,xml_declaration=False)
        if sys.version_info[0] > 2:
            from html.parser import HTMLParser
            xml = xml.encode(str)
        else:
            from HTMLParser import HTMLParser
            xml = xml.encode('utf-8','ignore')
        #unescape
        xml = HTMLParser().unescape(xml)
    except:
        pass

    return xml

def substituir_nfse(certificado, **kwargs):
    return _send(certificado, "SubstituirNfse", **kwargs)

def consulta_situacao_lote_rps(certificado, **kwargs):
    return _send(certificado, "ConsultaSituacaoLoteRPS", **kwargs)

def xml_consultar_nfse_por_rps(certificado, **kwargs):
    return _render(certificado, "ConsultarNfsePorRps", **kwargs)

def consultar_nfse_por_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_consultar_nfse_por_rps(certificado, **kwargs)
    response = _send(certificado, "ConsultarNfsePorRps", **kwargs)
    xml = None

    try:
        res, xml_obj = sanitize_response(response['object']['ConsultarNfsePorRpsResponse']['return'].text)
        xml_obj = xml_obj.find(".//CompNfse")
        #Conversão de volta a string
        xml = etree.tostring(xml_obj)
        if sys.version_info[0] > 2:
            from html.parser import HTMLParser
            xml = xml.encode(str)
        else:
            from HTMLParser import HTMLParser
            xml = xml.encode('utf-8','ignore')
        #unescape
        xml = HTMLParser().unescape(xml)
    except:
        pass

    return xml

def consulta_nfse_servico_prestado(certificado, **kwargs):
    return _send(certificado, "ConsultarNfseServicoPrestado", **kwargs)

def consultar_nfse_servico_tomado(certificado, **kwargs):
    return _send(certificado, "ConsultarNfseServicoTomado", **kwargs)

def consulta_nfse_faixe(certificado, **kwargs):
    return _send(certificado, "ConsultarNfseFaixa", **kwargs)

def consulta_cnpj(certificado, **kwargs):
    return _send(certificado, "ConsultaCNPJ", **kwargs)