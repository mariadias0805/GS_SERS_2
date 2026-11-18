# Cálculos e comparação das alternativas (SERS)

> Este arquivo é GERADO por `python -m sers.gerar_relatorio` a partir de `data/sers/` e `sers/calculos.py`. Não edite à mão: mude os dados e gere de novo.

Data de referência dos dados: 2026-11-17. Distribuidora: Enel Distribuição São Paulo (Enel SP).

## 1. Necessidade e período de referência

**Necessidade:** atender os serviços de energia de um apartamento alugado de 1 morador (cenário-base abaixo), com o mesmo conforto, durante **12 meses**. As duas alternativas e a combinação são comparadas para essa mesma necessidade e esse mesmo período.

## 2. Fórmulas

| O que calcula | Fórmula | Unidades |
|---|---|---|
| Energia de um equipamento | E = P × t × dias × quantidade | P em kW (watts ÷ 1000), t em h/dia, E em kWh/mês |
| Preço do kWh sem impostos | T = (TUSD + TE) ÷ 1000 + adicional da bandeira ÷ 100 | TUSD e TE em R$/MWh; bandeira em R$/100 kWh |
| Preço do kWh com impostos | Tc = T ÷ (1 − ICMS − PIS/COFINS) | ICMS depende da faixa de consumo; os impostos são "por dentro" |
| Conta mensal | Custo = E_total × Tc | R$/mês |
| Assinatura solar | Custo = mínimo × Tc + (E_total − mínimo) × Tc × (1 − d) | mínimo = custo de disponibilidade (kWh); d = desconto líquido |
| Emissões | CO2 = E × FE | FE em kg CO2/kWh |

## 3. Dados e premissas

