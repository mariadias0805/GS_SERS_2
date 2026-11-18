# 5. Integração com o Citizen Assist AI

A contribuição de energia **não é um programa separado**: ela entra no assistente que já existia, reaproveitando a busca por palavras-chave, as categorias e o histórico.

## Fluxo de uma pergunta

```
Usuário digita: "Qual opção apresenta melhor custo-benefício?"
   |
   v
main_sers.py  -> cria BaseConhecimentoSERS e AssistenteSERS
   |
   v
Assistente._ciclo_pergunta()          (assistente.py, original)
   |  chama base.buscar(pergunta)
   v
BaseConhecimento.pontuar()            (base_conhecimento.py, original)
   |  +3 por palavra-chave encontrada, +1 por palavra do título
   v
Melhor orientação: id 104 (OrientacaoEnergia)
   |  chama orientacao.exibir()
   v
sers/orientacao_energia.py -> sers/respostas.py -> sers/calculos.py
   |  lê data/sers/parametros.json, equipamentos_cenario_base.csv, medidas_eficiencia.json
   v
Resposta com números calculados + limitações + fonte
   |
   v
Assistente.registrar()  -> data/sers/historico_sers.json e atendimentos_sers.csv
```

## O que cada arquivo novo faz

| Arquivo | Função |
|---|---|
| `main_sers.py` | Ponto de entrada. Carrega a base (original + energia) e abre o menu. |
| `sers/base_energia.py` | `BaseConhecimentoSERS` herda de `BaseConhecimento` e carrega também o JSON de energia. |
| `sers/orientacao_energia.py` | `OrientacaoEnergia` herda de `Orientacao`; no lugar de uma resposta fixa, chama uma função que calcula. |
| `sers/respostas.py` | Monta os textos (linhas) com os números vindos de `calculos.py`. |
| `sers/calculos.py` | Todas as contas: energia, tarifa, custo, alternativas, CO2. Sem `print`/`input`. |
| `sers/dados.py` | Lê os arquivos de `data/sers/`. |
| `sers/assistente_sers.py` | `AssistenteSERS` herda de `Assistente`: adiciona a opção 4 (simulador) e grava o histórico em arquivos próprios. |
| `sers/gerar_relatorio.py` | Gera `docs/sers/02_calculos_e_comparacao.md` com os mesmos números. |
| `data/sers/base_conhecimento_energia.json` | 10 orientações da categoria "Energia e Sustentabilidade" (ids 101 a 110), no mesmo formato do JSON original. |

## Por que herança?

Como `OrientacaoEnergia` é uma `Orientacao` (e `BaseConhecimentoSERS` é uma `BaseConhecimento`), o código original funciona com os objetos novos **sem ser editado**. Isso mostra o conceito de herança e polimorfismo da disciplina de Python.

## Coerência entre cálculos e respostas

As respostas nunca têm números digitados à mão: tudo sai de `calculos.py`. Os testes (`testes/sers/test_calculos.py`) conferem valores calculados à mão e verificam que o texto do assistente traz os mesmos números.

## Perguntas que o assistente responde

Veja `testes/sers/casos_de_teste.csv`. Exemplos: reduzir consumo, consumo de um equipamento, chuveiro, LED, energia solar como alternativa, melhor custo-benefício, painel solar em imóvel alugado, bandeira tarifária, CO2 e fontes.
