"""Testes automáticos dos cálculos de energia (SERS).

Rodar, a partir da pasta citizen-assist-ai:
    python -m unittest discover -s testes/sers -v

Os valores esperados foram calculados À MÃO (ver docs/sers/06_testes_e_validacao.md),
independentes do código, para provar que o programa faz a conta certa.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sers import calculos as c
from sers import dados
from sers import respostas


class TestEnergiaDeEquipamentos(unittest.TestCase):
    def test_chuveiro_4500w_15min_30dias(self):
        # 4,5 kW x 0,25 h x 30 dias = 33,75 kWh
        self.assertAlmostEqual(c.kwh_mes(4500, 15, 30), 33.75, places=6)

    def test_tv_95w_5h(self):
        # 0,095 kW x 5 h x 30 = 14,25 kWh
        self.assertAlmostEqual(c.kwh_mes(95, 300, 30), 14.25, places=6)

    def test_quantidade_multiplica(self):
        # 4 lâmpadas de 15 W, 5 h, 30 dias = 9 kWh
        self.assertAlmostEqual(c.kwh_mes(15, 300, 30, quantidade=4), 9.0, places=6)

    def test_consumo_total_do_cenario_base(self):
        # 30 + 33,75 + 14,25 + 7,2 + 7,2 + 9 + 14,4 + 6 + 12 = 133,8 kWh
        eqs = dados.equipamentos_cenario_base()
        self.assertAlmostEqual(c.consumo_total(eqs), 133.8, places=6)


class TestTarifaECusto(unittest.TestCase):
    def setUp(self):
        self.p = dados.parametros()

    def test_tarifa_sem_tributos_bandeira_verde(self):
        # (472,42 + 316,96) / 1000 = 0,78938 R$/kWh
        self.assertAlmostEqual(c.tarifa_sem_tributos(self.p), 0.78938, places=6)

    def test_bandeira_amarela_soma_1_885_por_100kwh(self):
        self.assertAlmostEqual(c.tarifa_sem_tributos(self.p, "amarela"), 0.78938 + 0.01885, places=6)

    def test_faixas_de_icms(self):
        self.assertEqual(c.aliquota_icms(80, self.p), 0.0)
        self.assertEqual(c.aliquota_icms(90, self.p), 0.0)
        self.assertEqual(c.aliquota_icms(150, self.p), 0.12)
        self.assertEqual(c.aliquota_icms(200, self.p), 0.12)
        self.assertEqual(c.aliquota_icms(250, self.p), 0.18)

    def test_tarifa_com_tributos_faixa_12(self):
        # 0,78938 / (1 - 0,12 - 0,045) = 0,945365...
        self.assertAlmostEqual(c.tarifa_com_tributos(133.8, self.p), 0.78938 / 0.835, places=6)

    def test_conta_do_cenario_base(self):
        # 133,8 x 0,945365 = 126,49
        self.assertAlmostEqual(c.custo_mensal(133.8, self.p), 126.49, places=2)


class TestAlternativas(unittest.TestCase):
    def setUp(self):
        self.p = dados.parametros()
        self.eqs = dados.equipamentos_cenario_base()
        self.medidas = dados.medidas_eficiencia()

    def test_aplicar_medidas_nao_altera_a_lista_original(self):
        antes = c.consumo_total(self.eqs)
        c.aplicar_medidas(self.eqs, self.medidas)
        self.assertAlmostEqual(c.consumo_total(self.eqs), antes, places=9)

    def test_economia_banho_10min(self):
        # (15-10) min -> 4,5 kW x (5/60) h x 30 = 11,25 kWh
        r = c.economia_de_uma_medida(self.eqs, self.medidas, "banho_10min", self.p)
        self.assertAlmostEqual(r["kwh_mes"], 11.25, places=6)

    def test_economia_led(self):
        # 4 x (15-8) W x 5 h x 30 / 1000 = 4,2 kWh
        r = c.economia_de_uma_medida(self.eqs, self.medidas, "led_8w", self.p)
        self.assertAlmostEqual(r["kwh_mes"], 4.2, places=6)

    def test_alternativa_a_consumo_e_custo(self):
        cen = {x["nome"]: x for x in c.comparar_alternativas(self.p, self.eqs, self.medidas)}
        self.assertAlmostEqual(cen["A"]["consumo_kwh_mes"], 118.35, places=6)
        self.assertAlmostEqual(cen["A"]["custo_mes"], 111.88, places=2)
        self.assertAlmostEqual(cen["A"]["economia_mes"], 14.61, places=2)

    def test_alternativa_b_com_10_por_cento(self):
        # 50 kWh x 0,945365 + 83,8 x 0,945365 x 0,9 = 118,57
        cen = {x["nome"]: x for x in c.comparar_alternativas(self.p, self.eqs, self.medidas, 0.10)}
        self.assertAlmostEqual(cen["B"]["custo_mes"], 118.57, places=2)
        self.assertAlmostEqual(cen["B"]["economia_mes"], 7.92, places=2)

    def test_todas_as_alternativas_atendem_o_mesmo_periodo(self):
        cen = c.comparar_alternativas(self.p, self.eqs, self.medidas)
        for x in cen:
            self.assertAlmostEqual(x["custo_12_meses"], x["custo_mes"] * 12, places=6)

    def test_assinatura_nao_ajuda_se_consumo_menor_que_o_minimo(self):
        r = c.custo_com_assinatura(40, self.p, 0.10)
        self.assertEqual(r["kwh_compensados"], 0)
        self.assertAlmostEqual(r["total"], c.custo_mensal(40, self.p), places=6)

    def test_desconto_para_igualar_a_eficiencia(self):
        # 14,61 / (83,8 x 0,945365) = 18,4%
        d = c.desconto_para_igualar(14.61, 133.8, self.p)
        self.assertAlmostEqual(d, 0.184, places=3)

    def test_assinatura_a_20_por_cento_supera_a_eficiencia(self):
        # coerência da recomendação: a ordem A x B muda conforme o desconto
        a = {x["nome"]: x for x in c.comparar_alternativas(self.p, self.eqs, self.medidas, 0.10)}
        b = {x["nome"]: x for x in c.comparar_alternativas(self.p, self.eqs, self.medidas, 0.20)}
        self.assertGreater(a["A"]["economia_mes"], a["B"]["economia_mes"])
        self.assertGreater(b["B"]["economia_mes"], b["A"]["economia_mes"])

    def test_preco_limite_da_lampada(self):
        r = c.economia_de_uma_medida(self.eqs, self.medidas, "led_8w", self.p)
        limite = c.preco_limite_por_unidade(r["reais_mes"], 4, 12)
        self.assertAlmostEqual(limite, 11.91, places=2)

    def test_emissoes(self):
        self.assertAlmostEqual(c.emissoes_kg_co2(100, self.p), 3.85, places=6)


class TestCoerenciaComOAssistente(unittest.TestCase):
    """Os textos do assistente têm que mostrar exatamente os números dos cálculos."""

    def test_texto_da_comparacao_traz_os_valores_calculados(self):
        p = dados.parametros()
        eqs = dados.equipamentos_cenario_base()
        medidas = dados.medidas_eficiencia()
        cen = {x["nome"]: x for x in c.comparar_alternativas(p, eqs, medidas)}
        texto = "\n".join(respostas.texto_comparacao())
        self.assertIn(respostas.moeda(cen["A"]["economia_mes"]), texto)
        self.assertIn(respostas.moeda(cen["B"]["economia_mes"]), texto)
        self.assertIn(respostas.moeda(cen["A+B"]["economia_12_meses"]), texto)

    def test_texto_do_chuveiro_traz_33_75_kwh(self):
        self.assertIn("33,75", "\n".join(respostas.texto_chuveiro()))


class TestIntegridadeDosDados(unittest.TestCase):
    def test_todo_parametro_tem_fonte_status_e_data(self):
        validos = {"oficial", "secundária", "estimativa", "assumido"}
        bruto = dados.parametros_completos()
        for grupo, itens in bruto.items():
            if grupo == "contexto" or not isinstance(itens, dict):
                continue
            for nome, item in itens.items():
                self.assertIn(item["status"], validos, nome)
                self.assertTrue(item["fonte"].strip(), nome)
                self.assertTrue(item["consulta"].strip(), nome)

    def test_todo_equipamento_tem_fonte(self):
        for eq in dados.equipamentos_cenario_base():
            self.assertTrue(eq["fonte_potencia"].strip(), eq["id"])


if __name__ == "__main__":
    unittest.main()
