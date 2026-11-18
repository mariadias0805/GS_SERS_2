"""Leitura dos arquivos de dados de SERS (parâmetros, equipamentos e medidas).

Os caminhos são montados a partir da localização deste arquivo, então o
programa funciona em qualquer computador, de qualquer pasta.
"""
import csv
import json
import os

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(PASTA_PROJETO, "data", "sers")


def _ler_json(nome_arquivo):
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def parametros_completos():
    """Devolve o parametros.json inteiro (com fonte, status e data de cada item)."""
    return _ler_json("parametros.json")


def parametros():
    """Devolve um dicionário simples {nome: valor} com todos os parâmetros."""
    bruto = parametros_completos()
    simples = {}
    for grupo, itens in bruto.items():
        if not isinstance(itens, dict):
            continue  # ignora o texto "_leia_me"
        for nome, item in itens.items():
            if isinstance(item, dict) and "valor" in item:
                simples[nome] = item["valor"]
            else:
                simples[nome] = item  # grupo "contexto"
    return simples


def fontes_dos_parametros():
    """Lista (nome, valor, unidade, status, fonte) para mostrar as referências."""
    bruto = parametros_completos()
    linhas = []
    for grupo, itens in bruto.items():
        if not isinstance(itens, dict) or grupo == "contexto":
            continue
        for nome, item in itens.items():
            linhas.append((nome, item["valor"], item["unidade"], item["status"], item["fonte"]))
    return linhas


def equipamentos_cenario_base():
    """Lê o CSV do cenário-base e devolve uma lista de dicionários com números."""
    caminho = os.path.join(PASTA_DADOS, "equipamentos_cenario_base.csv")
    equipamentos = []
    with open(caminho, "r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            equipamentos.append({
                "id": linha["id"],
                "equipamento": linha["equipamento"],
                "quantidade": int(linha["quantidade"]),
                "potencia_w": float(linha["potencia_w"]),
                "minutos_dia": float(linha["minutos_dia"]) if linha["minutos_dia"] else None,
                "dias_mes": float(linha["dias_mes"]) if linha["dias_mes"] else None,
                "kwh_mes_direto": float(linha["kwh_mes_direto"]) if linha["kwh_mes_direto"] else None,
                "status": linha["status"],
                "fonte_potencia": linha["fonte_potencia"],
                "observacao": linha["observacao"],
            })
    return equipamentos


def medidas_eficiencia():
    """Lê as medidas da Alternativa A (eficiência)."""
    return _ler_json("medidas_eficiencia.json")["medidas"]
