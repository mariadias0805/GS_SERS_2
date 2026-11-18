"""Testes da integração com o Citizen Assist AI (busca, exibição e arquivos originais).

Rodar, a partir da pasta citizen-assist-ai:
    python -m unittest discover -s testes/sers -v
"""
import contextlib
import csv
import hashlib
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)

from sers.base_energia import BaseConhecimentoSERS


def montar_base():
    base = BaseConhecimentoSERS(os.path.join(RAIZ, "data", "base_conhecimento.json"),
                                os.path.join(RAIZ, "data", "sers", "base_conhecimento_energia.json"))
    base.carregar()
    return base


class TestBusca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = montar_base()

    def test_categoria_de_energia_existe(self):
        self.assertIn("Energia e Sustentabilidade", self.base.categorias())

    def test_orientacoes_originais_continuam_carregadas(self):
        ids = [o.id for o in self.base.orientacoes]
        for esperado in range(1, 11):
            self.assertIn(esperado, ids)

    def test_ids_nao_se_repetem(self):
        ids = [o.id for o in self.base.orientacoes]
        self.assertEqual(len(ids), len(set(ids)))

    def test_casos_de_teste_do_csv(self):
        caminho = os.path.join(RAIZ, "testes", "sers", "casos_de_teste.csv")
        with open(caminho, encoding="utf-8", newline="") as f:
            for caso in csv.DictReader(f):
                with self.subTest(caso=caso["id"], pergunta=caso["pergunta"]):
                    resultados = self.base.buscar(caso["pergunta"])
                    if caso["id_esperado"] == "NENHUM":
                        # mesma regra do assistente: menos de 3 pontos = "não encontrei"
                        self.assertTrue(not resultados or resultados[0][0] < 3)
                    else:
                        self.assertTrue(resultados, "nenhuma orientação encontrada")
                        pontos, orientacao = resultados[0]
                        self.assertGreaterEqual(pontos, 3)
                        self.assertEqual(orientacao.id, int(caso["id_esperado"]))

    def test_toda_orientacao_de_energia_exibe_fonte_e_limitacoes(self):
        energia = self.base.por_categoria("Energia e Sustentabilidade")
        self.assertEqual(len(energia), 10)
        for o in energia:
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                o.exibir()
            texto = saida.getvalue()
            with self.subTest(orientacao=o.id):
                self.assertIn("Fonte:", texto)
                self.assertIn("estimativa", texto.lower())
                self.assertNotIn("não consegui calcular", texto)
                self.assertNotIn("Traceback", texto)

    def test_nenhuma_resposta_promete_economia_garantida(self):
        for o in self.base.por_categoria("Energia e Sustentabilidade"):
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                o.exibir()
            self.assertNotIn("economia garantida", saida.getvalue().lower().replace("não garantia de economia", ""))


class TestArquivosOriginaisIntactos(unittest.TestCase):
    def test_hashes_dos_arquivos_do_projeto_de_python(self):
        caminho = os.path.join(RAIZ, "testes", "sers", "hashes_originais.txt")
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                esperado, nome = linha.split()
                with open(os.path.join(RAIZ, nome), "rb") as arq:
                    atual = hashlib.sha256(arq.read()).hexdigest()
                with self.subTest(arquivo=nome):
                    self.assertEqual(atual, esperado, f"{nome} foi alterado!")


if __name__ == "__main__":
    unittest.main()
