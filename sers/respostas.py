"""Textos dinâmicos do módulo de energia.

Cada função devolve uma lista de linhas. Os NÚMEROS vêm sempre de
sers/calculos.py (que lê data/sers/*.json e *.csv): nada é digitado à mão.
Por isso, se um parâmetro mudar, a resposta do assistente muda junto.
"""
from sers import calculos as c
from sers import dados


def br(valor, casas=2):
    """Formata número no padrão brasileiro: 1.234,56"""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def moeda(valor):
    return "R$ " + br(valor, 2)


def moeda_kwh(valor):
    """Preço do kWh com 4 casas, para não esconder a diferença entre 0,9454 e 0,95."""
    return "R$ " + br(valor, 4)


def _contexto():
    """Carrega parâmetros, equipamentos e medidas e calcula o cenário-base."""
    params = dados.parametros()
    equipamentos = dados.equipamentos_cenario_base()
    medidas = dados.medidas_eficiencia()
    consumo_base = c.consumo_total(equipamentos)
    tarifa_base = c.tarifa_com_tributos(consumo_base, params)
    return params, equipamentos, medidas, consumo_base, tarifa_base


# --------------------------------------------------------------------------

def texto_cenario_base():
    params, eqs, medidas, consumo, tarifa = _contexto()
    linhas = ["Cenário-base: 1 morador em apartamento alugado pequeno (valores ESTIMADOS).",
              "Consumo por equipamento (kWh/mês):"]
    for eq in sorted(eqs, key=c.consumo_equipamento, reverse=True):
        kwh = c.consumo_equipamento(eq)
        linhas.append(f"  - {eq['equipamento']}: {br(kwh, 1)} kWh ({br(kwh / consumo * 100, 0)}% do total)")
    custo = c.custo_mensal(consumo, params)
    linhas += [
        f"Total: {br(consumo, 1)} kWh por mês.",
        f"Preço do kWh com tributos: {moeda_kwh(tarifa)} (distribuidora: {params['distribuidora']}, bandeira {params['bandeira_vigente']}).",
        f"Conta estimada: {moeda(custo)} por mês, ou {moeda(custo * params['horizonte_meses'])} em {params['horizonte_meses']} meses.",
        "Sua conta real pode ser diferente: use o simulador (opção 4 do menu) com os kWh da sua conta.",
    ]
    return linhas


def texto_chuveiro():
    params, eqs, medidas, consumo, tarifa = _contexto()
    chuveiro = [e for e in eqs if e["id"] == "chuveiro"][0]
    kwh = c.consumo_equipamento(chuveiro)
    custo = kwh * tarifa
    econ = c.economia_de_uma_medida(eqs, medidas, "banho_10min", params)
    return [
        f"Cálculo: {br(chuveiro['potencia_w'], 0)} W = {br(chuveiro['potencia_w'] / 1000, 1)} kW x {br(chuveiro['minutos_dia'] / 60, 2)} h/dia x {br(chuveiro['dias_mes'], 0)} dias = {br(kwh, 2)} kWh por mês.",
        f"Isso é cerca de {br(kwh / consumo * 100, 0)}% do consumo do cenário-base e custa uns {moeda(custo)} por mês.",
        f"Se o banho passar de 15 para 10 minutos: economia de {br(econ['kwh_mes'], 2)} kWh e {moeda(econ['reais_mes'])} por mês ({moeda(econ['reais_mes'] * params['horizonte_meses'])} em 12 meses).",
        "Dica extra da CEMIG (não entra no cálculo): em dias quentes, a posição 'verão' do chuveiro economiza cerca de 30%.",
        "Atenção: reduzir o tempo de banho muda um hábito. A economia só existe se o hábito mudar de verdade.",
    ]


