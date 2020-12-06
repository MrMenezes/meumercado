from flask import Flask, json, Response
from sefazba import SefazBa, TipoInfo
app = Flask(__name__)


@app.route('/produtos/<string:p>/')
def produtos(p):
    url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=' + p
    sefaz = SefazBa(url)
    nfe = sefaz.dinamic_colector(TipoInfo.nfe)
    produtos = sefaz.dinamic_colector(TipoInfo.produtos)
    data = dict()
    data['resumo'] = nfe
    data['produtos'] = produtos
    json_string = json.dumps(data, ensure_ascii=False)
    response = Response(
        json_string, content_type="application/json; charset=utf-8")
    return response


@app.route('/totais/<string:p>/')
def totais(p):
    url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=' + p
    sefaz = SefazBa(url)
    nfe = sefaz.dinamic_colector(TipoInfo.nfe)
    produtos = sefaz.dinamic_colector(TipoInfo.totais)
    data = dict()
    data['resumo'] = nfe
    data['produtos'] = produtos
    json_string = json.dumps(data, ensure_ascii=False)
    response = Response(
        json_string, content_type="application/json; charset=utf-8")
    return response


@app.route('/nota/<string:p>/')
def nota(p):
    url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=' + p
    sefaz = SefazBa(url)
    data = sefaz.getNota()
    json_string = json.dumps(data, ensure_ascii=False)
    response = Response(
        json_string, content_type="application/json; charset=utf-8")
    return response
