"""Assistente com o módulo de energia (SERS).

AssistenteSERS herda de Assistente (assistente.py original) e muda só 3 coisas:
  1. o menu ganha a opção 4, o Simulador de energia;
  2. os registros de atendimento de SERS vão para arquivos próprios
     (data/sers/historico_sers.json e data/sers/atendimentos_sers.csv),
     para não misturar com os testes da disciplina de Python;
  3. o simulador usa as funções de sers/calculos.py.
A busca por texto livre, a navegação por categorias, o aviso de dado pessoal
e os indicadores continuam sendo os do Assistente original.
"""
import csv
import json
import os
import time

from assistente import Assistente
from sers import calculos as c
from sers import dados
from sers.respostas import br, moeda, moeda_kwh, texto_comparacao

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou", "tentativas", "tempo"]


class AssistenteSERS(Assistente):

    # ---------------- menu principal (adaptado do original) ----------------
    def perguntar(self):
        print("==" * 32)
        print(" Citizen Assist AI: Assistente Digital de Orientação ao Cidadão")
        print(f" Seja bem-vindo ao {self.nome}!")
        print("==" * 32)

        while True:
            print("\nMenu Principal:")
            print("1. Fazer uma pergunta (texto livre)")
            print("2. Navegar por categorias")
            print("3. Ver indicadores e encerrar")
            print("4. Simulador de energia (SERS)")
            opcao = input("Escolha uma opção (1-4) ou digite '0' para sair: ").strip()

            if opcao == '0' or opcao == '3':
                if opcao == '3':
                    self.indicadores()
                break
            elif opcao == '1':
                self._ciclo_pergunta()
            elif opcao == '2':
                self._navegar_categorias()
            elif opcao == '4':
                self._simulador_energia()
            else:
                print("OPÇÃO INVÁLIDA. Digite 1, 2, 3, 4 ou 0.")

    # ---------------- registros em arquivos próprios de SERS ----------------
    def _salvar_historico_json(self):
        os.makedirs("data/sers", exist_ok=True)
        try:
            with open("data/sers/historico_sers.json", "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ERRO AO SALVAR HISTORICO_SERS.JSON: {e}")

    def _exportar_csv_arquivo(self):
        os.makedirs("data/sers", exist_ok=True)
        caminho_csv = "data/sers/atendimentos_sers.csv"
        try:
            existe = os.path.exists(caminho_csv)
            with open(caminho_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
                if not existe or os.path.getsize(caminho_csv) == 0:
                    writer.writeheader()
                writer.writerow(self.historico[-1])
        except Exception as e:
            print(f"ERRO AO EXPORTAR ATENDIMENTOS_SERS.CSV: {e}")

    # ---------------- simulador ----------------
    def _ler_numero(self, texto, minimo, maximo):
        """Pede um número ao usuário até ele digitar um valor válido (aceita vírgula)."""
        while True:
            bruto = input(texto).strip().replace(",", ".")
            try:
                valor = float(bruto)
            except ValueError:
                print("ENTRADA INVÁLIDA. Digite um número, por exemplo 4500 ou 0,5.")
                continue
            if valor < minimo or valor > maximo:
                print(f"VALOR FORA DO ESPERADO. Digite entre {minimo} e {maximo}.")
                continue
            return valor

    def _simulador_energia(self):
        while True:
            print("\n--- Simulador de energia (SERS) ---")
            print("1. Quanto um equipamento consome e custa por mês")
            print("2. Quanto a energia solar por assinatura poderia economizar na MINHA conta")
            print("3. Comparar eficiência x solar por assinatura (cenário-base)")
            print("0. Voltar ao menu principal")
            escolha = input("Escolha uma opção: ").strip()
            if escolha == '0':
                break
            elif escolha == '1':
                self._simular_equipamento()
            elif escolha == '2':
                self._simular_assinatura()
            elif escolha == '3':
                print()
                for linha in texto_comparacao():
                    print(linha)
                self._finalizar_simulacao("comparacao", "Simulador: comparação do cenário-base")
            else:
                print("OPÇÃO INVÁLIDA. TENTE NOVAMENTE.")

    def _simular_equipamento(self):
        params = dados.parametros()
        eqs = dados.equipamentos_cenario_base()
        potencia = self._ler_numero("Potência do aparelho em watts (veja a etiqueta): ", 1, 20000)
        minutos = self._ler_numero("Minutos de uso por dia: ", 0, 1440)
        dias = self._ler_numero("Dias de uso por mês: ", 0, 31)
        quantidade = int(self._ler_numero("Quantidade de aparelhos iguais: ", 1, 50))

        inicio = time.time()
        kwh = c.kwh_mes(potencia, minutos, dias, quantidade)
        tarifa = c.tarifa_com_tributos(c.consumo_total(eqs), params)
        custo = kwh * tarifa
        co2 = c.emissoes_kg_co2(kwh, params)
        print(f"\nConta: {br(potencia, 0)} W = {br(potencia / 1000, 3)} kW x {br(minutos / 60, 2)} h/dia x {br(dias, 0)} dias x {quantidade} = {br(kwh, 2)} kWh por mês")
        print(f"Custo estimado: {moeda(custo)} por mês, usando o kWh a {moeda_kwh(tarifa)} (cenário-base, com tributos).")
        print(f"Em 12 meses: {moeda(custo * params['horizonte_meses'])} e {br(co2 * params['horizonte_meses'], 1)} kg de CO2 associados.")
        print("Estimativa: sua conta real pode ter outra faixa de ICMS e outra bandeira.")
        self._finalizar_simulacao("equipamento", f"Simulador: equipamento de {br(potencia, 0)} W", inicio)

    def _simular_assinatura(self):
        params = dados.parametros()
        consumo = self._ler_numero("Consumo mensal da sua conta, em kWh: ", 1, 5000)
        print("Tipo de ligação (veja na conta): 1) monofásico  2) bifásico  3) trifásico")
        tipo_num = int(self._ler_numero("Escolha 1, 2 ou 3: ", 1, 3))
        params["tipo"] = ["monofasico", "bifasico", "trifasico"][tipo_num - 1]

        inicio = time.time()
        base = c.custo_mensal(consumo, params)
        minimo = c.disponibilidade_kwh(params)
        print(f"\nSem assinatura: {moeda(base)} por mês (kWh com tributos a {moeda_kwh(c.tarifa_com_tributos(consumo, params))}).")
        if consumo <= minimo:
            print(f"Seu consumo ({br(consumo, 0)} kWh) é menor ou igual ao mínimo faturado ({minimo} kWh). Não sobra energia para compensar: a assinatura não ajuda.")
        else:
            print(f"Mínimo que continua na distribuidora: {minimo} kWh. Energia que poderia vir de créditos: {br(consumo - minimo, 1)} kWh.")
            for s in c.sensibilidade_assinatura(params, consumo):
                print(f"  - desconto líquido de {br(s['desconto'] * 100, 0)}%: conta de {moeda(s['custo_mes'])}, economia de {moeda(s['economia_mes'])}/mês ({moeda(s['economia_12_meses'])} em 12 meses)")
            print("Estimativa. Confirme no contrato o desconto líquido, a fidelidade e se a conta precisa estar no seu nome.")
        self._finalizar_simulacao("assinatura", f"Simulador: assinatura solar com {br(consumo, 0)} kWh", inicio)

    def _finalizar_simulacao(self, tipo, descricao, inicio=None):
        """Pergunta se ajudou e registra no histórico (mesma lógica do assistente original)."""
        tempo = round(time.time() - inicio, 1) if inicio is not None else 0.0
        while True:
            resp = input("Essa simulação ajudou? (s/n): ").strip().lower()
            if resp in ['s', 'n']:
                ajudou = (resp == 's')
                break
            print("ENTRADA INVÁLIDA. Digite (s/n).")
        self.registrar(origem=f"simulador:{tipo}", pergunta=descricao, id_orientacao=None,
                       encontrou=True, ajudou=ajudou, tentativas=1, tempo=tempo)
