"""Gera docs/sers/02_calculos_e_comparacao.md a partir dos MESMOS cálculos do assistente.

Rodar, a partir da pasta citizen-assist-ai:
    python -m sers.gerar_relatorio

Assim o documento e o assistente nunca ficam com números diferentes: se a tarifa
mudar em data/sers/parametros.json, é só rodar de novo.
"""
import os

from sers import calculos as c
from sers import dados
from sers.respostas import br, moeda, moeda_kwh


def gerar():
    p = dados.parametros()
    eqs = dados.equipamentos_cenario_base()
    medidas = dados.medidas_eficiencia()
    c0 = c.consumo_total(eqs)
    t0 = c.tarifa_com_tributos(c0, p)
    cenarios = c.comparar_alternativas(p, eqs, medidas)
    cen = {x["nome"]: x for x in cenarios}
    minimo = c.disponibilidade_kwh(p)
    icms0 = c.aliquota_icms(c0, p)

    L = []
    L.append("# Cálculos e comparação das alternativas (SERS)\n")
    L.append("> Este arquivo é GERADO por `python -m sers.gerar_relatorio` a partir de `data/sers/` e `sers/calculos.py`. Não edite à mão: mude os dados e gere de novo.\n")
    L.append(f"Data de referência dos dados: {p['data_consulta']}. Distribuidora: {p['distribuidora']}.\n")

    L.append("## 1. Necessidade e período de referência\n")
    L.append("**Necessidade:** atender os serviços de energia de um apartamento alugado de 1 morador (cenário-base abaixo), com o mesmo conforto, durante **12 meses**. As duas alternativas e a combinação são comparadas para essa mesma necessidade e esse mesmo período.\n")

    L.append("## 2. Fórmulas\n")
    L.append("| O que calcula | Fórmula | Unidades |")
    L.append("|---|---|---|")
    L.append("| Energia de um equipamento | E = P × t × dias × quantidade | P em kW (watts ÷ 1000), t em h/dia, E em kWh/mês |")
    L.append("| Preço do kWh sem impostos | T = (TUSD + TE) ÷ 1000 + adicional da bandeira ÷ 100 | TUSD e TE em R$/MWh; bandeira em R$/100 kWh |")
    L.append("| Preço do kWh com impostos | Tc = T ÷ (1 − ICMS − PIS/COFINS) | ICMS depende da faixa de consumo; os impostos são \"por dentro\" |")
    L.append("| Conta mensal | Custo = E_total × Tc | R$/mês |")
    L.append("| Assinatura solar | Custo = mínimo × Tc + (E_total − mínimo) × Tc × (1 − d) | mínimo = custo de disponibilidade (kWh); d = desconto líquido |")
    L.append("| Emissões | CO2 = E × FE | FE em kg CO2/kWh |\n")

    L.append("## 3. Dados e premissas\n")
    L.append("| Parâmetro | Valor | Status | Fonte |")
    L.append("|---|---|---|---|")
    for nome, valor, unidade, status, fonte in dados.fontes_dos_parametros():
        valor_txt = valor if not isinstance(valor, (list, dict)) else "ver `parametros.json`"
        L.append(f"| {nome} | {valor_txt} ({unidade}) | {status} | {fonte} |")
    L.append("\nSignificado do status: **oficial** = publicado por órgão oficial; **secundária** = reportado por notícia ou artigo a partir de dado oficial; **estimativa** = valor estimado com justificativa; **assumido** = premissa do grupo.\n")

    L.append("## 4. Cenário-base (consumo)\n")
    L.append("| Equipamento | Qtd | Potência (W) | Uso | kWh/mês | % | Status |")
    L.append("|---|---|---|---|---|---|---|")
    for eq in sorted(eqs, key=c.consumo_equipamento, reverse=True):
        kwh = c.consumo_equipamento(eq)
        if eq["kwh_mes_direto"] is not None:
            uso = "consumo mensal da tabela"
        else:
            uso = f"{br(eq['minutos_dia'], 0)} min/dia, {br(eq['dias_mes'], 0)} dias"
        L.append(f"| {eq['equipamento']} | {eq['quantidade']} | {br(eq['potencia_w'], 0)} | {uso} | {br(kwh, 2)} | {br(kwh / c0 * 100, 0)}% | {eq['status']} |")
    L.append(f"| **Total** | | | | **{br(c0, 2)}** | 100% | |\n")
    L.append(f"Faixa de ICMS aplicada: {br(icms0 * 100, 0)}% (consumo entre 91 e 200 kWh).")
    L.append(f"Preço do kWh: ({br(p['tusd_r_mwh'], 2)} + {br(p['te_r_mwh'], 2)}) ÷ 1000 = R$ {br(c.tarifa_sem_tributos(p), 5)} sem impostos; com impostos: {br(c.tarifa_sem_tributos(p), 5)} ÷ (1 − {br(icms0, 2)} − {br(p['pis_cofins'], 3)}) = **{moeda_kwh(t0)}**.")
    L.append(f"Conta do cenário-base: {br(c0, 2)} × {br(t0, 4)} = **{moeda(cen['Base']['custo_mes'])} por mês** ({moeda(cen['Base']['custo_12_meses'])} em 12 meses).\n")

    L.append("## 5. Alternativa A: eficiência energética\n")
    for m in medidas:
        r = c.economia_de_uma_medida(eqs, medidas, m["id"], p)
        L.append(f"- **{m['titulo']}**: economiza {br(r['kwh_mes'], 2)} kWh e {moeda(r['reais_mes'])} por mês. Fonte: {m['fonte']} {m['observacao']}")
    lamp = [e for e in eqs if e["id"] == "lampadas"][0]
    r_led = c.economia_de_uma_medida(eqs, medidas, "led_8w", p)
    limite = c.preco_limite_por_unidade(r_led["reais_mes"], lamp["quantidade"], p["horizonte_meses"])
    L.append(f"\nPreço-limite da lâmpada LED para pagar a troca em 12 meses: {moeda(r_led['reais_mes'])} × 12 ÷ {lamp['quantidade']} = **{moeda(limite)} por lâmpada**. (O grupo não inventou preço de produto: ao pesquisar na loja, compare com esse limite.)\n")
    L.append(f"Resultado da alternativa A: consumo de {br(cen['A']['consumo_kwh_mes'], 2)} kWh/mês, conta de {moeda(cen['A']['custo_mes'])}, economia de **{moeda(cen['A']['economia_mes'])}/mês** ({moeda(cen['A']['economia_12_meses'])} em 12 meses).\n")

    L.append("## 6. Alternativa B: energia solar por assinatura (fonte renovável)\n")
    L.append(f"Tipo de ligação assumido: {p['tipo']} (custo de disponibilidade = {minimo} kWh/mês). Energia coberta por créditos: {br(c0, 2)} − {minimo} = {br(c0 - minimo, 2)} kWh.\n")
    L.append("| Desconto líquido | Conta mensal | Economia/mês | Economia em 12 meses |")
    L.append("|---|---|---|---|")
    for s in c.sensibilidade_assinatura(p, c0):
        L.append(f"| {br(s['desconto'] * 100, 0)}% | {moeda(s['custo_mes'])} | {moeda(s['economia_mes'])} | {moeda(s['economia_12_meses'])} |")
    L.append(f"\nCaso-base escolhido: {br(p['desconto_base'] * 100, 0)}% (extremo inferior da faixa de 10% a 20% citada em reportagem). Resultado: conta de {moeda(cen['B']['custo_mes'])}, economia de **{moeda(cen['B']['economia_mes'])}/mês**.\n")

    L.append("## 7. Comparação final (mesma necessidade, 12 meses)\n")
    L.append("| Cenário | kWh/mês | Conta/mês | Conta em 12 meses | Economia/mês | Economia em 12 meses | CO2 (kg/ano) |")
    L.append("|---|---|---|---|---|---|---|")
    for x in cenarios:
        L.append(f"| {x['nome']}: {x['descricao']} | {br(x['consumo_kwh_mes'], 1)} | {moeda(x['custo_mes'])} | {moeda(x['custo_12_meses'])} | {moeda(x['economia_mes'])} | {moeda(x['economia_12_meses'])} | {br(x['co2_evitado_kg_ano'], 1)} |")
    d_igual = c.desconto_para_igualar(cen["A"]["economia_mes"], c0, p)
    L.append(f"\nDesconto líquido que a assinatura precisaria ter para igualar a eficiência: {moeda(cen['A']['economia_mes'])} ÷ ({br(c0 - minimo, 1)} kWh × {br(t0, 4)}) = **{br(d_igual * 100, 1)}%**.\n")
    L.append("**Recomendação gerada pelo código (`calculos.recomendar`):**\n")
    for linha in c.recomendar(p, eqs, medidas):
        L.append(f"- {linha}")

    L.append("\n## 8. Bandeira tarifária (sensibilidade)\n")
    L.append("| Bandeira | Conta/mês do cenário-base | Diferença para a verde |")
    L.append("|---|---|---|")
    verde = c.custo_mensal(c0, p, "verde")
    for nome in ["verde", "amarela", "vermelha1", "vermelha2"]:
        v = c.custo_mensal(c0, p, nome)
        L.append(f"| {nome} | {moeda(v)} | {moeda(v - verde)} |")

    L.append("\n## 9. Impacto ambiental\n")
    L.append(f"FE = {br(p['fator_emissao_kg_co2_kwh'], 4)} kg CO2/kWh. A: ({br(c0, 2)} − {br(cen['A']['consumo_kwh_mes'], 2)}) × FE × 12 = {br(cen['A']['co2_evitado_kg_ano'], 1)} kg/ano. B: {br(c0 - minimo, 2)} × FE × 12 = {br(cen['B']['co2_evitado_kg_ano'], 1)} kg/ano (contabilização por créditos). Em A+B os kWh evitados e os kWh de créditos somam o mesmo total de B, por isso o valor é igual ao de B.")
    L.append("Os números são pequenos porque a eletricidade brasileira já é majoritariamente renovável: o ganho principal das duas alternativas é financeiro. Impactos de fabricação dos painéis e uso de área da usina não foram calculados.\n")

    L.append("## 10. Limitações\n")
    for lim in [
        "O cenário-base é uma estimativa para 1 morador. Os dados de potência vêm de uma cartilha da CEMIG de 2014; os tempos de uso são premissas do grupo.",
        "O preço do kWh usa a tarifa B1 convencional da Enel SP (REH 3.596/2026). ICMS e PIS/COFINS são aproximados e variam; confira na sua conta.",
        "O modelo da assinatura é simplificado: o desconto é tratado como líquido e não reproduz as regras detalhadas de ICMS sobre a energia compensada nem a cobrança gradual do Fio B da Lei 14.300/2022.",
        "O desconto da assinatura vem de uma reportagem (10% a 20%) e de uma oferta divulgada; o valor de 5% é cenário pessimista do grupo. As regras da geração compartilhada estão em discussão na ANEEL em 2026.",
        "A economia da eficiência depende de mudança de hábito (banho) e do preço das lâmpadas, que não foi inventado.",
        "O cenário não considera inflação, reajustes futuros de tarifa nem a fidelidade e multas de contratos.",
        "Nenhum resultado aqui é promessa de economia.",
    ]:
        L.append(f"- {lim}")

    caminho = os.path.join(dados.PASTA_PROJETO, "docs", "sers", "02_calculos_e_comparacao.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"Arquivo gerado: {caminho}")


if __name__ == "__main__":
    gerar()
