from sefazba import SefazBa, TipoInfo
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def simple(event, context=None):
    logger.info('Event: %s', event)
    url = event["url"]
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
    result = {
        "cnpj": resumo['emitente']['cnpj'],
        "compras": compras,
        "data": resumo['dados_da_nfc_e']['data_de_emissao'],
        "local": resumo['emitente']['nomerazao_social'],
        "total": resumo['dados_da_nfc_e']['valor_total_da_nota_fiscal'],
    }
    response = {'result': result}
    return response