| Parâmetro | Valor | Status | Fonte |
|---|---|---|---|
| tusd_r_mwh | 472.42 (R$/MWh) | oficial | ANEEL, Resolução Homologatória 3.596/2026 (vigente desde 04/07/2026); tabela publicada pela Enel SP em https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html |
| te_r_mwh | 316.96 (R$/MWh) | oficial | ANEEL, Resolução Homologatória 3.596/2026; Enel SP (mesma página da TUSD). Tarifa B1 residencial convencional. |
| bandeira_vigente | verde (bandeira) | oficial | ANEEL manteve a bandeira verde em novembro/2026 (anúncio de 30/10/2026, Agência Brasil: https://imirante.com/noticias/brasil/2026/10/30/aneel-mantem-bandeira-tarifaria-verde-novembro) |
| bandeiras_acrescimo_r_100kwh | ver `parametros.json` (R$ por 100 kWh) | oficial | Valores citados em reportagens de out/2026 sobre a bandeira de novembro (SBT News: https://sbtnews.sbt.com.br/noticia/economia/aneel-mantem-bandeira-verde-na-conta-de-luz-em-novembro). Conferir no site da ANEEL. |
| icms_faixas_sp | ver `parametros.json` (alíquota por faixa do consumo mensal total da conta) | secundária | Isenção até 90 kWh: Lei estadual SP 12.185/2006 (https://www.al.sp.gov.br/repositorio/legislacao/lei/2006/lei-12185-05.01.2006.html). 12% entre 91 e 200 kWh: NetCPA (https://netcpa.com.br/colunas/contas-de-energia-sofrem-queda-no-preco-devido-a-diminuicao-do-icms-pelo-governo-federal/14697). 18% acima de 200 kWh: Teletime, 27/06/2022 (https://teletime.com.br/27/06/2022/sao-paulo-reduz-icms-sobre-telecom-energia-e-combustiveis-para-18/). CONFERIR na linha de ICMS da conta real. |
| pis_cofins | 0.045 (fração do valor da conta) | estimativa | Varia todo mês. Em três faturas residenciais de março/2026 (de outra distribuidora, publicadas no portal da Câmara dos Deputados) o PIS/COFINS ficou entre 4,1% e 4,5% do valor. Usamos 4,5%. CONFERIR na conta real. |
| cosip_reais | 0.0 (R$/mês) | assumido | A contribuição de iluminação pública é municipal e igual em todas as alternativas, então não muda a comparação. Ficou em zero. Some o valor da sua conta se quiser o total. |
| tipo | bifasico (monofasico, bifasico ou trifasico) | assumido | Assumimos bifásico porque o chuveiro de 4500 W costuma ser ligado em 220 V. Veja o tipo de fornecimento na sua conta. |
| custo_disponibilidade_kwh | ver `parametros.json` (kWh/mês) | oficial | ANEEL, Resolução Normativa 1.000/2021 (consumo mínimo faturado, o 'custo de disponibilidade'): https://www.gov.br/aneel |
| desconto_cenarios | ver `parametros.json` (fração) | estimativa | A Folha Vitória cita desconto médio de 10% a 20% na energia por assinatura (https://www.folhavitoria.com.br/economia/energia-alugada-reduz-conta-em-20; a data da reportagem não foi confirmada, o grupo deve conferir). Uma oferta divulgada em 10/2026 anuncia 15% (https://www.em.com.br/mundo-corporativo/2026/10/7526277-energia-solar-por-assinatura-e-confiavel-veja-como-funciona.html). O valor de 5% é um cenário pessimista criado pelo grupo, sem fonte. O desconto REAL depende do contrato. |
| desconto_base | 0.1 (fração) | estimativa | Escolhemos o extremo mais baixo da faixa citada (10%) como caso-base, por prudência. É o desconto líquido, já considerando tudo que continua vindo na conta da distribuidora. |
| fator_emissao_kg_co2_kwh | 0.0385 (kg CO2/kWh) | secundária | MCTI: média do SIN em 2023 = 38,5 kg CO2/MWh (reportado em https://eixos.com.br/brasil-tem-menor-taxa-de-emissao-de-carbono-na-geracao-eletrica-em-onze-anos/). Em 2025 os fatores mensais ficaram entre 21,5 e 28,9 kg/MWh (jan-abr, MCTI). Usamos o valor mais alto, o de 2023. |

Significado do status: **oficial** = publicado por órgão oficial; **secundária** = reportado por notícia ou artigo a partir de dado oficial; **estimativa** = valor estimado com justificativa; **assumido** = premissa do grupo.

## 4. Cenário-base (consumo)

| Equipamento | Qtd | Potência (W) | Uso | kWh/mês | % | Status |
|---|---|---|---|---|---|---|
| Chuveiro elétrico 4500 W | 1 | 4.500 | 15 min/dia, 30 dias | 33,75 | 25% | estimativa |
| Geladeira 1 porta frost free | 1 | 80 | consumo mensal da tabela | 30,00 | 22% | tabela |
| Ventilador de teto | 1 | 120 | 240 min/dia, 30 dias | 14,40 | 11% | estimativa |
| TV LED 32 pol | 1 | 95 | 300 min/dia, 30 dias | 14,25 | 11% | estimativa |
| Forno micro-ondas | 1 | 1.200 | 20 min/dia, 30 dias | 12,00 | 9% | estimativa |
| Lâmpada fluorescente compacta 15 W | 4 | 15 | 300 min/dia, 30 dias | 9,00 | 7% | estimativa |
| Notebook | 1 | 30 | 480 min/dia, 30 dias | 7,20 | 5% | estimativa |
| Roteador wi-fi | 1 | 10 | 1.440 min/dia, 30 dias | 7,20 | 5% | estimativa |
| Máquina de lavar roupa | 1 | 500 | 60 min/dia, 12 dias | 6,00 | 4% | estimativa |
| **Total** | | | | **133,80** | 100% | |

Faixa de ICMS aplicada: 12% (consumo entre 91 e 200 kWh).
Preço do kWh: (472,42 + 316,96) ÷ 1000 = R$ 0,78938 sem impostos; com impostos: 0,78938 ÷ (1 − 0,12 − 0,045) = **R$ 0,9454**.
Conta do cenário-base: 133,80 × 0,9454 = **R$ 126,49 por mês** (R$ 1.517,88 em 12 meses).

## 5. Alternativa A: eficiência energética

- **Reduzir o banho de 15 para 10 minutos por dia**: economiza 11,25 kWh e R$ 10,64 por mês. Fonte: Cartilha CEMIG (2014): 'um bom banho não necessita mais que dez minutos'. Muda um hábito: existe pequena perda de conforto. Não exige compra.
- **Trocar as 4 lâmpadas fluorescentes compactas de 15 W por LED de 8 W**: economiza 4,20 kWh e R$ 3,97 por mês. Fonte: Cartilha CEMIG (2014), tabela de consumo: fluorescente compacta 15 W e LED 8 W. Confira os lumens na embalagem para manter a mesma iluminação. O preço das lâmpadas depende da loja. O grupo deve pesquisar e informar. Enquanto isso o assistente mostra o preço-limite.

Preço-limite da lâmpada LED para pagar a troca em 12 meses: R$ 3,97 × 12 ÷ 4 = **R$ 11,91 por lâmpada**. (O grupo não inventou preço de produto: ao pesquisar na loja, compare com esse limite.)

Resultado da alternativa A: consumo de 118,35 kWh/mês, conta de R$ 111,88, economia de **R$ 14,61/mês** (R$ 175,27 em 12 meses).

## 6. Alternativa B: energia solar por assinatura (fonte renovável)

Tipo de ligação assumido: bifasico (custo de disponibilidade = 50 kWh/mês). Energia coberta por créditos: 133,80 − 50 = 83,80 kWh.

| Desconto líquido | Conta mensal | Economia/mês | Economia em 12 meses |
|---|---|---|---|
| 5% | R$ 122,53 | R$ 3,96 | R$ 47,53 |
| 10% | R$ 118,57 | R$ 7,92 | R$ 95,07 |
| 15% | R$ 114,61 | R$ 11,88 | R$ 142,60 |
| 20% | R$ 110,65 | R$ 15,84 | R$ 190,13 |

Caso-base escolhido: 10% (extremo inferior da faixa de 10% a 20% citada em reportagem). Resultado: conta de R$ 118,57, economia de **R$ 7,92/mês**.

## 7. Comparação final (mesma necessidade, 12 meses)

| Cenário | kWh/mês | Conta/mês | Conta em 12 meses | Economia/mês | Economia em 12 meses | CO2 (kg/ano) |
|---|---|---|---|---|---|---|
| Base: Situação atual, sem mudanças | 133,8 | R$ 126,49 | R$ 1.517,88 | R$ 0,00 | R$ 0,00 | 0,0 |
| A: Eficiência (banho de 10 min + lâmpadas LED) | 118,3 | R$ 111,88 | R$ 1.342,61 | R$ 14,61 | R$ 175,27 | 7,1 |
| B: Solar por assinatura (10% de desconto líquido) | 133,8 | R$ 118,57 | R$ 1.422,81 | R$ 7,92 | R$ 95,07 | 38,7 |
| A+B: Eficiência + solar por assinatura | 118,3 | R$ 105,42 | R$ 1.265,07 | R$ 21,07 | R$ 252,81 | 38,7 |

Desconto líquido que a assinatura precisaria ter para igualar a eficiência: R$ 14,61 ÷ (83,8 kWh × 0,9454) = **18,4%**.

**Recomendação gerada pelo código (`calculos.recomendar`):**

- Comece pela eficiência (Alternativa A): no caso-base ela economiza mais que a assinatura solar e não exige contrato.
- A assinatura solar pode ser somada depois (A+B), desde que o desconto líquido seja comprovado e o contrato não tenha fidelidade longa. Para a assinatura sozinha igualar a eficiência, o desconto líquido precisaria ser de cerca de 18,4%.
- Todos os valores são estimativas e podem mudar com a tarifa, o consumo real e o contrato.

## 8. Bandeira tarifária (sensibilidade)

| Bandeira | Conta/mês do cenário-base | Diferença para a verde |
|---|---|---|
| verde | R$ 126,49 | R$ 0,00 |
| amarela | R$ 129,51 | R$ 3,02 |
| vermelha1 | R$ 133,64 | R$ 7,15 |
| vermelha2 | R$ 139,11 | R$ 12,62 |

## 9. Impacto ambiental

FE = 0,0385 kg CO2/kWh. A: (133,80 − 118,35) × FE × 12 = 7,1 kg/ano. B: 83,80 × FE × 12 = 38,7 kg/ano (contabilização por créditos). Em A+B os kWh evitados e os kWh de créditos somam o mesmo total de B, por isso o valor é igual ao de B.
Os números são pequenos porque a eletricidade brasileira já é majoritariamente renovável: o ganho principal das duas alternativas é financeiro. Impactos de fabricação dos painéis e uso de área da usina não foram calculados.

## 10. Limitações

- O cenário-base é uma estimativa para 1 morador. Os dados de potência vêm de uma cartilha da CEMIG de 2014; os tempos de uso são premissas do grupo.
- O preço do kWh usa a tarifa B1 convencional da Enel SP (REH 3.596/2026). ICMS e PIS/COFINS são aproximados e variam; confira na sua conta.
- O modelo da assinatura é simplificado: o desconto é tratado como líquido e não reproduz as regras detalhadas de ICMS sobre a energia compensada nem a cobrança gradual do Fio B da Lei 14.300/2022.
- O desconto da assinatura vem de uma reportagem (10% a 20%) e de uma oferta divulgada; o valor de 5% é cenário pessimista do grupo. As regras da geração compartilhada estão em discussão na ANEEL em 2026.
- A economia da eficiência depende de mudança de hábito (banho) e do preço das lâmpadas, que não foi inventado.
- O cenário não considera inflação, reajustes futuros de tarifa nem a fidelidade e multas de contratos.
- Nenhum resultado aqui é promessa de economia.
