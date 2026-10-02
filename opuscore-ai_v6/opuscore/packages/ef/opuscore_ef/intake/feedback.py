"""Relatório de feedback para o FUNCIONAL — o que falta e o que dá pra melhorar na EF.

Gerado em Python a partir do que a Etapa 1 já descobriu (sem chamada extra à IA).
Tom descontraído de propósito: é um colega dando um toque, não um parecer jurídico.
"""
from __future__ import annotations

import re
from collections import OrderedDict

from .checks import Achado
from .deterministic import is_template, role_of
from .gate import INVALIDO, VALIDO, Gate
from .parser import EFDocument
from .schema import ExtractionResult, Item

# seções que a gente espera numa EF (papel -> nome amigável, por que importa)
ESPERADAS = OrderedDict([
    ("objetivo", ("Objetivo e justificativa", "é daqui que o dev entende o PORQUÊ do desenvolvimento")),
    ("processos", ("Processos relacionados", "mostra em quais transações/apps o negócio roda")),
    ("regras", ("Regras de negócio", "é o coração da EF: sem regra clara, o dev chuta")),
    ("premissas", ("Premissas e escopo", "diz o que entra e o que fica de fora")),
    ("fluxo", ("Fluxo do processo", "mostra a ordem das coisas e quem faz o quê")),
    ("sistemas", ("Sistemas impactados", "evita surpresa com integração no meio do caminho")),
    ("teste_proc", ("Procedimento de testes", "sem roteiro de teste ninguém sabe quando terminou")),
    ("teste_result", ("Resultados esperados", "é o critério de aceite: o que é 'funcionou'")),
    ("nfr", ("Informações complementares", "volumetria, janela, erros e criticidade")),
    ("homologacao", ("Homologação", "diz quem bate o martelo no final")),
])

# palavras que deixam a EF aberta a interpretação
_VAGOS = [
    (r"\bsimplificad[ao]s?\b", "simplificada", "simplificada em relação a quê? Diga o que sai e o que fica."),
    (r"\badequad[ao]s?\b|\bde forma adequada\b", "adequado(a)", "adequado segundo qual critério? Troque por uma regra verificável."),
    (r"\baplic[aá]ve(l|is)\b", "aplicável(is)", "quais, exatamente? Liste os itens em vez de deixar o dev adivinhar."),
    (r"\bquando necess[aá]rio\b|\bse necess[aá]rio\b|\bconforme necessidade\b", "quando necessário",
     "necessário quando? Descreva a condição que dispara."),
    (r"\balgumas? funcionalidades\b", "algumas funcionalidades", "quais? Uma lista resolve."),
    (r"\bentre outros\b|\betc\.?(?=\s|$)", "etc. / entre outros", "o 'etc.' vira escopo infinito. Feche a lista."),
    (r"\bos demais\b|\bas demais\b", "os demais", "'os demais' quais? Vale nomear, nem que seja numa lista curta."),
    (r"\bdevidamente\b", "devidamente", "devidamente como? Diga qual é a condição."),
]

_EMOJI = {VALIDO: "🟢", INVALIDO: "🔴"}


def _cel(s, n=160) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return (s[:n] + "…") if len(s) > n else s


def _onde(doc: EFDocument, loc: str) -> str:
    """Seção + começo do trecho, pra achar com Ctrl+F no Word."""
    for s in doc.sections:
        if s.sid == loc:
            return f"seção “{s.path_str.split(' > ')[-1]}”"
        for b in s.blocks:
            if b.loc == loc:
                ini = re.sub(r"\s+", " ", b.text.replace("|", " ")).strip()[:60]
                return f"seção “{s.path_str.split(' > ')[-1]}”, no trecho que começa com “{ini}…”"
    return loc


def _ondes(doc: EFDocument, locs: list[str], limite: int = 3) -> str:
    partes = [_onde(doc, l) for l in locs[:limite]]
    resto = len(locs) - limite
    return "; ".join(partes) + (f" (e mais {resto} lugar{'es' if resto > 1 else ''})" if resto > 0 else "")


def _pl(n: int, sing: str, plur: str) -> str:
    return f"{n} {sing if n == 1 else plur}"


def _secoes_por_papel(doc: EFDocument) -> dict[str, list]:
    out: dict[str, list] = {}
    for s in doc.sections:
        out.setdefault(role_of(s), []).append(s)
    return out


