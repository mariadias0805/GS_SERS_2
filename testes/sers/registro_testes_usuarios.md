# Registro dos testes com usuários (SERS)

> Registro com os resultados informados pelo grupo. Perfis e resultado das tarefas T1 a T3 (S/A/N) ainda precisam ser preenchidos. Não registre nome, CPF, telefone, e-mail ou endereço: use só "P1", "P2"... e um perfil geral.

## 1. Informações gerais

| Item | Preenchimento |
|---|---|
| Data(s) dos testes | ___/___/2026 |
| Quem aplicou | (iniciais dos integrantes) |
| Versão testada | `python main_sers.py` (commit/data: ________) |
| Local/forma | (presencial, videochamada, etc.) |
| Número de participantes | ___ (mínimo 5) |
| Público | Jovens em primeiro emprego, que já alugam ou pretendem alugar |
| Consentimento | Cada participante foi avisado de que as respostas são anônimas e aceitou participar (sim/não: ___) |

Fala inicial usada: "É um assistente que ajuda a entender e reduzir a conta de luz. Os valores são estimativas. Use sozinho(a); não vou ajudar durante as tarefas."

## 2. Situações testadas (tarefas)

| Tarefa | Situação | Onde no assistente | Resultado esperado |
|---|---|---|---|
| T1 | "Descubra quanto o chuveiro elétrico costuma gastar por mês." | Menu 1 (texto livre) | Orientação 102 com 33,75 kWh |
| T2 | "Descubra se vale mais a pena economizar energia em casa ou assinar energia solar." | Menu 1 ou categoria Energia | Orientação 104, com comparação A x B |
| T3 | "Estime quanto a assinatura solar economizaria numa conta de 150 kWh." | Menu 4 (simulador) → opção 2 | Valor estimado, com limitações |
| T4 | "Pergunte algo que você queira saber sobre energia." | Menu 1 (texto livre) | Resposta pertinente ou aviso de "não encontrei" |

## 3. Resultados por participante

Notas de 1 a 5 (1 = nada, 5 = totalmente). Em "Conseguiu?" use S (sim, sozinho), A (sim, com dúvida/releitura) ou N (não conseguiu).

| Part. | Perfil (idade, mora com quem) | T1 | T2 (preferência) | T3 (kWh usado no simulador) | T4 | Entendeu (1-5) | Saberia agir (1-5) | Linguagem (1-5) | Viu que é estimativa? | Achou que a economia é garantida? |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | (19) | (Sozinho) | Eficiência | 44,87 | Como é calculado? | 4 | 5 | 5 | Sim | Sim |
| P2 | (17) | (Mãe e irmão) | Eficiência | 97,92 | Como é calculado? | 5 | 5 | 5 | Sim | Mais ou menos |
| P3 | (18) | (Família(4)) | Eficiência | 184,00 | Por que em regiões maiores é mais caro? | 3 | 4 | 5 | Sim | Sim (achou difícil de entender) |
| P4 | (25) | (Família (4)) | Solar por assinatura | 123,77 | Como diminuir sem impactar muito? | 5 | 4 | 4 | Sim | Não tinha certeza |
| P5 | (19) | (Família(3)) | Solar por assinatura | 112,98 | O preço tende a subir ou cair com a tecnologia? | 4 | 4 | 5 | Sim | Sim |

**T2, preferência:** 3 de 5 acharam melhor economizar em casa (eficiência) e 2 de 5 preferiram assinar energia solar.

### Simulador (T3): estimativa para cada consumo informado

Calculado com `sers/calculos.py` (tarifa da Enel SP, bandeira verde, ligação bifásica assumida, mínimo faturado de 50 kWh). Valores estimados, sem garantia.

| Part. | Consumo (kWh/mês) | Conta sem assinatura | Economia/mês com 10% de desconto líquido | Faixa de economia/mês (5% a 20%) | Economia em 12 meses (10%) |
|---|---|---|---|---|---|
| P1 | 44,87 | R$ 37,09 | R$ 0,00 (consumo abaixo do mínimo de 50 kWh; não sobra energia para compensar) | R$ 0,00 | R$ 0,00 |
| P2 | 97,92 | R$ 92,57 | R$ 4,53 | R$ 2,27 a R$ 9,06 | R$ 54,36 |
| P3 | 184,00 | R$ 173,95 | R$ 12,67 | R$ 6,33 a R$ 25,34 | R$ 152,01 |
| P4 | 123,77 | R$ 117,01 | R$ 6,97 | R$ 3,49 a R$ 13,95 | R$ 83,69 |
| P5 | 112,98 | R$ 106,81 | R$ 5,95 | R$ 2,98 a R$ 11,91 | R$ 71,45 |

Observação: se algum participante escolheu outro tipo de ligação (monofásico ou trifásico), os valores mudam, porque o mínimo faturado muda (30 ou 100 kWh).

## 4. Comentários e observações

| Part. | Onde travou / o que releu | Palavra ou número que não entendeu | O que mudaria |
|---|---|---|---|
| P1 | Nos parâmetros | Nenhuma | Deixaria mais simples |
| P2 | Em lugar nenhum | Nenhuma | Nada |
| P3 | Nos números | Nenhuma | Nada |
| P4 | Em nada | Nenhuma | Acredito que nada |
| P5 | Nas medidas | Nenhuma | Talvez mais simples |

## 5. Resumo (preencher no final)

Para calcular as médias automaticamente, preencha `registro_testes_usuarios.csv` e rode `python testes/sers/resumir_testes.py`.

- Média de "entendeu": 4,2 (4, 5, 3, 5, 4)
- Média de "saberia agir": 4,4 (5, 5, 4, 4, 4)
- Média de "linguagem": 4,8 (5, 5, 5, 4, 5)
- Viram que é estimativa: 5 de 5
- Acharam que a economia é garantida: 3 de 5 (P1, P3, P5); P2 respondeu "mais ou menos" e P4 disse que não tinha certeza. Ninguém afirmou com segurança que não é garantida, apesar de todos dizerem que viram que é estimativa.
- Palavras ou números não entendidos: nenhum participante apontou.
- Principais dificuldades: parâmetros, números e medidas (P1, P3, P5); P3 teve a menor nota de compreensão (3); P1 pediu mais simplicidade e P5 sugeriu mais simples.
- Perguntas feitas no texto livre: "como é calculado?" (2 pessoas), "por que em regiões maiores é mais caro?", "como diminuir sem impactar muito?", "o preço tende a subir ou cair com a tecnologia?".
- O que funcionou bem: linguagem (média 4,8) e a percepção de que se trata de estimativa (5 de 5).
- Ajustes feitos a partir dos testes: ver `registro_ajustes.md`

## 6. Evidências anexadas

- [ ] `data/sers/atendimentos_sers.csv` gerado durante os testes (só perguntas, sem dados pessoais)
- [ ] Fotos/prints sem rosto, nome ou dados pessoais (opcional)
