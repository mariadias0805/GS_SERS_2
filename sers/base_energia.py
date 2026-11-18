"""Base de conhecimento com as orientações originais + as de energia (SERS).

BaseConhecimentoSERS herda de BaseConhecimento (base_conhecimento.py original)
e só acrescenta o carregamento do segundo arquivo JSON. Os métodos categorias(),
por_categoria(), pontuar() e buscar() são os do projeto original, sem mudanças.
"""
import json
import os

from base_conhecimento import BaseConhecimento
from sers.orientacao_energia import OrientacaoEnergia


class BaseConhecimentoSERS(BaseConhecimento):
    def __init__(self, caminho_original, caminho_energia):
        super().__init__(caminho_original)
        self.caminho_energia = caminho_energia

    def carregar(self):
        super().carregar()          # carrega as orientações do projeto de PCP
        self._carregar_energia()    # acrescenta as de energia

    def _carregar_energia(self):
        if not os.path.exists(self.caminho_energia):
            print(f"AVISO: ARQUIVO {self.caminho_energia} NÃO ENCONTRADO. SEM ORIENTAÇÕES DE ENERGIA.")
            return
        try:
            with open(self.caminho_energia, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for item in dados:
                self.orientacoes.append(OrientacaoEnergia(
                    item["id"], item["categoria"], item["titulo"], item["palavras_chave"],
                    item["resposta"], item["documentos"], item["onde"], item["fonte"],
                    item["verificado_em"], item["calculo"], item["limitacoes"]
                ))
        except (json.JSONDecodeError, KeyError) as erro:
            print(f"AVISO: ERRO AO LER {self.caminho_energia} ({erro}). SEM ORIENTAÇÕES DE ENERGIA.")
