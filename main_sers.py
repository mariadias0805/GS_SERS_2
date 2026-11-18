"""Ponto de entrada do Citizen Assist AI com o módulo de energia (SERS).

Rode com:  python main_sers.py
O main.py original (disciplina de Pensamento Computacional) continua funcionando
do mesmo jeito, sem o módulo de energia.
"""
import os

from sers.assistente_sers import AssistenteSERS
from sers.base_energia import BaseConhecimentoSERS


def main():
    # Garante que os caminhos "data/..." funcionem mesmo se o programa for aberto de outra pasta.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    base = BaseConhecimentoSERS("data/base_conhecimento.json", "data/sers/base_conhecimento_energia.json")
    base.carregar()

    assistente = AssistenteSERS("Citizen Assist AI - Primeiro Emprego (com Energia e Sustentabilidade)", base)
    assistente.perguntar()


if __name__ == "__main__":
    main()
