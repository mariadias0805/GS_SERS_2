import json
import os
import time
import csv
from base_conhecimento import normalizar

class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []

    def validar_dado_pessoal(self, texto):
        if '@' in texto:
            return True
        digitos_consecutivos = 0
        for char in texto:
            if char.isdigit():
                digitos_consecutivos += 1
                if digitos_consecutivos >= 8:
                    return True
            else:
                digitos_consecutivos = 0
        return False

    def perguntar(self):
        print(f"=="*32)
        print(" Citizen Assist AI: Assistente Digital de Orientação ao Cidadão")
        print(f" Seja bem-vindo ao {self.nome}!")
        print(f"=="*32)

        while True:
            print("\nMenu Principal:")
            print("1. Fazer uma pergunta (texto livre)")
            print("2. Navegar por categorias")
            print("3. Ver indicadores e encerrar")
            opcao = input("Escolha uma opção (1-3) ou digite '0' para sair: ").strip()

            if opcao == '0' or opcao == '3':
                if opcao == '3':
                    self.indicadores()
                break
            elif opcao == '1':
                self._ciclo_pergunta()
            elif opcao == '2':
                self._navegar_categorias()
            else:
                print("OPÇÃO INVÁLIDA. Digite 1, 2, 3 ou 0.")

    def _ciclo_pergunta(self):
        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == '0':
                break
            if not pergunta:
                print("A resposta não pode ser vazia. Tente novamente.")
                continue

            if self.validar_dado_pessoal(pergunta):
                print("AVISO: NÃO DIGITE CPF, TELEFONE OU E-MAIL. REESCREVA.")
                continue

            inicio = time.time()
            resultados = self.base.buscar(pergunta)
            tempo = round(time.time() - inicio, 1)

            encontrou = len(resultados) > 0
            id_orientacao = None
            ajudou = False

            if not encontrou or resultados[0][0] < 3:
                print("\nConfiança da resposta: BAIXA / Não encontrei")
                print("Não encontrei uma orientação precisa. Tente outras palavras-chave ou navegue pelas categorias.")
                if resultados:
                    print("\nAlternativas encontradas:")
                    for pontos, o in resultados[:2]:
                        print(f" - [{o.id}] {o.titulo} (Pontos: {pontos})")
                
                self.registrar(
                    origem="pergunta",
                    pergunta=pergunta,
                    id_orientacao=None,
                    encontrou=False,
                    ajudou=False,
                    tentativas=1,
                    tempo=tempo
                )
            else:
                melhor_pontos, melhor_orientacao = resultados[0]
                id_orientacao = melhor_orientacao.id

                confianca = "ALTA" if melhor_pontos >= 6 else "MÉDIA"

                print(f"\nConfiança da resposta: {confianca} ({melhor_pontos} pontos)")
                melhor_orientacao.exibir()

                if len(resultados) > 1:
                    print("\nOutras alternativas que podem ajudar:")
                    for pontos, o in resultados[1:3]:
                        print(f" - [{o.id}] {o.titulo} ({pontos} pontos)")

                while True:
                    resp = input("Essa orientação respondeu sua dúvida? (s/n): ").strip().lower()
                    if resp in ['s', 'n']:
                        ajudou = (resp == 's')
                        break
                    print("ENTRADA INVÁLIDA. Digite (s/n).")

                self.registrar(
                    origem="pergunta",
                    pergunta=pergunta,
                    id_orientacao=id_orientacao,
                    encontrou=True,
                    ajudou=ajudou,
                    tentativas=1,
                    tempo=tempo
                )

                if ajudou:
                    print("Fico feliz em ajudar no seu primeiro emprego!")
                    break
                else:
                    continuar = input("Deseja tentar outra pergunta? (s/n): ").strip().lower()
                    if continuar != 's':
                        break

    def _navegar_categorias(self):
        while True:
            cats = self.base.categorias()
            print("\n--- Categorias Disponíveis ---")
            for i, cat in enumerate(cats, 1):
                print(f"{i}. {cat}")
            print("0. Voltar ao menu principal")

            escolha = input("Escolha uma categoria ou 0 para voltar: ").strip()
            if escolha == '0':
                break
            
            if not escolha.isdigit() or not (1 <= int(escolha) <= len(cats)):
                print("OPÇÃO INVÁLIDA. TENTE NOVAMENTE.")
                continue

            cat_escolhida = cats[int(escolha) - 1]
            orientacoes_cat = self.base.por_categoria(cat_escolhida)

            while True:
                print(f"\n--- Orientações em '{cat_escolhida}' ---")
                for i, o in enumerate(orientacoes_cat, 1):
                    print(f"{i}. {o.titulo}")
                print("0. Voltar às categorias")

                item_esc = input("Escolha o número da orientação ou 0 para voltar: ").strip()
                if item_esc == '0':
                    break
                if not item_esc.isdigit() or not (1 <= int(item_esc) <= len(orientacoes_cat)):
                    print("OPÇÃO INVÁLIDA. TENTE NOVAMENTE.")
                    continue

                o_selecionada = orientacoes_cat[int(item_esc) - 1]
                
                inicio = time.time()
                o_selecionada.exibir()
                tempo = round(time.time() - inicio, 1)

                while True:
                    resp = input("Essa orientação respondeu sua dúvida? (s/n): ").strip().lower()
                    if resp in ['s', 'n']:
                        ajudou = (resp == 's')
                        break
                    print("Entrada inválida. Digite (s/n).")

                self.registrar(
                    origem=f"categoria:{cat_escolhida}",
                    pergunta=f"Navegação: {cat_escolhida} -> {o_selecionada.titulo}",
                    id_orientacao=o_selecionada.id,
                    encontrou=True,
                    ajudou=ajudou,
                    tentativas=1,
                    tempo=tempo
                )
                break

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        atendimento = {
            "data": time.strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo": tempo
        }
        self.historico.append(atendimento)
        self._salvar_historico_json()
        self._exportar_csv_arquivo()

    def _salvar_historico_json(self):
        os.makedirs("data", exist_ok=True)
        try:
            with open("data/historico.json", "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ERRO AO SALVAR HISTORICO.JSON: {e}")

    def _exportar_csv_arquivo(self):
        os.makedirs("data", exist_ok=True)
        caminho_csv = "data/atendimentos.csv"
        try:
            existe = os.path.exists(caminho_csv)
            with open(caminho_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou", "tentativas", "tempo"])
                if not existe or os.path.getsize(caminho_csv) == 0:
                    writer.writeheader()
                writer.writerow(self.historico[-1])
        except Exception as e:
            print(f"ERRO AO EXPORTAR ATENDIMENTOS.CSV: {e}")

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("\nNenhum atendimento realizado ainda.")
            return

        encontrados = sum(1 for h in self.historico if h["encontrou"])
        ajudados = sum(1 for h in self.historico if h["ajudou"])
        tempo_total = sum(h["tempo"] for h in self.historico)
        tentativas_total = sum(h["tentativas"] for h in self.historico)

        taxa_encontro = (encontrados / total) * 100
        taxa_acerto = (ajudados / total) * 100
        tempo_medio = tempo_total / total
        tentativas_media = tentativas_total / total

        print("\n=="*10)
        print(" INDICADORES DE ATENDIMENTO")
        print("=="*10)
        print(f"Total de atendimentos: {total}")
        print(f"Resposta encontrada: {taxa_encontro:.1f}%")
        print(f"Tempo médio para encontrar: {tempo_medio:.1f} segundos")
        print(f"Taxa de acerto (ajudou): {taxa_acerto:.1f}%")
        print(f"Tentativas por atendimento: {tentativas_media:.1f}")
        
        duvidas_sem_solucao = [h["pergunta"] for h in self.historico if not h["encontrou"] or not h["ajudou"]]
        print(f"Lista de dúvidas sem solução ({len(duvidas_sem_solucao)}):")
        for d in duvidas_sem_solucao:
            print(f"  - {d}")

        while True:
            nota = input("\nAvalie a facilidade de uso do assistente (1 a 5): ").strip()
            if nota.isdigit() and 1 <= int(nota) <= 5:
                print(f"Obrigado! Nota de facilidade registrada: {nota}/5")
                break
            print("Entrada inválida. Digite um número inteiro de 1 a 5.")
        print("=="*10)