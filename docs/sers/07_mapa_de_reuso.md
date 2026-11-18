# 7. Mapa de reuso: o que veio do projeto de Python e o que é novo de SERS

## Arquivos originais (Pensamento Computacional): NÃO foram alterados

Os hashes SHA-256 estão em `testes/sers/hashes_originais.txt` e são conferidos pelo teste automático.

| Arquivo original | Status | O que SERS aproveitou | Onde foi aproveitado |
|---|---|---|---|
| `orientacao.py` | Intacto | Classe `Orientacao` (id, categoria, título, palavras-chave, resposta, documentos, onde, fonte, verificado_em) | `OrientacaoEnergia` herda dela em `sers/orientacao_energia.py` (adaptação: acrescenta `calculo` e `limitacoes` e muda o `exibir()`) |
| `base_conhecimento.py` | Intacto | `normalizar`, `carregar`, `categorias`, `por_categoria`, `pontuar`, `buscar` | `BaseConhecimentoSERS` herda dela em `sers/base_energia.py` (só acrescenta o carregamento do JSON de energia) |
| `assistente.py` | Intacto | Menu, ciclo de perguntas em texto livre, navegação por categorias, aviso de dado pessoal, registro, indicadores | `AssistenteSERS` herda dele em `sers/assistente_sers.py` (adaptação: menu com opção 4, arquivos de histórico próprios) |
| `main.py` | Intacto | Estrutura de iniciar base e assistente | `main_sers.py` repete a ideia (criação do zero, baseado no original) com a base ampliada |
| `data/base_conhecimento.json` | Intacto | Formato dos campos; 10 orientações continuam carregadas | `data/sers/base_conhecimento_energia.json` segue o mesmo formato (ids 101 a 110) |
| `data/historico.json`, `data/atendimentos.csv` | Intactos (não vão no pacote) | Formato dos campos do registro | SERS grava em `data/sers/historico_sers.json` e `atendimentos_sers.csv` |
| `__pycache__/` | Ignorar | – | Está no `.gitignore` |

## Arquivos novos de SERS (criados do zero)

`main_sers.py`, `requirements.txt`, `.gitignore`, `README.md`, tudo em `sers/`, `data/sers/`, `docs/sers/` e `testes/sers/`.

## O que copiar para o repositório

Copie para dentro do repositório do Citizen Assist AI: `main_sers.py`, `README.md` (mescle com o README que já existir, mantendo a seção de SERS), `requirements.txt`, `.gitignore` e as pastas `sers/`, `data/sers/`, `docs/sers/` e `testes/sers/`. **Não precisa reenviar** os arquivos originais. **Não envie** `__pycache__/`.
