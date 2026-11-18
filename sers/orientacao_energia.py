"""Orientação de energia: estende a classe Orientacao do projeto original.

A classe original (orientacao.py) guarda uma resposta fixa. A de energia herda
tudo dela e acrescenta:
  - calculo: nome da função de sers/respostas.py que monta o texto com números;
  - limitacoes: lista de avisos sobre as estimativas.
O resto (id, categoria, título, palavras-chave, fonte...) é igual, então a busca
por palavras-chave e a navegação por categorias do projeto original funcionam
sem nenhuma alteração.
"""
from orientacao import Orientacao
from sers import respostas


class OrientacaoEnergia(Orientacao):
    def __init__(self, id, categoria, titulo, palavras_chave, resposta, documentos,
                 onde, fonte, verificado_em, calculo, limitacoes):
        super().__init__(id, categoria, titulo, palavras_chave, resposta,
                         documentos, onde, fonte, verificado_em)
        self.calculo = calculo
        self.limitacoes = limitacoes

    def exibir(self):
        print(f"\n>> [{self.id}] {self.titulo} [{self.categoria}]")
        print(f"{self.resposta}")

        gerar_texto = respostas.TEXTOS.get(self.calculo)
        if gerar_texto is not None:
            try:
                for linha in gerar_texto():
                    print(linha)
            except Exception as erro:  # não derruba o assistente se um arquivo de dados quebrar
                print(f"AVISO: não consegui calcular agora ({erro}). Confira os arquivos em data/sers/.")

        if self.limitacoes:
            print("Condições e limitações:")
            for item in self.limitacoes:
                print(f"  - {item}")
        print("O que ter em mãos:")
        for doc in self.documentos:
            print(f"  - {doc}")
        print(f"Onde conferir: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("AVISO: ESTE ASSISTENTE NÃO É UM CANAL OFICIAL. Os valores são estimativas, não garantia de economia.")
