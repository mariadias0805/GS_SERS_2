"""Cálculos de energia da contribuição de SERS.

Só Python básico: funções que recebem números e devolvem números.
Nenhuma função aqui usa print() nem input(): isso facilita os testes
automáticos e deixa claro de onde vêm os resultados que o assistente mostra.

Fórmulas principais (todas aparecem em docs/sers/02_calculos_e_comparacao.md):
    E (kWh/mês) = P (kW) x t (h/dia) x dias        -> energia de um equipamento
    tarifa c/ tributos = (TUSD + TE + bandeira) / (1 - ICMS - PIS/COFINS)
    custo (R$) = consumo (kWh) x tarifa c/ tributos
    emissões (kg CO2) = energia (kWh) x fator de emissão (kg CO2/kWh)
"""
import copy

# --------------------------------------------------------------------------
# 1) Energia de equipamentos
# --------------------------------------------------------------------------

def kwh_mes(potencia_w, minutos_dia, dias_mes, quantidade=1):
    """Energia mensal de um equipamento: E = P(kW) x horas/dia x dias x quantidade."""
    potencia_kw = potencia_w / 1000
    horas_dia = minutos_dia / 60
    return quantidade * potencia_kw * horas_dia * dias_mes


def consumo_equipamento(eq):
    """kWh/mês de um item do cenário-base (usa o valor direto da tabela, se existir)."""
    if eq["kwh_mes_direto"] is not None:
        return eq["kwh_mes_direto"] * eq["quantidade"]
    return kwh_mes(eq["potencia_w"], eq["minutos_dia"], eq["dias_mes"], eq["quantidade"])


def consumo_total(equipamentos):
    """Soma o consumo mensal (kWh) de todos os equipamentos."""
    return sum(consumo_equipamento(eq) for eq in equipamentos)


# --------------------------------------------------------------------------
# 2) Tarifa e custo
# --------------------------------------------------------------------------

def aliquota_icms(consumo_kwh, params):
    """Alíquota de ICMS pela faixa de consumo mensal (regra de SP, ver parametros.json)."""
    for faixa in params["icms_faixas_sp"]:
        if consumo_kwh <= faixa["ate_kwh"]:
            return faixa["aliquota"]
    return params["icms_faixas_sp"][-1]["aliquota"]


def tarifa_sem_tributos(params, bandeira=None):
    """TUSD + TE (R$/kWh) mais o adicional da bandeira, ainda sem impostos."""
    if bandeira is None:
        bandeira = params["bandeira_vigente"]
    base = (params["tusd_r_mwh"] + params["te_r_mwh"]) / 1000
    adicional = params["bandeiras_acrescimo_r_100kwh"][bandeira] / 100
    return base + adicional


def tarifa_com_tributos(consumo_kwh, params, bandeira=None):
    """Preço do kWh com ICMS e PIS/COFINS 'por dentro': tarifa / (1 - alíquotas)."""
    aliquotas = aliquota_icms(consumo_kwh, params) + params["pis_cofins"]
    return tarifa_sem_tributos(params, bandeira) / (1 - aliquotas)


def custo_mensal(consumo_kwh, params, bandeira=None):
    """Conta mensal da distribuidora para um consumo (kWh), sem assinatura."""
    return consumo_kwh * tarifa_com_tributos(consumo_kwh, params, bandeira) + params["cosip_reais"]


# --------------------------------------------------------------------------
# 3) Alternativa A: eficiência energética
# --------------------------------------------------------------------------

def aplicar_medidas(equipamentos, medidas, ids_das_medidas=None):
    """Devolve uma CÓPIA dos equipamentos com as medidas aplicadas.

    A lista original nunca é alterada (copy.deepcopy), assim o cenário-base
    continua disponível para comparação.
    """
    novos = copy.deepcopy(equipamentos)
    for medida in medidas:
        if ids_das_medidas is not None and medida["id"] not in ids_das_medidas:
            continue
        for eq in novos:
            if eq["id"] == medida["equipamento_id"]:
                eq[medida["campo"]] = medida["valor_novo"]
    return novos


