# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Endereços Simpliss Piracicaba
# Homologação: http://wshomologacao.simplissweb.com.br/nfseservice.svc
# Homologação site: http://homologacaonovo.simplissweb.com.br/Account/Login

# Prod:http://sistemas.pmp.sp.gov.br/semfi/simpliss/contrib/Account/Login
# Prod:http://sistemas.pmp.sp.gov.br/semfi/simpliss/ws_nfse/nfseservice.svc

import os
from lxml import etree
from requests import Session
from zeep.transports import Transport
from pytrustnfe.xml import render_xml, sanitize_response
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key
from pytrustnfe.nfe.assinatura import Assinatura

from datetime import datetime, timedelta
import requests 
def _render_xml(certificado, method, **kwargs):
    kwargs['method'] = method
    path = os.path.join(os.path.dirname(__file__), "templates")
    #parser = etree.XMLParser(
        #remove_blank_text=True, remove_comments=True, strip_cdata=False
    #)
    #signer = Assinatura(certificado.pfx, certificado.password)

    #referencia = ""
    xml_string_send = render_xml(path, "%s.xml" % method, True, **kwargs)
    # xml object
    #xml_send = etree.fromstring(
        #xml_string_send, parser=parser)

    #if method == "recepcionarLoteRps":
        #referencia = kwargs.get("nfse").get("numero_lote")
        #for item in kwargs["nfse"]["lista_rps"]:
            #reference = "rps:{0}{1}".format(
                #item.get('numero'), item.get('serie'))
            
            #signer.assina_xml(xml_send, reference)

        #xml_signed_send = signer.assina_xml(
             #xml_send, "lote:{0}".format(referencia))
    #else:
        #xml_signed_send = etree.tostring(xml_send)

    return xml_string_send

def _send(certificado, method, **kwargs):
    if kwargs["ambiente"] == "homologacao":
        base_url = "http://fi1.fiorilli.com.br:5663/IssWeb-ejb/IssWebWS/IssWebWS?wsdl"
    else:
        base_url = kwargs["base_url"]

    xml_send = kwargs["xml"]
    path = os.path.join(os.path.dirname(__file__), "templates")
    soap = render_xml(path, "SoapRequest.xml", False, **{"soap_body":xml_send, "method": method, "username": kwargs["nfse"]["usuario"], "password": kwargs["nfse"]["senha"] })

    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)
    session = Session()
    session.cert = (cert, key)
    session.verify = False
    action = "%s" %(method)
    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": action,
        "Content-length": str(len(soap))
    }

    request = requests.post(base_url, data=soap, headers=headers)
    response, obj = sanitize_response(request.content.decode('utf8', 'ignore'))
    return {"sent_xml": str(soap), "received_xml": str(response.encode('utf8')), "object": obj.Body }


def xml_recepcionar_lote_rps(certificado, **kwargs):
    return _render_xml(certificado, "recepcionarLoteRps", **kwargs)


def recepcionar_lote_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_recepcionar_lote_rps(certificado, **kwargs)
    return _send(certificado,"recepcionarLoteRps", **kwargs)


def xml_consultar_situacao_lote(certificado, **kwargs):
    return _render_xml(certificado, "ConsultarSituacaoLoteRps", **kwargs)


def consultar_situacao_lote(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_consultar_situacao_lote(certificado, **kwargs)
    return _send(None, "ConsultarSituacaoLoteRps", **kwargs)


def consultar_nfse_por_rps(certificado, **kwargs):
    return _send(None, "ConsultarNfsePorRps", **kwargs)


def xml_consultar_lote_rps(certificado, **kwargs):
    return _render_xml(certificado, "ConsultarLoteRps", **kwargs)


def consultar_lote_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_consultar_lote_rps(certificado, **kwargs)
    return _send(certificado, "ConsultarLoteRps", **kwargs)


def xml_consultar_nfse(certificado, **kwargs):
    return _render_xml(certificado, "ConsultarNfse", **kwargs)


def consultar_nfse(certificado, **kwargs):
    return _send("ConsultarNfse", **kwargs)


def xml_cancelar_nfse(certificado, **kwargs):
    return _render_xml(certificado, "CancelarNfse", **kwargs)


def cancelar_nfse(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_cancelar_nfse(certificado, **kwargs)
    return _send("CancelarNfse", **kwargs)


def xml_gerar_nfse(certificado, **kwargs):
    return _render_xml(certificado, "GerarNfse", **kwargs)


def gerar_nfse(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_recepcionar_lote_rps(certificado, **kwargs)
    return _send("GerarNfse", **kwargs)