def texto_led():
    params, eqs, medidas, consumo, tarifa = _contexto()
    econ = c.economia_de_uma_medida(eqs, medidas, "led_8w", params)
    lampadas = [e for e in eqs if e["id"] == "lampadas"][0]
    limite = c.preco_limite_por_unidade(econ["reais_mes"], lampadas["quantidade"], params["horizonte_meses"])
    antes = c.consumo_equipamento(lampadas)
    return [
        f"Cenário: {lampadas['quantidade']} lâmpadas fluorescentes compactas de 15 W acesas 5 h por dia gastam {br(antes, 1)} kWh por mês.",
        f"Trocando por LED de 8 W a economia é de {br(econ['kwh_mes'], 1)} kWh por mês, ou {moeda(econ['reais_mes'])} por mês ({moeda(econ['reais_mes'] * params['horizonte_meses'])} em 12 meses).",
        f"Preço-limite: se cada lâmpada LED custar até {moeda(limite)}, a troca se paga em 12 meses. Compare com o preço que você encontrar na loja.",
        "O grupo não colocou preço de lâmpada no cálculo porque ele varia por loja e marca.",
        "Confira os lumens na embalagem para manter a mesma iluminação. Em apartamento alugado, trocar lâmpada costuma ser permitido, mas guarde as antigas se o contrato pedir.",
    ]


def texto_comparacao():
    params, eqs, medidas, consumo, tarifa = _contexto()
    cenarios = c.comparar_alternativas(params, eqs, medidas)
    linhas = [f"Mesma necessidade (os mesmos serviços do cenário-base) e mesmo período ({params['horizonte_meses']} meses):"]
    for cen in cenarios:
        linhas.append(f"  {cen['nome']} - {cen['descricao']}")
        linhas.append(f"      {br(cen['consumo_kwh_mes'], 1)} kWh/mês | conta {moeda(cen['custo_mes'])}/mês | economia {moeda(cen['economia_mes'])}/mês ({moeda(cen['economia_12_meses'])} em 12 meses)")
    linhas.append("Quanto a assinatura solar (B) economiza, conforme o desconto líquido do contrato:")
    for s in c.sensibilidade_assinatura(params, consumo):
        linhas.append(f"  - desconto de {br(s['desconto'] * 100, 0)}%: {moeda(s['economia_mes'])}/mês ({moeda(s['economia_12_meses'])} em 12 meses)")
    fe = {cen["nome"]: cen["co2_evitado_kg_ano"] for cen in cenarios}
    linhas += [
        "Viabilidade e impacto:",
        "  - A (eficiência): sem contrato e sem obra; depende de mudar hábitos e comprar lâmpadas. Evita cerca de " + br(fe["A"], 1) + " kg de CO2 por ano.",
        "  - B (solar por assinatura): não precisa instalar nada no apartamento, mas exige contrato, conta de luz no seu nome e confiança na empresa. Associa-se a cerca de " + br(fe["B"], 1) + " kg de CO2 por ano (contabilização por créditos).",
    ]
    linhas += ["Recomendação:"] + ["  - " + r for r in c.recomendar(params, eqs, medidas)]
    return linhas


def texto_assinatura():
    params, eqs, medidas, consumo, tarifa = _contexto()
    minimo = c.disponibilidade_kwh(params)
    res = c.custo_com_assinatura(consumo, params, params["desconto_base"])
    return [
        "Como funciona: uma usina solar compartilhada injeta energia na rede. Você recebe créditos desses kWh na sua conta e paga à empresa da usina um valor com desconto. Não há painel no seu apartamento.",
        f"No cenário-base ({br(consumo, 1)} kWh/mês, ligação {params['tipo']}): o mínimo de {minimo} kWh continua na distribuidora e {br(res['kwh_compensados'], 1)} kWh seriam cobertos por créditos.",
        f"Com {br(params['desconto_base'] * 100, 0)}% de desconto líquido a conta iria de {moeda(c.custo_mensal(consumo, params))} para {moeda(res['total'])} por mês.",
        "Antes de assinar, pergunte: o desconto incide sobre qual valor? Há fidelidade ou multa? A conta precisa estar no seu nome? Os créditos aparecem na fatura da Enel?",
        "Cuidado: em 2026 a ANEEL discute mudanças nas regras da geração compartilhada (notícias do setor), então condições e descontos podem mudar. O desconto de verdade só vale o que está no contrato.",
    ]


