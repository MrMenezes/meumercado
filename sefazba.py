# -*- coding: utf-8 -*-
import json
from enum import Enum
from typing import List
import requests
from bs4 import BeautifulSoup
import base64
from unicodedata import normalize
from stringcase import snakecase
import re


class TipoInfo(Enum):
    nfe = None
    emitente = 'btn_aba_emitente'
    destinatario = 'btn_aba_destinatario'
    produtos = 'btn_aba_produtos'
    totais = 'btn_aba_totais'
    transporte = 'btn_aba_transporte'
    infadicionais = 'btn_aba_infadicionais'


class SefazBa:
    def __init__(self, url):
        self.url = url
        self.url_request = self.url.replace(
            'qrcode', 'Modulos/Geral/NFCEC_consulta_abas')
        self.session = requests.Session()
        self.session.get(url)

    def getNota(self):
        nota = dict()
        nota['nfe'] = self.dinamic_colector(TipoInfo.nfe)
        nota['emitente'] = self.dinamic_colector(TipoInfo.emitente)
        nota['destinatario'] = self.dinamic_colector(TipoInfo.destinatario)
        nota['produtos'] = self.dinamic_colector(TipoInfo.produtos)
        nota['totais'] = self.dinamic_colector(TipoInfo.totais)
        nota['totais'] = self.dinamic_colector(TipoInfo.totais)
        nota['infadicionais'] = self.dinamic_colector(TipoInfo.infadicionais)
        return nota

    def base64(self):
        html_base64 = base64.b64decode(
            self.view_state).decode('utf-8', errors='replace')
        start = html_base64.find("<link")
        end = html_base64.rfind("</div>") + 6
        html_parse = html_base64[start:end]
        return BeautifulSoup(html_parse, 'html.parser')

    def save_state(self, soup):
        self.view_state = soup.find('input', id='__VIEWSTATE').get("value")
        self.event_validation = soup.find(
            'input', id='__EVENTVALIDATION').get("value")
        self.view_state_generator = soup.find(
            'input', id='__VIEWSTATEGENERATOR').get("value")

    def dinamic_colector(self, tipo: TipoInfo):
        if tipo.value is None:
            response = self.session.get(self.url_request)
        else:
            data = {
                '__VIEWSTATE': self.view_state,
                '__VIEWSTATEGENERATOR': self.view_state_generator,
                '__EVENTVALIDATION': self.event_validation,
                'hd_origem_chamada': '',
                tipo.value + '.x': '13^',
                tipo.value + '.y': '12^',
                'hid_uf_dest': ''
            }
            response = self.session.post(
                self.url_request, data=data, verify=False)
        soup = BeautifulSoup(normalize(
            "NFKD", response.text), 'html.parser')
        self.save_state(soup)

        data = dict()
        td_titulo = soup.find("td", {"class": "table-titulo-aba"})

        titulo_aba = snake(td_titulo.text)
        tds_aba = td_titulo.parent.parent.next_sibling.find_all("td")
        if len(tds_aba) > 0 or tipo != TipoInfo.produtos:
            data[titulo_aba] = dict()
            for td in tds_aba:
                if td.label is None:
                    continue
                label = snake(td.label.text)
                if "".join(td.span.get("class")).find("lin") > -1:
                    temp_span_value = td.span.text.strip()
                    # Endereço - Número
                    separator = "-" if temp_span_value.find("-") > -1 else ","
                    span_value = separator.join([va.strip()
                                                 for va in temp_span_value.split(separator)])
                else:
                    span_value = td.span.text.strip()
                data[titulo_aba][label] = span_value

            td_titulos_aba_interna = soup.find_all(
                "td", {"class": "table-titulo-aba-interna"})
            for td_titulos_interno in td_titulos_aba_interna:
                titulo_interno = snake(td_titulos_interno.text)
                tds_aba_interna = td_titulos_interno.parent.parent.next_sibling.find_all(
                    "td")
                data[titulo_interno] = dict()

                if len(tds_aba_interna) == 0 or tds_aba_interna[0].span is None or tds_aba_interna[0].label is None:
                    continue
                else:
                    for td in tds_aba_interna:
                        label = snake(td.label.text)
                        data[titulo_interno][label] = td.span.text.strip()
        else:
            data[titulo_aba] = list()
            produtos = soup.find_all(
                "td", {"class": "table_produtos"})
            for produto in produtos:
                produto_data = dict()
                for td in produto.table.find_all("td"):
                    label = snake(td.label.text)
                    produto_data[label] = td.span.text.strip()

                table_td = produto.find(
                    "table", {"class": "toggable"}).find_all("table")
                table_td_filter = table_td[:min([i if ['table-titulo-aba-interna'] == x.td.get('class') else len(
                    table_td) for i, x in enumerate(table_td)])]
                for td_titulos_interno in table_td_filter:
                    findall_td = td_titulos_interno.find_all("td")
                    tds_aba_interna = findall_td[:min([i if 'table' == x.next.name else len(
                        findall_td) for i, x in enumerate(findall_td)])]
                    for td in tds_aba_interna:
                        if td.span is None or td.label is None:
                            continue
                        label = snake(td.label.text)
                        produto_data[label] = td.span.text.strip()

                td_titulos_aba_interna = produto.find(
                    "table", {"class": "toggable"}).find_all(
                    "td", {"class": "table-titulo-aba-interna"})
                for td_titulos_interno in td_titulos_aba_interna:
                    titulo_interno = snake(td_titulos_interno.text)
                    tds_aba_interna = td_titulos_interno.parent.parent.next_sibling.find_all(
                        "td")
                    produto_data[titulo_interno] = dict()

                    if len(tds_aba_interna) == 0 or tds_aba_interna[0].span is None or tds_aba_interna[0].label is None:
                        continue
                    else:
                        for td in tds_aba_interna:
                            label = snake(td.label.text)
                            produto_data[titulo_interno][label] = td.span.text.strip(
                            )
                data[titulo_aba].append(produto_data)
        return(data)


def snake(source):
    source = source.split(":")[0].strip() if source.find(
        ":") > 0 else source.strip()
    source = re.sub(r'[\W_]+ ', '', source)
    source = re.sub(' +', ' ', source)
    return snakecase(normalize('NFKD', source.lower()).encode(
        'ASCII', 'ignore').decode('ASCII'))


url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=29200597422620001041650120002081901799884007|2|1|1|A9EB0D25898B7241D80D94FC0947A452B5091CEC'
url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=29200597422620004067650020001862161628617124|2|1|1|4F3382BF7029FC19B55AE6C0F08685AE39828057'
url = 'http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=29200573849952001120650120000916261977709247|2|1|1|524F7C982976B6433EF7DC0828D503DD50D7B828'


sefaz = SefazBa(url)
# sefaz.dinamic_colector(TipoInfo.nfe)
# data = sefaz.dinamic_colector(TipoInfo.produtos)
data = sefaz.getNota()
with open('data.json', 'w', encoding='utf-8') as fp:
    json.dump(data, fp)
