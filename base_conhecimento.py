import json
import os
from orientacao import Orientacao

ACENTOS = {
    "á": "a", "à": "a", "ã": "a", "â": "a",
    "é": "e", "ê": "e",
    "í": "i",
    "ó": "o", "õ": "o", "ô": "o",
    "ú": "u",
    "ç": "c"
}

def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-_":
        texto = texto.replace(sinal, " ")
    return " ".join(texto.split())

class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        if not os.path.exists(self.caminho):
            print(f"AVISO: ARQUIVO {self.caminho} NÃO ENCONTRADO. BASE INICIADA VAZIA.")
            self.orientacoes = []
            return
        try:
            with open(self.caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                self.orientacoes = [
                    Orientacao(
                        item["id"],
                        item["categoria"],
                        item["titulo"],
                        item["palavras_chave"],
                        item["resposta"],
                        item["documentos"],
                        item["onde"],
                        item["fonte"],
                        item["verificado_em"]
                    ) for item in dados
                ]
        except (json.JSONDecodeError, Exception) as e:
            print(f"AVISO: ERRO AO LER ARQUIVO JSON ({e}). BASE VAZIA.")
            self.orientacoes = []

    def categorias(self):
        cats = set(o.categoria for o in self.orientacoes)
        return sorted(list(cats))

    def por_categoria(self, categoria_desejada):
        return [o for o in self.orientacoes if normalizar(o.categoria) == normalizar(categoria_desejada)]

    def pontuar(self, pergunta):
        pergunta_norm = normalizar(pergunta)
        palavras_pergunta = set(pergunta_norm.split())
        resultados = []

        for o in self.orientacoes:
            pontos = 0
            # +3 pontos para cada palavra-chave da orientação encontrada na pergunta
            for pc in o.palavras_chave:
                pc_norm = normalizar(pc)
                if pc_norm in pergunta_norm:
                    pontos += 3

            # +1 ponto para cada palavra da pergunta (4+ letras) encontrada no título
            titulo_norm = normalizar(o.titulo)
            for palavra in palavras_pergunta:
                if len(palavra) >= 4 and palavra in titulo_norm:
                    pontos += 1

            if pontos > 0:
                resultados.append((pontos, o))

        resultados.sort(key=lambda x: x[0], reverse=True)
        return resultados

    def buscar(self, pergunta):
        return self.pontuar(pergunta)