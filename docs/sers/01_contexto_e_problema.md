# 1. Contexto, público e problema energético (SERS)

> Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis (SERS)** ao Citizen Assist AI.

## Público atendido

O Citizen Assist AI atende **jovens no primeiro emprego** (documentos, contrato, direitos). Muitos deles saem da casa dos pais para um apartamento ou kitnet **alugado** e passam a pagar a própria conta de luz pela primeira vez. Para a SERS escolhemos esse recorte: o **jovem que mora de aluguel**, sozinho, na área da **Enel SP** (Grande São Paulo).

## Necessidade energética

> **Atender os serviços de energia de um apartamento alugado pequeno gastando menos, sem poder fazer obra nem instalar equipamentos fixos no imóvel.**

Quem aluga tem duas restrições que mudam a análise: (1) não pode modificar o imóvel sem autorização do proprietário (Lei do Inquilinato, art. 23) e (2) não decide sobre a instalação elétrica do prédio. Por isso, painel solar no telhado ou aquecedor solar não são opções realistas para esse público.

## Como o assistente ajuda

O jovem pergunta em texto livre (ou usa o simulador) e recebe: quanto cada equipamento consome, quanto custa, quanto cada alternativa economiza, a recomendação com justificativa, as fontes e as limitações.

## Por que esse problema (e não outro)

Avaliamos quatro ideias:

| Ideia | Vantagem | Problema | Decisão |
|---|---|---|---|
| Reduzir a conta de luz de quem aluga (eficiência + solar por assinatura) | Realista para o público; dá para calcular em Python; tem fonte renovável viável sem obra | Depende de dados e do contrato da assinatura | **Escolhida** |
| Chuveiro elétrico x aquecedor solar de água | O chuveiro pesa muito na conta | Aquecedor solar exige instalação e autorização; não serve para inquilino | Descartada (mencionada no assistente) |
| Carregar celular com mini painel solar | Fácil de explicar | O consumo é muito pequeno; análise fraca | Descartada |
| Tarifa Branca (deslocar uso para fora do horário de ponta) | Dá para calcular | Não envolve fonte renovável | Descartada |

A ideia escolhida é fácil de explicar, usa só Python básico e permite comparar **duas alternativas para a mesma necessidade**, uma delas com fonte renovável (solar por assinatura), como o PDF exige.

## Alternativas comparadas

- **A. Eficiência energética:** banho de 15 para 10 minutos e troca das lâmpadas fluorescentes compactas por LED.
- **B. Energia solar por assinatura (geração compartilhada):** créditos de uma usina solar abatem o consumo, sem instalar nada no apartamento.
- **A+B:** as duas juntas.

Todas atendem ao **mesmo cenário** de consumo e ao **mesmo período** (12 meses). Os cálculos completos estão em `02_calculos_e_comparacao.md`.

## Dados necessários

Tarifa da Enel SP, bandeira tarifária, ICMS e PIS/COFINS, custo de disponibilidade, potência dos equipamentos, tempo de uso, desconto da assinatura e fator de emissão de CO2. Cada um está em `data/sers/parametros.json` com **fonte, status e data de consulta**. O que é estimativa está marcado como estimativa.