def gerar(doc: EFDocument, res: ExtractionResult, gate: Gate, achados: list[Achado], meta: dict) -> str:
    ef_id = res.controle.id_demanda
    faltas: list[dict] = []       # {titulo, onde, porque, como}
    melhorias: list[dict] = []
    positivos: list[str] = []
    itens = res.itens
    por = lambda cat: [i for i in itens if i.categoria == cat]  # noqa: E731

    # ---------------- o que está FALTANDO ----------------
    papeis = _secoes_por_papel(doc)
    for papel, (nome, porque) in ESPERADAS.items():
        secs = papeis.get(papel, [])
        if not secs:
            faltas.append({"titulo": f"Não achei a seção **{nome}**",
                           "onde": "em lugar nenhum da EF",
                           "porque": porque,
                           "como": f"Inclua a seção {nome}. Se não se aplica, escreva 'Não se aplica' e o motivo."})
            continue
        uteis = [b for s in secs for b in s.blocks if not is_template(b)]
        if not uteis:
            faltas.append({"titulo": f"A seção **{nome}** está vazia (ou só com o texto do template)",
                           "onde": ", ".join(s.path_str.split(" > ")[-1] for s in secs),
                           "porque": porque,
                           "como": "Preencha com o conteúdo do seu cenário. Se não se aplica, deixe isso escrito com o motivo."})

    # parâmetros: só o texto de orientação do template
    param = papeis.get("parametros", [])
    if param and not [b for s in param for b in s.blocks if not is_template(b)]:
        tabelas = sorted({i.valor_original for i in por("REF_TECNICA")
                          if i.tipo_objeto == "TABELA" and i.escopo != "EXCLUIDO"})
        dica = f" Pelo que a EF descreve, a {', '.join(tabelas)} parece ser uma tabela de parâmetros." if tabelas else ""
        faltas.append({"titulo": "A seção de **TVARV, BRF+ e tabelas de parâmetros** só tem o texto de orientação do template",
                       "onde": param[0].path_str.split(" > ")[-1],
                       "porque": "o dev precisa saber o que é parametrizável e quem mantém, senão vira hardcode",
                       "como": "Liste cada parâmetro: nome, tipo (TVARV, BRF+, tabela, app), valores e quem dá manutenção."
                               + dica})

    # homologação sem nomes
    for s in papeis.get("homologacao", []):
        vazios = [b for b in s.blocks if not b.loc.endswith(".r0") and re.search(r"\)\s*/?\s*$", b.text)]
        if vazios:
            faltas.append({"titulo": f"Faltam os nomes de quem homologa ({_pl(len(vazios), 'papel', 'papéis')} sem ninguém)",
                           "onde": "seção “Homologação”, na tabela de responsáveis",
                           "porque": "sem responsável definido, a aprovação trava no final",
                           "como": "Coloque o nome de cada responsável: " +
                                   "; ".join(_cel(b.text.strip(' /'), 60) for b in vazios[:4]) + "."})

    # versão divergente
    for a in achados:
        if a.codigo == "VERSAO_DIVERGENTE":
            faltas.append({"titulo": "A versão do arquivo não bate com o histórico de revisão",
                           "onde": "tabela de histórico de revisão, no começo do documento",
                           "porque": "quem ler não sabe se está com a versão certa",
                           "como": _cel(a.mensagem, 200) + " Adicione a linha da nova versão no histórico."})

    # esboços de tela que ficaram sem leitura (ex.: execução sem IA)
    imgs = meta.get("imagens") or []
    esb_nao_lidos = [i for i in imgs if i["tipo"] == "ESBOCO" and not i["lida"]]
    if esb_nao_lidos:
        motivo = ("a leitura de imagens estava desligada nesta execução"
                  if meta.get("modo_imagens") == "nenhuma" else
                  "; ".join(sorted({i['erro'] for i in esb_nao_lidos if i['erro']})) or "não foi possível ler")
        faltas.append({"titulo": f"{_pl(len(esb_nao_lidos), 'esboço de tela ficou', 'esboços de tela ficaram')} sem leitura",
                       "onde": _ondes(doc, [i["loc"] for i in esb_nao_lidos]),
                       "porque": f"o que está só na imagem pode se perder ({motivo})",
                       "como": "Rode de novo com a IA ligada pra gente ler os esboços. Se preferir, descreva os "
                               "campos em texto embaixo da imagem (campo | tipo | obrigatório)."})

    # anexos citados
    for i in por("ANEXO"):
        if i.classificacao == "PONTO_A_CONFIRMAR":
            faltas.append({"titulo": "A EF cita um anexo que não veio junto",
                           "onde": _onde(doc, i.fonte.localizacao[0]),
                           "porque": "se a regra ou o layout está no anexo, o dev fica sem",
                           "como": "Anexe o arquivo ou traga o conteúdo pra dentro da EF."})

    # ausências apontadas pela IA
    for i in por("AUSENCIA"):
        if i.id.startswith("G"):     # campo que está na tela e não está no texto
            faltas.append({"titulo": _cel(i.descricao, 180), "onde": _onde(doc, (i.fonte.localizacao or ["—"])[0]),
                           "porque": "o campo aparece só no esboço; se ninguém escrever, o dev pode deixar passar",
                           "como": "Confirme se o campo existe mesmo. Se existir, inclua na lista de campos do texto "
                                   "(com o nome técnico, se já tiver). Se foi engano no esboço, é só avisar."})
            continue
        faltas.append({"titulo": _cel(i.descricao, 140), "onde": _onde(doc, (i.fonte.localizacao or ["—"])[0]),
                       "porque": "a IA não achou essa informação na EF",
                       "como": "Complete esse ponto na seção indicada."})

    # ---------------- o que dá pra MELHORAR ----------------
    for i in por("AMBIGUIDADE") + por("CONTRADICAO"):
        tipo = "Ficou ambíguo" if i.categoria == "AMBIGUIDADE" else "Parece que se contradiz"
        melhorias.append({"titulo": f"{tipo}: {_cel(i.descricao, 140)}",
                          "onde": _onde(doc, (i.fonte.localizacao or ["—"])[0]),
                          "porque": "cada pessoa pode entender de um jeito",
                          "como": f"Reescreva deixando uma interpretação só. Trecho: “{_cel(i.fonte.trecho, 120)}”"})

    # termos vagos (varredura determinística nas seções narrativas)
    narrativas = {"objetivo", "regras", "premissas", "fluxo", "novos_objetos", "enh_requisitos", "enh_regra"}
    for pat, termo, dica in _VAGOS:
        ocorr = [(s, b) for s in doc.sections if role_of(s) in narrativas
                 for b in s.blocks if not is_template(b) and re.search(pat, b.text, re.I)]
        if ocorr:
            locs = _ondes(doc, [b.loc for _, b in ocorr], limite=2)
            exemplo = next(b.text for _, b in ocorr)
            m = re.search(pat, exemplo, re.I)
            ini = max(0, m.start() - 60)
            melhorias.append({"titulo": f"A palavra **“{termo}”** aparece {_pl(len(ocorr), 'vez', 'vezes')}",
                              "onde": locs,
                              "porque": "é palavra que abre margem pra interpretação",
                              "como": f"{dica} Exemplo na EF: “…{_cel(exemplo[ini:m.end() + 60], 140)}…”"})

    # referências sem escopo definido
    brutos = sorted({i.valor_original for i in por("REF_TECNICA") if i.escopo == "INDEFINIDO"})
    tabelas_campos: dict[str, list[str]] = {}
    for r in brutos:
        if "-" in r:
            t, c = r.split("-", 1)
            tabelas_campos.setdefault(t, []).append(c)
    indef = [r for r in brutos if "-" not in r]
    indef += [t for t in tabelas_campos if t not in indef]
    rotulos = [f"{r} (campos {', '.join(tabelas_campos[r])})" if r in tabelas_campos else r for r in sorted(indef)]
    if indef:
        melhorias.append({"titulo": f"{_pl(len(indef), 'objeto técnico citado', 'objetos técnicos citados')} "
                                    "sem dizer se entra ou não no escopo",
                          "onde": "; ".join(rotulos[:8]) + (" …" if len(rotulos) > 8 else ""),
                          "porque": "o dev não sabe se precisa mexer neles ou só consultar",
                          "como": "Pra cada um, diga: remediar, só consultar, ou fora do escopo."})

    # componentes com natureza incerta
    incertos = [i for i in por("COMPONENTE") if i.confianca != "ALTA"]
    if incertos:
        melhorias.append({"titulo": f"{_pl(len(incertos), 'componente', 'componentes')} sem deixar claro se é novo, remediação ou evolução",
                          "onde": "; ".join(_cel(i.descricao.split(' — ')[0], 50) for i in incertos[:5]),
                          "porque": "isso muda o nível de Clean Core exigido e o jeito de desenvolver",
                          "como": "Marque a natureza de cada objeto (Novo / Remediação / Evolução)."})

    # enhancement implícito declarado (Clean Core)
    implic = [i for i in por("ESCOPO_INCLUIDO") if "ponto de ampliação implícito" in i.descricao.lower()]
    if implic:
        melhorias.append({"titulo": "A EF prevê uso de ponto de ampliação implícito",
                          "onde": _onde(doc, implic[0].fonte.localizacao[0]),
                          "porque": "enhancement implícito é o nível mais baixo de Clean Core (nível D)",
                          "como": "Não é você quem decide a técnica, relaxa: só registre se já foi avaliada alternativa "
                                  "(BAdI liberada, por exemplo). O Líder Técnico vai bater o martelo."})

    # ---------------- o que já está BOM ----------------
    if por("ESCOPO_EXCLUIDO"):
        positivos.append(f"Você deixou claro o que **fica de fora** ({_pl(len(por('ESCOPO_EXCLUIDO')), 'ponto', 'pontos')}). Isso economiza muito retrabalho.")
    refs = [i for i in por("REF_TECNICA") if i.escopo != "EXCLUIDO"]
    if refs:
        positivos.append(f"Os objetos técnicos estão **nomeados** ({_pl(len(refs), 'referência', 'referências')}). O dev já sabe por onde começar.")
    if por("TESTE"):
        positivos.append(f"Tem **roteiro de teste** ({_pl(len(por('TESTE')), 'passo', 'passos')}) e {_pl(len(por('ACEITE')), 'resultado esperado', 'resultados esperados')}.")
    if por("REGRA"):
        positivos.append(f"**{_pl(len(por('REGRA')), 'regra de negócio', 'regras de negócio')}** bem identificadas.")
    if por("CAMPO"):
        positivos.append(f"Os campos da tabela de parâmetros estão **mapeados** ({_pl(len(por('CAMPO')), 'campo', 'campos')}).")
    if por("DEPENDENCIA"):
        positivos.append("As **dependências com outros GAPs** estão citadas: "
                         + ", ".join(sorted({i.valor_original for i in por('DEPENDENCIA')})) + ".")

    # ---------------- montagem ----------------
    emoji = _EMOJI.get(gate.status, "🟡")
    veredito = {
        VALIDO: "Tá redondinha! Dá pra seguir pra descoberta técnica sem susto.",
        INVALIDO: "Ainda não dá pra seguir: tem coisa bloqueando. Mas relaxa, a lista abaixo mostra exatamente o quê.",
    }.get(gate.status, "Dá pra seguir, mas tem uns pontos que valem ajuste pra ninguém travar lá na frente.")

    out = [f"# 📝 Feedback da EF {ef_id} — o que falta e o que dá pra melhorar", "",
           f"E aí! Passei a EF **{doc.filename}** (versão {meta.get('versao') or '—'}) pelo raio-x. "
           "Aqui vai o resumo sem enrolação, com onde está cada ponto e como resolver.", "",
           f"## {emoji} Resumo rápido", "", veredito, "",
           f"- **{_pl(len(faltas), 'coisa', 'coisas')}** faltando",
           f"- **{_pl(len(melhorias), 'sugestão', 'sugestões')}** de melhoria",
           f"- **{_pl(len(gate.a_confirmar), 'ponto', 'pontos')}** que a IA achou sensível e precisa da sua confirmação", ""]

    if gate.bloqueantes:
        out += ["## 🚧 O que está travando", "",
                "Esses pontos impedem a EF de seguir. São os primeiros a resolver:", ""]
        for b in gate.bloqueantes:
            out += [f"- **{b['codigo']} — {b['descricao']}**: {_cel(b['evidencia'], 260)}"]
        out += [""]

    if gate.a_confirmar:
        out += ["## 🤔 A IA ficou com uma pulga atrás da orelha", "",
                "A IA leu a EF e achou que esses pontos podem travar. **Não é bloqueio automático**: "
                "você (ou o Líder Técnico) olha e decide se procede.", ""]
        for a in gate.a_confirmar:
            onde = _ondes(doc, a.get("localizacao") or []) or "—"
            out += [f"### {a['codigo']} — {a['descricao']}", "",
                    f"**O que a IA achou:** {_cel(a['evidencia'], 400)}", "",
                    f"**Onde olhar:** {onde}", "",
                    "**O que fazer:** se proceder, ajuste a EF deixando uma leitura só; se não proceder, "
                    "marque como descartado e siga. Dica: às vezes uma frase explicando o porquê já resolve.", ""]

    def bloco(titulo, lista, vazio):
        linhas = [f"## {titulo}", ""]
        if not lista:
            return linhas + [vazio, ""]
        for n, x in enumerate(lista, start=1):
            linhas += [f"### {n}. {x['titulo']}", "",
                       f"- **Onde:** {x['onde']}",
                       f"- **Por que importa:** {x['porque']}",
                       f"- **Como resolver:** {x['como']}", ""]
        return linhas

    out += bloco("❌ O que está faltando", faltas, "Nada faltando. Mandou bem! 👏")
    out += bloco("✏️ O que dá pra melhorar", melhorias, "Nenhuma sugestão. Tá bem escrita!")

    lidas = [i for i in (meta.get("imagens") or []) if i["lida"] and i["tela"]]
    if lidas:
        out += ["## 📸 A gente leu os esboços pra você", "",
                "Em vez de pedir pra você descrever cada tela, a IA leu as imagens. **Só confere se está certo**: "
                "se algum campo estiver errado ou faltando, ajusta na EF.", ""]
        for i in lidas:
            t = i["tela"]
            out += [f"### {i['nome']} — {_cel(i['legenda'], 90)}", ""]
            if t.get("observacoes"):
                out += [f"_{_cel(t['observacoes'], 400)}_", ""]
            if t.get("abas"):
                out += [f"**Abas:** {', '.join(t['abas'])}" + (f" (aberta: {t['aba_ativa']})" if t.get("aba_ativa") else ""), ""]
            if t.get("campos"):
                com_aba = any((c.get("aba") or "").strip() for c in t["campos"])
                out += (["| Campo | Tipo | Exemplo na tela | Aba |", "|---|---|---|---|"] if com_aba else
                        ["| Campo | Tipo | Exemplo na tela |", "|---|---|---|"])
                for c in t["campos"]:
                    linha = f"| {_cel(c.get('rotulo'), 60)} | {c.get('tipo', '')} | {_cel(c.get('valor_exemplo'), 30)} |"
                    out.append(linha + (f" {_cel(c.get('aba'), 40)} |" if com_aba else ""))
                out += [""]
            if t.get("botoes"):
                out += [f"**Botões:** {', '.join(t['botoes'])}", ""]
            if i.get("mascarados"):
                out += [f"🔒 Valores de identificação de pessoas foram escondidos ({', '.join(i['mascarados'])}).", ""]

    if positivos:
        out += ["## ✅ O que já está bom", "", "Nem tudo é crítica, tá? Isso aqui ficou bem feito:", ""]
        out += [f"- {p}" for p in positivos] + [""]

    out += ["## 📋 Checklist pra próxima versão", ""]
    for x in faltas:
        out.append(f"- [ ] {re.sub(r'[*]', '', x['titulo'])}")
    for x in melhorias:
        out.append(f"- [ ] {re.sub(r'[*]', '', x['titulo'])}")
    for a in gate.a_confirmar:
        out.append(f"- [ ] Confirmar ou descartar o ponto da IA: {a['codigo']} ({a['descricao']})")
    if lidas:
        out.append(f"- [ ] Conferir a leitura dos {_pl(len(lidas), 'esboço de tela', 'esboços de tela')}")
    out += ["- [ ] Atualizar o histórico de revisão com a nova versão", "",
            "---", "",
            "_Esse feedback foi gerado automaticamente a partir da própria EF. Os trechos citados são o começo "
            "de cada parágrafo: é só copiar e buscar com Ctrl+F no Word. Ficou alguma dúvida? Chama o time técnico._", ""]
    return "\n".join(out)


def nome_arquivo(id_demanda: str, versao: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", (id_demanda or "EF").strip()).strip("-") or "EF"
    v = re.sub(r"[^A-Za-z0-9._-]+", "", (versao or "0").lstrip("vV")) or "0"
    return f"{base}-Feedback-Funcional-EF-v{v}.md"