def economia_de_uma_medida(equipamentos, medidas, id_medida, params):
    """Quanto UMA medida economiza sozinha (kWh/mês e R$/mês)."""
    antes = consumo_total(equipamentos)
    depois_eqs = aplicar_medidas(equipamentos, medidas, [id_medida])
    depois = consumo_total(depois_eqs)
    economia_kwh = antes - depois
    economia_reais = custo_mensal(antes, params) - custo_mensal(depois, params)
    return {"id": id_medida, "kwh_mes": economia_kwh, "reais_mes": economia_reais}


def preco_limite_por_unidade(economia_reais_mes, unidades, meses_retorno=12):
    """Preço máximo por unidade para a troca se pagar no prazo (sem inventar preço).

    preço-limite = (economia por mês x meses) / número de unidades
    """
    return economia_reais_mes * meses_retorno / unidades


def meses_para_pagar(investimento_reais, economia_reais_mes):
    """Payback simples em meses (None se não houver economia)."""
    if economia_reais_mes <= 0:
        return None
    return investimento_reais / economia_reais_mes


# --------------------------------------------------------------------------
# 4) Alternativa B: energia solar por assinatura (geração compartilhada)
# --------------------------------------------------------------------------

def disponibilidade_kwh(params):
    """Consumo mínimo faturado (custo de disponibilidade) pelo tipo de ligação."""
    return params["custo_disponibilidade_kwh"][params["tipo"]]


def custo_com_assinatura(consumo_kwh, params, desconto, bandeira=None):
    """Custo mensal usando créditos de uma usina solar por assinatura.

    Modelo simplificado (ver limitações em docs/sers/02):
      - o mínimo (disponibilidade) continua sendo pago à distribuidora;
      - os kWh acima do mínimo são cobertos por créditos da usina;
      - a empresa da usina cobra esses kWh com 'desconto' sobre o preço do kWh
        com tributos. O desconto é LÍQUIDO (já inclui o que ainda vem na conta).
    """
    tarifa = tarifa_com_tributos(consumo_kwh, params, bandeira)
    minimo = disponibilidade_kwh(params)
    kwh_compensados = max(consumo_kwh - minimo, 0)
    kwh_distribuidora = consumo_kwh - kwh_compensados
    parte_distribuidora = kwh_distribuidora * tarifa + params["cosip_reais"]
    parte_assinatura = kwh_compensados * tarifa * (1 - desconto)
    return {
        "kwh_compensados": kwh_compensados,
        "kwh_distribuidora": kwh_distribuidora,
        "tarifa": tarifa,
        "parte_distribuidora": parte_distribuidora,
        "parte_assinatura": parte_assinatura,
        "total": parte_distribuidora + parte_assinatura,
    }


def desconto_para_igualar(economia_alvo_reais_mes, consumo_kwh, params):
    """Desconto necessário para a assinatura economizar o mesmo que a eficiência."""
    tarifa = tarifa_com_tributos(consumo_kwh, params)
    kwh_compensados = max(consumo_kwh - disponibilidade_kwh(params), 0)
    if kwh_compensados == 0:
        return None
    return economia_alvo_reais_mes / (kwh_compensados * tarifa)


# --------------------------------------------------------------------------
# 5) Impacto ambiental
# --------------------------------------------------------------------------

def emissoes_kg_co2(energia_kwh, params):
    """Emissões associadas a uma energia: kg CO2 = kWh x fator (kg CO2/kWh)."""
    return energia_kwh * params["fator_emissao_kg_co2_kwh"]


# --------------------------------------------------------------------------
# 6) Comparação das alternativas (mesma necessidade, mesmo período)
# --------------------------------------------------------------------------

