# 6. Testes e validação

## 6.1 Testes automáticos (já existem; o grupo só precisa rodar)

```
python -m unittest discover -s testes/sers -v
```

Resultado esperado: `Ran 31 tests ... OK`.

| Grupo | O que verifica |
|---|---|
| Energia de equipamentos | Ex.: chuveiro 4,5 kW × 0,25 h × 30 dias = 33,75 kWh; total do cenário = 133,8 kWh |
| Tarifa e custo | (472,42 + 316,96) ÷ 1000 = 0,78938; faixas de ICMS; conta de R$ 126,49 |
| Alternativas | Economia do banho (11,25 kWh) e do LED (4,2 kWh); conta de A e B; desconto de equilíbrio de 18,4%; a ordem A × B muda com o desconto |
| Coerência | O texto do assistente contém os valores calculados |
| Dados | Todo parâmetro tem fonte, status e data |
| Busca | 14 perguntas de energia, 3 de regressão (projeto original) e 3 sem correspondência (`casos_de_teste.csv`) |
| Originais | Hash SHA-256 dos arquivos do projeto de Python (provam que não foram alterados) |

Os valores esperados dos testes foram calculados à mão, não copiados da saída do programa.

## 6.2 Teste manual do assistente (o grupo executa e anota)

Rodar `python main_sers.py` e conferir:

| # | Ação | Resultado esperado | Aprovado quando |
|---|---|---|---|
| M1 | Opção 1, "Quanto o chuveiro consome?" | Orientação 102 com 33,75 kWh | Mostra fórmula, número, limitações e fonte |
| M2 | Opção 1, "Receita de bolo" | "Não encontrei" | Não inventa resposta |
| M3 | Opção 2, categoria "Energia e Sustentabilidade" | Lista as 10 orientações | Todas abrem sem erro |
| M4 | Opção 4 → 1 com 1200 W, 20 min, 30 dias | 12,00 kWh e R$ 11,34 aprox. | Confere com a conta feita à mão |
| M5 | Opção 4 → 2 com 40 kWh | Avisa que não sobra energia para compensar | Não mostra economia |
| M6 | Digitar letra em vez de número no simulador | Pede de novo | Não trava |
| M7 | Opção 3 (indicadores) | Mostra totais | Usa os registros de SERS |

## 6.3 Testes com usuários (o grupo PRECISA fazer; nada foi feito por nós)

O PDF exige registrar **situações testadas, comentários recebidos e ajustes realizados**, sem dados pessoais desnecessários.

1. Chamar pelo menos 5 pessoas do público (jovens que já alugam, ou que pretendem alugar).
2. Seguir `roteiro_teste_usuarios.md`.
3. Preencher `registro_testes_usuarios.md` (use apelidos ou "Participante 1", sem nome, CPF ou telefone).
4. Fazer pelo menos 2 ajustes de verdade e registrar em `registro_ajustes.md`, com o "antes" e o "depois".
5. Guardar o `data/sers/atendimentos_sers.csv` gerado nos testes como evidência (ele só tem perguntas, sem dados pessoais; o assistente bloqueia CPF, telefone e e-mail).

## 6.4 Problemas que encontramos no código original e como foram tratados

| Problema | Onde | Tratamento |
|---|---|---|
| O histórico de SERS se misturaria com os testes de Python | `assistente.py` grava sempre em `data/historico.json` | `AssistenteSERS` grava em `data/sers/historico_sers.json` e `atendimentos_sers.csv` |
| `historico.json` é reescrito do zero a cada execução (só o CSV acumula) | `assistente.py`, `_salvar_historico_json` | Não alteramos (preservar o original). Use o CSV como registro oficial dos testes. |
| O campo `tempo` quase sempre fica 0,0 | `assistente.py` | Não alteramos. Não usem esse indicador como evidência forte. |
| A busca usa trecho de palavra ("led" dentro de outra palavra pode dar acerto falso) | `base_conhecimento.py`, `pontuar` | Mantida. Escolhemos palavras-chave específicas e testamos 20 perguntas. |
