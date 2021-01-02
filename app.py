import os
from flask import Flask, json, Response, request, jsonify
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



@app.route('/simple', methods=['POST'])
def produto_simple():
    url = request.form['url']
    url_param = url[url.index("p=")+2:]
    url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=' + url_param
    sefaz = SefazBa(url)
    nfe = sefaz.dinamic_colector(TipoInfo.nfe)
    produtos = sefaz.dinamic_colector(TipoInfo.produtos)
    list_produtos = produtos['dados_dos_produtos_e_servicos']
    compras = []
    for produto in list_produtos:
        compras.append({
            "codigo": produto['codigo_do_produto'],
            "nome": produto['descricao'],
            "quantidade": produto['qtd_'],
            "unidade": produto['unidade_comercial'],
            "valor_unitario": produto['valor_unitario_de_comercializacao'],
            "valor": produto['valor_(r$)'],
        })
    resumo = nfe
    return jsonify({
        "cnpj": resumo['emitente']['cnpj'],
        "compras": compras,
        "data": resumo['dados_da_nfc_e']['data_de_emissao'],
        "local": resumo['emitente']['nomerazao_social'],
        "total": resumo['dados_da_nfc_e']['valor_total_da_nota_fiscal'],
    })

    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