def comparar_alternativas(params, equipamentos, medidas, desconto=None):
    """Compara Base, A (eficiência), B (solar por assinatura) e A+B.

    Todos atendem à MESMA necessidade (os serviços do cenário-base) no MESMO
    período (12 meses). Devolve uma lista de dicionários, um por cenário.
    """
    if desconto is None:
        desconto = params["desconto_base"]
    meses = params["horizonte_meses"]

    c0 = consumo_total(equipamentos)
    eqs_a = aplicar_medidas(equipamentos, medidas)
    c1 = consumo_total(eqs_a)
    minimo = disponibilidade_kwh(params)

    custo_base = custo_mensal(c0, params)
    custo_a = custo_mensal(c1, params)
    custo_b = custo_com_assinatura(c0, params, desconto)["total"]
    custo_ab = custo_com_assinatura(c1, params, desconto)["total"]

    def linha(nome, descricao, consumo, custo, co2_kg_ano):
        return {
            "nome": nome,
            "descricao": descricao,
            "consumo_kwh_mes": consumo,
            "custo_mes": custo,
            "custo_12_meses": custo * meses,
            "economia_mes": custo_base - custo,
            "economia_12_meses": (custo_base - custo) * meses,
            "co2_evitado_kg_ano": co2_kg_ano,
        }

    fe = params["fator_emissao_kg_co2_kwh"]
    return [
        linha("Base", "Situação atual, sem mudanças", c0, custo_base, 0.0),
        linha("A", "Eficiência (banho de 10 min + lâmpadas LED)", c1, custo_a,
              (c0 - c1) * fe * meses),
        linha("B", f"Solar por assinatura ({desconto*100:.0f}% de desconto líquido)", c0, custo_b,
              max(c0 - minimo, 0) * fe * meses),
        linha("A+B", "Eficiência + solar por assinatura", c1, custo_ab,
              (c0 - minimo) * fe * meses if c0 > minimo else 0.0),
    ]


def sensibilidade_assinatura(params, consumo_kwh):
    """Economia mensal e anual da assinatura para cada desconto do cenário."""
    base = custo_mensal(consumo_kwh, params)
    meses = params["horizonte_meses"]
    resultado = []
    for d in params["desconto_cenarios"]:
        total = custo_com_assinatura(consumo_kwh, params, d)["total"]
        resultado.append({
            "desconto": d,
            "custo_mes": total,
            "economia_mes": base - total,
            "economia_12_meses": (base - total) * meses,
        })
    return resultado


def recomendar(params, equipamentos, medidas):
    """Gera a recomendação (texto) a partir dos números, com regras explícitas.

    Regra 1: se a eficiência economiza mais que a assinatura no caso-base,
             a primeira recomendação é eficiência (sem contrato nem risco).
    Regra 2: a assinatura entra como complemento, se o contrato tiver desconto
             líquido comprovado e sem prazo de fidelidade longo.
    Regra 3: nunca prometer economia garantida (os valores são estimativas).
    """
    cenarios = {c["nome"]: c for c in comparar_alternativas(params, equipamentos, medidas)}
    econ_a = cenarios["A"]["economia_mes"]
    econ_b = cenarios["B"]["economia_mes"]
    c0 = cenarios["Base"]["consumo_kwh_mes"]
    d_igual = desconto_para_igualar(econ_a, c0, params)
    if econ_a >= econ_b:
        principal = ("Comece pela eficiência (Alternativa A): no caso-base ela economiza "
                     "mais que a assinatura solar e não exige contrato.")
    else:
        principal = ("No caso-base a assinatura solar (Alternativa B) economiza mais que a "
                     "eficiência, mas confirme o desconto líquido no contrato antes de decidir.")
    complemento = ("A assinatura solar pode ser somada depois (A+B), desde que o desconto "
                   "líquido seja comprovado e o contrato não tenha fidelidade longa.")
    if d_igual is not None:
        complemento += (f" Para a assinatura sozinha igualar a eficiência, o desconto líquido "
                        "precisaria ser de cerca de " + f"{d_igual*100:.1f}".replace(".", ",") + "%.")
    return [principal, complemento,
            "Todos os valores são estimativas e podem mudar com a tarifa, o consumo real e o contrato."]
