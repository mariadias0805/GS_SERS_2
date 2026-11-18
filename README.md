# GS_SERS
Citizen Assist AI: assistente para jovens no primeiro emprego, com módulo de energia e sustentabilidade (SERS) que compara eficiência e solar por assinatura.
# Citizen Assist AI: assistente digital para jovens no primeiro emprego

Projeto em grupo de Ciência da Computação (FIAP). O Citizen Assist AI nasceu na disciplina de **Pensamento Computacional com Python** e agora ganhou a contribuição da **Global Solution de Soluções em Energias Renováveis e Sustentáveis (SERS)**.

## Integrantes

Ana Julia Yumi Inoue - RM: 569430
Maria Fernanda Dias Ribeiro - RM: 569999
Ulysses Gomes Soares de Souza - RM: 573826



### Público e problema

O público do assistente é o **jovem em primeiro emprego**. Muitos vão morar de aluguel e pagar a conta de luz pela primeira vez. O problema escolhido foi: **como gastar menos energia em um apartamento alugado, sem poder fazer obra nem instalar equipamentos no imóvel**.

### Objetivo

Colocar dentro do assistente orientações sobre uso consciente de energia, baseadas em cálculos feitos pelo próprio programa, com fontes e limitações, comparando duas alternativas para a mesma necessidade.

### Funcionalidades de energia

- Nova categoria **"Energia e Sustentabilidade"** com 10 orientações (ids 101 a 110), que o usuário acessa por pergunta em texto livre ou pela navegação por categorias.
- Respostas com **números calculados em Python**, fórmulas, condições, limitações, fonte e data de verificação.
- **Simulador de energia** (opção 4 do menu): consumo e custo de qualquer equipamento, e estimativa da economia da assinatura solar a partir dos kWh da conta do usuário.
- **Comparação de alternativas** e recomendação gerada por regras explícitas.
- Registro dos atendimentos em `data/sers/` (aproveitando a estrutura de histórico original).

### Análise energética

Cenário-base **estimado**: 1 morador, apartamento pequeno, área da Enel SP, 133,8 kWh por mês (chuveiro, geladeira, TV, ventilador etc.). A conta sai de: energia (kWh) × preço do kWh com tributos. Tarifa homologada pela ANEEL (REH 3.596/2026), bandeira verde de novembro/2026, ICMS por faixa de consumo e PIS/COFINS estimado. Todos os dados, com fonte e status (oficial, secundária, estimativa ou assumido), estão em `data/sers/parametros.json`.

### Alternativas comparadas (mesma necessidade, 12 meses)

- **A. Eficiência energética:** banho de 15 para 10 minutos e lâmpadas LED no lugar das fluorescentes compactas.
- **B. Energia solar por assinatura** (fonte renovável): créditos de uma usina compartilhada, sem instalar nada no apartamento.
- **A+B:** as duas juntas.

### Principais resultados (estimativas)

| Cenário | Conta/mês | Economia/mês | Economia em 12 meses |
|---|---|---|---|
| Base | R$ 126,49 | – | – |
| A. Eficiência | R$ 111,88 | R$ 14,61 | R$ 175,27 |
| B. Solar por assinatura (10% de desconto líquido) | R$ 118,57 | R$ 7,92 | R$ 95,07 |
| A+B | R$ 105,42 | R$ 21,07 | R$ 252,81 |

No caso-base a eficiência economiza mais. A assinatura só iguala a eficiência com desconto líquido de cerca de 18,4%. Em CO2 os números são pequenos (7,1 kg/ano na eficiência) porque a energia elétrica do Brasil já é bem renovável. 

### Limitações

- O cenário é uma estimativa; a conta real de cada pessoa é diferente.
- O desconto da assinatura vem de reportagem e de oferta divulgada; o contrato real pode ser outro, e as regras da geração compartilhada estão em discussão na ANEEL em 2026.
- O modelo da assinatura é simplificado (não reproduz todas as regras de ICMS nem o Fio B da Lei 14.300/2022).
- As potências dos equipamentos vêm de uma cartilha da CEMIG de 2014; os tempos de uso são premissas nossas.
- Nenhum resultado é garantia de economia.

---

## Sobre o Citizen Assist AI (projeto original)

Assistente em linha de comando que orienta jovens sobre documentos (CTPS, CPF, título de eleitor, PIS/NIS, reservista), contratos (aprendiz, estágio, conta salário) e direitos (férias, 13º, FGTS). A busca funciona por palavras-chave com pontuação e o assistente avisa quando não encontra uma resposta. Ele também bloqueia CPF, telefone e e-mail digitados e calcula indicadores de atendimento.

## Tecnologias

Python 3 (somente biblioteca padrão: `json`, `csv`, `os`, `time`, `copy`, `unittest`).

## Estrutura de pastas

```
citizen-assist-ai/
│
├── main.py                       
├── assistente.py                
├── base_conhecimento.py          
├── orientacao.py                 
│
├── main_sers.py                  
├── README.md                     
├── requirements.txt              
├── .gitignore                    
│
├── sers/                        
├── data/
│   ├── base_conhecimento.json    
│   └── sers/                    
├── docs/
│   └── sers/                     
└── testes/
    └── sers/                     

** ## Uso de IA generativa
**
Usamos IA como apoio para organizar e programar, e verificamos dados, cálculos, fontes e recomendações.