def texto_formula():
    params, eqs, medidas, consumo, tarifa = _contexto()
    linhas = [
        "Fórmula: energia (kWh) = potência (kW) x tempo (h). Potência em watts dividida por 1000 dá kW.",
        "Exemplo: TV de 95 W ligada 5 h por dia, 30 dias: 0,095 kW x 5 h x 30 = 14,25 kWh por mês.",
        f"Custo: kWh x preço do kWh. No cenário-base o kWh sai a {moeda_kwh(tarifa)} com tributos.",
        "Consumo mensal de cada equipamento do cenário-base:",
    ]
    for eq in sorted(eqs, key=c.consumo_equipamento, reverse=True):
        linhas.append(f"  - {eq['equipamento']}: {br(c.consumo_equipamento(eq), 1)} kWh")
    linhas.append("A potência (W) fica na etiqueta do aparelho. Para o seu caso use o simulador (opção 4 do menu).")
    return linhas


def texto_co2():
    params, eqs, medidas, consumo, tarifa = _contexto()
    cenarios = {x["nome"]: x for x in c.comparar_alternativas(params, eqs, medidas)}
    fe = params["fator_emissao_kg_co2_kwh"]
    return [
        f"Fórmula: kg de CO2 = kWh x {br(fe, 4)} kg CO2/kWh (média do sistema elétrico brasileiro, MCTI, ano de 2023).",
        f"Alternativa A (eficiência): {br(cenarios['A']['co2_evitado_kg_ano'], 1)} kg de CO2 por ano a menos.",
        f"Alternativa B (solar por assinatura): {br(cenarios['B']['co2_evitado_kg_ano'], 1)} kg de CO2 por ano, se contarmos os kWh dos créditos como energia limpa.",
        "Veja que os números são pequenos: a eletricidade do Brasil já é bem renovável, então cada kWh economizado evita pouco CO2. Aqui o ganho principal é financeiro.",
        "A usina solar também tem impactos (fabricação dos painéis e uso de área), que não foram calculados.",
    ]


def texto_bandeiras():
    params, eqs, medidas, consumo, tarifa = _contexto()
    linhas = [f"Bandeira vigente (novembro/2026): {params['bandeira_vigente']}. A bandeira soma um adicional por 100 kWh consumidos.",
              f"Efeito no consumo do cenário-base ({br(consumo, 1)} kWh/mês):"]
    base = c.custo_mensal(consumo, params, "verde")
    for nome in ["verde", "amarela", "vermelha1", "vermelha2"]:
        custo = c.custo_mensal(consumo, params, nome)
        linhas.append(f"  - bandeira {nome}: {moeda(custo)} por mês (diferença para a verde: {moeda(custo - base)})")
    linhas.append("Quanto maior o consumo, maior o efeito da bandeira. Por isso reduzir kWh também protege você de bandeiras caras.")
    return linhas


def texto_locacao():
    return [
        "Em apartamento alugado, painel solar ou aquecedor solar mudam o imóvel. A Lei do Inquilinato (Lei 8.245/1991, art. 23) diz que o inquilino não pode modificar o imóvel sem consentimento prévio e por escrito do locador. Em prédio, ainda depende do condomínio.",
        "Por isso, para quem aluga, as saídas mais realistas são: (A) eficiência no dia a dia e (B) energia solar por assinatura, que não mexe no imóvel.",
        "Se o proprietário aceitar uma instalação, vale conversar e registrar por escrito. Essa análise do grupo não calcula esse caso.",
    ]


def texto_fontes():
    linhas = ["Parâmetros usados nos cálculos (status: oficial, secundária, estimativa ou assumido):"]
    for nome, valor, unidade, status, fonte in dados.fontes_dos_parametros():
        valor_txt = valor if not isinstance(valor, (list, dict)) else "(veja data/sers/parametros.json)"
        linhas.append(f"  - {nome} = {valor_txt} [{unidade}] ({status})")
        linhas.append(f"      fonte: {fonte}")
    linhas.append("Equipamentos: potências da Cartilha CEMIG 'Guia do melhor consumo' (2014). Horas de uso são premissas do grupo.")
    linhas.append("Lista completa em docs/sers/04_fontes_e_referencias.md.")
    return linhas


TEXTOS = {
    "cenario_base": texto_cenario_base,
    "chuveiro": texto_chuveiro,
    "led": texto_led,
    "comparacao": texto_comparacao,
    "assinatura": texto_assinatura,
    "formula": texto_formula,
    "co2": texto_co2,
    "bandeiras": texto_bandeiras,
    "locacao": texto_locacao,
    "fontes": texto_fontes,
}
