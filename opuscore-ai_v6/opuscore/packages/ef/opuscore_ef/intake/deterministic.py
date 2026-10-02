"""Extração determinística da EF — sem IA.

Tudo o que é estrutural sai daqui: cabeçalho, checkboxes do Resumo, tabelas de
desenvolvimento, regras em tabela, fluxo, testes, requisitos não funcionais,
referências técnicas, campos, dependências e zonas de escopo excluído.
Cada item nasce com fonte literal (o próprio bloco), então é FATO_DA_EF por
construção. A IA fica só com o que exige interpretação (ver semantic.py).
"""
from __future__ import annotations

import re
import unicodedata

from .checks import _REF_PATTERNS, _TAB_CAMPO, _tipo_por_nome
from .parser import Block, EFDocument, Section
from .schema import Criterio, Fonte, Item, Verificacao


def _plain(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip().lower()


# papel de cada seção, pelo título (sem acento, minúsculo); a numeração é ignorada
_ROLES = [
    (r"resumo do desenvolvimento", "resumo"),
    (r"objetivo", "objetivo"),
    (r"processos relacionados", "processos"),
    (r"regras? de neg[oó]cio", "regras"),
    (r"premissas", "premissas"),
    (r"fluxo", "fluxo"),
    (r"sistemas", "sistemas"),
    (r"novos objetos", "novos_objetos"),
    (r"tvarv|brf|parametr", "parametros"),
    (r"implementacao de ampliac|cmod|badi", "enh_ampliacoes"),
    (r"ponto de ampliacao implicito", "enh_implicito"),
    (r"enhancements?\s*$", "enh_requisitos"),
    (r"procedimento de testes", "teste_proc"),
    (r"resultados esperados", "teste_result"),
    (r"material adicional para os testes", "teste_material"),
    (r"periodicidade|tipo de execucao|volumetria|janela|tratamento de erros|processo critico", "nfr"),
    (r"homologacao", "homologacao"),
    (r"formulario", "formulario"), (r"interfaces? de entrada", "interface_entrada"),
    (r"interfaces? de saida", "interface_saida"), (r"workflow", "workflow"),
    (r"relatorio", "relatorio"), (r"programas? on.?line", "programa"), (r"fiori", "fiori"),
]


def role_of(sec: Section) -> str:
    t = _plain(sec.title)
    if sec.sid == "S00":
        return "capa"
    # "Enhancements – Regra de negócio" é tabela de regras, não a seção 1.3
    if "enhancement" in t and "regra" in t:
        return "enh_regra"
    for pat, role in _ROLES:
        if re.search(pat, t):
            return role
    return "outro"


# texto de orientação do próprio template (não é dado do projeto)
_TEMPLATE = [
    "se o desenvolvimento requer regras de conversoes", "criterios e conceitos importantes",
    "artefato | quem da manutencao", "tvarv | somente ti", "brf+ | somente ti", "sm30 | somente ti",
    "app / fiori | ti e usuarios", "funcionalidades. premissa da brf",
    "<descrever", "descrever as regras", "ex.:", "_____",
]


def is_template(b: Block) -> bool:
    p = _plain(b.text)
    return any(p.startswith(t) or t in p[:60] for t in _TEMPLATE) or bool(re.fullmatch(r"[_\s./-]*", b.text))


_EXCL = re.compile(r"(?i)n[aã]o (ser[aã]o|ser[aá]|fazem parte|far[aã]o parte|ser[aã]o remediad)|"
                   r"n[aã]o ser[aá] utilizad|fora do escopo|desconsiderad")
_INCL = re.compile(r"(?i)dever[aã]o ser remediad|objetos que dever[aã]o|dever[aá] ser mantid|dever[aã]o ser mantid")
_ACAO = re.compile(r"(?i)\bdever[aá]o?\b.{0,40}\b(impedir|validar|permitir|suportar|utilizar|apresentar|"
                   r"preservar|manter|bloque|considerar|ser substitu|ser mantid|contemplar)")
_ATOR = re.compile(r"(?i)\b(usu[aá]rios?|administrador(?:es)?|aprovador(?:es)?|comprador(?:es)?|"
                   r"analistas?|gestor(?:es)?|consultor(?:es)?)\b(?:\s+(?:autorizad\w+|liberad\w+|cadastrad\w+))?")
_GAP_ID = re.compile(r"\b[A-Z]{2,3}-\d{3}(?:-[A-Z]{3})?\b")
_CAMPO = re.compile(r"(?i)campo\s*[\"“”]?\s*([^\"“”:]{3,80}?)\s*[\"“”]?\s*:\s*([ZY][A-Z0-9_]+-[A-Z0-9_]+)")
_SISTEMA = re.compile(r"(?i)\b(SAP\s*S/?4\s*HANA|S/?4\s*HANA|S4|SAP\s*ECC|ECC|SAP\s*BTP|BTP|CPI|"
                      r"Integration Suite|PI/PO|PDV|legado)\b")
_CHECK = re.compile(r"\(\s*[Xx]\s*\)\s*([^()]+?)(?=\s*\(|\s*$|\s{3,}|\t)")
_CTX_TIPO = [
    (re.compile(r"(?i)(tcode|transa[cç][aã]o)\s*(ecc|std sap)?\s*:?\s*$"), "TRANSACAO"),
    (re.compile(r"(?i)programa\s*(ecc)?\s*:?\s*$"), "PROGRAMA"),
    (re.compile(r"(?i)tabela\s*(ecc)?\s*:?\s*$"), "TABELA"),
    (re.compile(r"(?i)bad[iI]\s*$"), "BADI"),
    (re.compile(r"(?i)(nome da )?implementa[cç][aã]o\s*:?\s*$"), "IMPLEMENTACAO_BADI"),
    (re.compile(r"(?i)m[eé]todo\s*:?\s*$"), "METODO"),
    (re.compile(r"(?i)fun[cç][aã]o\s*:?\s*$"), "FUNCAO"),
    (re.compile(r"(?i)classe\s*$"), "CLASSE"),
    (re.compile(r"(?i)include\s*$"), "INCLUDE"),
    (re.compile(r"(?i)enhancement\s*$"), "ENHANCEMENT"),
]
_EXTRA_REF = [
    re.compile(r"(?i)(?:transa[cç][aã]o|tcode(?:\s*ecc)?:?)\s+([A-Z][A-Z0-9_]{2,})\b"),
    re.compile(r"(?i)bad[iI]\s*([A-Z][A-Z0-9_]{4,})\b"),
    re.compile(r"(?i)\binclude\s*([A-Z0-9_]{6,})\b"),
    re.compile(r"\b([A-Z][A-Z0-9]*_[A-Z0-9_]{3,})\b"),          # nomes SAP com "_"
]
_NAO_REF = {"AT-SELECTION-SCREEN", "USER_EXIT_OLD_CODE", "N_A"}


class _Ids:
    def __init__(self, prefix: str):
        self.p, self.n = prefix, 0

    def __call__(self) -> str:
        self.n += 1
        return f"{self.p}{self.n:03d}"


def _item(ids, cat, desc, sec: Section, blocks: list[Block], **kw) -> Item:
    trecho = blocks[0].text[:400]
    return Item(id=ids(), categoria=cat, descricao=desc[:500], classificacao=kw.pop("classificacao", "FATO_DA_EF"),
                confianca=kw.pop("confianca", "ALTA"),
                fonte=Fonte(secao=sec.sid, localizacao=[b.loc for b in blocks], trecho=trecho), **kw)


def _tipo_ref(tok: str, antes: str) -> str:
    for pat, tipo in _CTX_TIPO:
        if pat.search(antes[-40:]):
            return tipo
    return _tipo_por_nome(tok)


_SPLIT = re.compile(r"([A-Z0-9_~]{3,}) / ([A-Z0-9_]{3,})")


def reparar_quebras(texto: str, doc_texto: str) -> str:
    """Célula de tabela com quebra de linha no meio de um nome ('CALC_ITE / M_POST_CHECK').
    Junta os pedaços só se o nome inteiro existir em outro ponto da EF."""
    def junta(m):
        inteiro = m.group(1) + m.group(2)
        return inteiro if inteiro in doc_texto else m.group(0)
    return _SPLIT.sub(junta, texto)


def _refs_do_bloco(b: Block, doc_texto: str = "") -> list[tuple[str, str]]:
    """[(token, tipo)] do bloco. Pares tabela-campo primeiro; depois padrões."""
    texto = reparar_quebras(b.text, doc_texto) if b.kind == "table" else b.text
    achados: dict[str, str] = {}
    for m in _TAB_CAMPO.finditer(texto):
        achados.setdefault(m.group(0), "CAMPO_TABELA")
    resto = _TAB_CAMPO.sub(" ", texto)
    for pat in list(_REF_PATTERNS) + _EXTRA_REF:
        for m in pat.finditer(resto):
            bruto = m.group(1) if m.groups() else m.group(0)
            if bruto != bruto.upper():            # "include standard" -> não é nome técnico
                continue
            tok = bruto.strip("_/~")
            if len(tok) < 4 or tok in _NAO_REF or tok.isdigit():
                continue
            pos = texto.find(tok)
            achados.setdefault(tok, _tipo_ref(tok, texto[:max(pos, 0)]))
    toks = list(achados)
    # descarta tokens contidos em outro token do mesmo bloco (IF_EX_X dentro de IF_EX_X~METODO)
    return [(t, achados[t]) for t in toks if not any(o != t and t in o for o in toks)]


def extrair(doc: EFDocument) -> tuple[list[Item], dict]:
    ids = _Ids("D")
    itens: list[Item] = []
    ctx: dict = {"roles": {}, "narrativa": [], "sistemas": set(),
                 "doc_texto": " ".join(b.text for s in doc.sections for b in s.blocks)}
    id_proprio = (doc.header.get("ID GAP") or "").strip().upper()

    # ---------- capa / cabeçalho ----------
    capa = doc.sections[0]
    for chave in ("ID GAP", "Descrição GAP", "Projeto", "Fase do Projeto", "Módulo",
                  "Cenário empresarial", "Processo", "Autor"):
        if chave in doc.header:
            b = next((x for x in capa.blocks if f"{chave}:" in x.text), None)
            if b:
                itens.append(_item(ids, "IDENTIFICACAO", f"{chave}: {doc.header[chave]}", capa, [b],
                                   valor_original=doc.header[chave]))
    for b in capa.blocks:
        if re.search(r"(?i)^(remedia|desenvolvimento|evolu|simplifica)", b.text):
            itens.append(_item(ids, "TIPO_DEMANDA", f"Tipo de EF declarado na capa: {b.text}", capa, [b],
                               valor_original=b.text))
            break

    refs: dict[str, dict] = {}          # token -> {tipo, blocos, zonas, sistema}
    atores: dict[str, tuple[Section, Block]] = {}

    for sec in doc.sections:
        role = role_of(sec)
        ctx["roles"][sec.sid] = role
        blocos = [b for b in sec.blocks if not is_template(b)]
        if role in ("objetivo", "regras", "premissas", "fluxo", "novos_objetos", "processos"):
            ctx["narrativa"].append(sec.sid)
        zona = None                                  # None | "EXCLUIDO" | "INCLUIDO"
        contemplar = False

        for i, b in enumerate(blocos):
            t = b.text
            zona_bloco = zona
            frases = [f for f in re.split(r"(?<=[.;])\s+", t) if f.strip()]
            # checkboxes do Resumo/capa ("Requerimentos legais não serão atendidos") não são escopo
            frases_excl = [] if role in ("resumo", "capa") else [f for f in frases if _EXCL.search(f)]
            # zonas de escopo: a frase-gatilho vale para os blocos seguintes (lista)
            if frases_excl:
                for f in frases_excl:
                    itens.append(_item(ids, "ESCOPO_EXCLUIDO", f, sec, [b]))
                    itens[-1].fonte.trecho = f[:400]
                zona = "EXCLUIDO" if (frases[-1] in frases_excl) else zona
            elif zona == "EXCLUIDO":
                if t.rstrip().endswith(";") or ":" in t[:70]:
                    itens.append(_item(ids, "ESCOPO_EXCLUIDO", t, sec, [b]))
                else:
                    zona = zona_bloco = None
            if _INCL.search(t) and zona != "EXCLUIDO":
                zona = "INCLUIDO"

            # referências técnicas (todas as seções)
            for tok, tipo in _refs_do_bloco(b, ctx["doc_texto"]):
                z = zona_bloco or "SEM_ZONA"
                if any(tok in f.upper() for f in frases_excl):
                    z = "EXCLUIDO"
                r = refs.setdefault(tok, {"tipo": tipo, "blocos": [], "zonas": set(), "ecc": False, "sec": sec})
                r["blocos"].append(b)
                r["zonas"].add(z)
                if re.search(r"\bECC\b", t) and not re.search(r"(?i)S/?4", t):
                    r["ecc"] = True
                if r["tipo"] == "OUTRO" and tipo != "OUTRO":
                    r["tipo"] = tipo

            for m in _CAMPO.finditer(t):
                itens.append(_item(ids, "CAMPO", f"Campo \"{m.group(1).strip()}\" → {m.group(2)}", sec, [b],
                                   valor_original=m.group(2)))
            for m in _GAP_ID.finditer(t):
                if not (id_proprio and m.group(0).startswith(id_proprio)):
                    itens.append(_item(ids, "DEPENDENCIA", f"Relação com o GAP {m.group(0)}: {t[:200]}", sec, [b],
                                       valor_original=m.group(0)))
            for m in _SISTEMA.finditer(t):
                ctx["sistemas"].add(m.group(1))
            if role not in ("capa", "homologacao"):
                sem_rotulos = re.sub(r"[\"“][^\"”]*[\"”]", " ", t)       # ignora rótulos de campo
                for m in _ATOR.finditer(sem_rotulos):
                    base = _plain(m.group(1))
                    base = re.sub(r"(es|s)$", "", base) if not base.endswith("ores") else base[:-2]
                    base = {"usuario": "usuário", "aprovador": "aprovador", "administrador": "administrador"}.get(base, base)
                    if re.search(r"(?i)autorizad|liberad|cadastrad", m.group(0)):
                        base = "usuário autorizado (exceção)"
                    atores.setdefault(base, (sec, b))
            if re.search(r"(?i)esbo[cç]o", t):
                itens.append(_item(ids, "LAYOUT", f"Esboço de tela citado (imagem não lida em texto): {t}", sec, [b],
                                   classificacao="PONTO_A_CONFIRMAR", confianca="MEDIA"))
            elif re.search(r"(?i)^aba\s*[\"“]", t):
                itens.append(_item(ids, "LAYOUT", t, sec, [b]))
            if re.search(r"(?i)\banexo|bpmn|em anexo", t) and role != "teste_material":
                itens.append(_item(ids, "ANEXO", f"Anexo citado: {t[:200]}", sec, [b],
                                   classificacao="PONTO_A_CONFIRMAR", confianca="MEDIA"))

            # ---------- conteúdo por papel da seção ----------
            if role == "resumo":
                rot = t.split("|")[0].strip()
                marc = [re.sub(r"\s*/\s*$", "", x).strip(" /") for x in _CHECK.findall(t)]
                if marc and re.search(r"(?i)tipo de programa", rot):
                    itens.append(_item(ids, "TIPO_DEMANDA", f"Tipo de programa: {', '.join(marc)}", sec, [b]))
                elif marc and re.search(r"(?i)prioridade", rot):
                    itens.append(_item(ids, "IDENTIFICACAO", f"Prioridade: {marc[0]}", sec, [b]))
                elif re.search(r"(?i)impacto", rot):
                    for x in marc:
                        itens.append(_item(ids, "JUSTIFICATIVA", f"Impacto se não desenvolvido: {x}", sec, [b]))
                    outros = re.search(r"(?i)outros:\s*([^_][^|]{10,})", t)
                    if outros:
                        itens.append(_item(ids, "JUSTIFICATIVA", outros.group(1).strip(" _"), sec, [b]))
                elif marc and re.search(r"(?i)alternativa", rot):
                    itens.append(_item(ids, "JUSTIFICATIVA", f"Existe alternativa no S/4HANA? {marc[0]}", sec, [b]))
            elif role == "objetivo":
                itens.append(_item(ids, "OBJETIVO", t, sec, [b]))
            elif role == "processos":
                itens.append(_item(ids, "PROCESSO", t, sec, [b]))
            elif role == "regras":
                if re.search(r"(?i)exce[cç][aã]o", t) and _ACAO.search(t):
                    itens.append(_item(ids, "EXCECAO", t, sec, [b]))
                elif _ACAO.search(t) and zona != "EXCLUIDO":
                    itens.append(_item(ids, "REGRA", t, sec, [b]))
                elif re.search(r"(?i)^atualmente", t):
                    itens.append(_item(ids, "AS_IS", t, sec, [b]))
            elif role == "premissas":
                if re.search(r"(?i)contemplar:\s*$", t):
                    contemplar = True
                    continue
                cat = "ESCOPO_INCLUIDO" if contemplar and len(t) < 220 else "PREMISSA"
                if cat == "PREMISSA":
                    contemplar = False
                itens.append(_item(ids, cat, t, sec, [b]))
            elif role == "fluxo":
                itens.append(_item(ids, "TO_BE", f"Passo {i + 1}: {t}", sec, [b]))
            elif role == "sistemas" and len(t) > 3:
                itens.append(_item(ids, "SISTEMA", t, sec, [b]))
            elif role == "novos_objetos":
                if re.search(r"(?i)ser[aá] desenvolvid|ser[aá] criad|nova aplica", t):
                    itens.append(_item(ids, "COMPONENTE", t, sec, [b], natureza="NOVO", ancora=t[:120],
                                       confianca="MEDIA"))
                else:
                    itens.append(_item(ids, "TO_BE", t, sec, [b]))
            elif role == "enh_regra" and "|" in t and not re.search(r"(?i)^objeto\s*\|", t):
                obj, regra = [x.strip(" /") for x in t.split("|", 1)]
                itens.append(_item(ids, "REGRA", f"[{obj}] {regra}", sec, [b]))
            elif role == "enh_implicito" and "|" in t and not b.loc.endswith(".r0"):
                itens.append(_item(ids, "ESCOPO_INCLUIDO",
                                   f"Uso declarado de ponto de ampliação implícito: {t}", sec, [b]))
            elif role == "enh_ampliacoes" and "|" in t and not b.loc.endswith(".r0"):
                cols = [x.strip(" /") for x in t.split("|")]
                desc = cols[-2] if len(cols) >= 3 else cols[-1]
                nat, conf = "REMEDIACAO", "MEDIA"
                if re.search(r"(?i)desenvolvid|criad|\bnov[oa]\b|aplica[cç][aã]o fiori", t) and \
                        not re.search(r"(?i)existente", t):
                    nat, conf = "NOVO", "ALTA"
                elif re.search(r"(?i)mantid|remedi|adequa|preserv|migrar", desc):
                    conf = "ALTA"
                nome = cols[0].replace(" / ", " ").strip()
                tecnico = bool(re.search(r"\b[A-Z][A-Z0-9_]{3,}\b", nome))
                itens.append(_item(ids, "COMPONENTE", f"{nome} — {desc}", sec, [b], natureza=nat,
                                   objeto_origem=nome if tecnico and nat != "NOVO" else None,
                                   ancora=None if tecnico and nat != "NOVO" else nome, confianca=conf))
            elif role == "enh_requisitos" and "|" in t and not re.search(r"(?i)^requisito", t):
                rot, val = [x.strip(" /") for x in t.split("|", 1)]
                r = _plain(rot)
                if "objetivo" in r:
                    itens.append(_item(ids, "OBJETIVO", val, sec, [b]))
                elif "fiorizacao" in r and re.match(r"(?i)sim", val):
                    itens.append(_item(ids, "COMPONENTE", val, sec, [b], natureza="NOVO", ancora=val[:120],
                                       confianca="MEDIA"))
                elif "alternativa" in r:
                    itens.append(_item(ids, "JUSTIFICATIVA", val, sec, [b]))
                elif val:
                    itens.append(_item(ids, "ESCOPO_INCLUIDO", f"{rot}: {val}", sec, [b]))
            elif role == "teste_proc":
                itens.append(_item(ids, "TESTE", t, sec, [b]))
            elif role == "teste_result":
                itens.append(_item(ids, "ACEITE", t, sec, [b]))
            elif role == "teste_material":
                itens.append(_item(ids, "ANEXO", f"Material de teste: {t}", sec, [b]))
            elif role == "nfr":
                itens.append(_item(ids, "REQ_NAO_FUNCIONAL", f"{sec.title}: {t}", sec, [b]))

    # ---------- componentes duplicados (mesmo objeto descrito em mais de uma seção) ----------
    vistos: dict[str, Item] = {}
    unicos: list[Item] = []
    for it in itens:
        if it.categoria != "COMPONENTE":
            unicos.append(it)
            continue
        chave = re.sub(r"^sim\.?\s*", "", _plain(it.descricao))[:55]
        if it.natureza == "NOVO" and chave in vistos:
            vistos[chave].fonte.localizacao += it.fonte.localizacao
            continue
        vistos[chave] = it
        unicos.append(it)
    itens = unicos

    # ---------- atores ----------
    for chave, (sec, b) in atores.items():
        itens.append(_item(ids, "ATOR", f"Ator citado: {chave}", sec, [b]))

    # ---------- referências técnicas consolidadas ----------
    for tok, r in sorted(refs.items()):
        zonas = r["zonas"]
        escopo = "EXCLUIDO" if zonas == {"EXCLUIDO"} else ("INCLUIDO" if "INCLUIDO" in zonas else "INDEFINIDO")
        nota = ""
        if escopo == "EXCLUIDO":
            nota = " Escopo inferido: citado apenas na lista de objetos não contemplados."
        elif escopo == "INCLUIDO":
            nota = " Escopo inferido: citado na lista de objetos a remediar/manter."
        n = len(r["blocos"])
        itens.append(_item(ids, "REF_TECNICA", f"{r['tipo'].title()} citado em {n} ponto(s) da EF.{nota}",
                           r["sec"], [r["blocos"][0]], valor_original=tok, tipo_objeto=r["tipo"],
                           escopo=escopo, sistema="ECC" if r["ecc"] else None))
    ctx["n_refs"] = len(refs)
    return itens, ctx


# ---------------------------------------------------------------------------
# Critérios e plano determinísticos
# ---------------------------------------------------------------------------
def criterios(itens: list[Item], ctx: dict) -> list[Criterio]:
    tem = lambda *c: [i for i in itens if i.categoria in c]  # noqa: E731
    out = []

    def c(cod, bloq, evid, locs=()):
        out.append(Criterio(codigo=cod, bloqueia=bloq, evidencia=evid, localizacao=list(locs), origem="regra"))

    obj = tem("OBJETIVO")
    c("B01", not (obj or tem("JUSTIFICATIVA", "AS_IS")), f"{len(obj)} item(ns) de objetivo e "
      f"{len(tem('JUSTIFICATIVA'))} de justificativa extraídos.")
    c("B02", not obj, f"{len(obj)} item(ns) de objetivo." if obj else "Nenhum objetivo identificado.")
    proc, ator = tem("PROCESSO", "AS_IS", "TO_BE"), tem("ATOR")
    c("B03", not (proc and ator), f"{len(proc)} item(ns) de processo/fluxo e {len(ator)} ator(es).")
    refs = [i for i in tem("REF_TECNICA", "ANCORA_FUNCIONAL") if i.escopo != "EXCLUIDO"]
    c("B04", not refs, f"{len(refs)} referência(s) técnica(s) ou âncora(s) no escopo ou indefinidas.")
    c("B05", not (tem("SISTEMA") or ctx["sistemas"]),
      f"Sistemas citados: {', '.join(sorted(ctx['sistemas'])) or 'nenhum'}.")
    anexos = [i for i in tem("ANEXO") if i.classificacao == "PONTO_A_CONFIRMAR"]
    c("B08", False, f"{len(anexos)} anexo(s) citado(s) e não fornecido(s); a essencialidade deve ser "
      "confirmada." if anexos else "Nenhum anexo citado como fonte de regra, layout ou mapeamento.")
    sem = [i for i in tem("COMPONENTE") if i.natureza == "REMEDIACAO" and not (i.objeto_origem or i.ancora)]
    c("B09", bool(sem), f"{len(sem)} componente(s) de remediação sem objeto de origem." if sem
      else "Todos os componentes de remediação têm objeto de origem.")
    return out


_VERIF = {
    "TRANSACAO": ("Confirmar a transação e o programa/objeto associado", "existência de objeto"),
    "PROGRAMA": ("Ler o código-fonte e localizar os controles citados", "leitura de código"),
    "INCLUDE": ("Ler o include e localizar o enhancement citado", "leitura de código"),
    "CLASSE": ("Ler a classe e os métodos citados", "leitura de código"),
    "METODO": ("Ler a implementação do método", "leitura de código"),
    "FUNCAO": ("Ler a função e seus pontos de chamada", "leitura de código + where-used"),
    "BADI": ("Listar implementações ativas da BAdI", "existência de objeto"),
    "IMPLEMENTACAO_BADI": ("Confirmar a implementação e seu status", "existência de objeto"),
    "EXIT": ("Confirmar o projeto de ampliação ativo e o include Z associado", "existência de objeto"),
    "ENHANCEMENT": ("Localizar a implementação de enhancement e o código", "leitura de código"),
    "TABELA": ("Ler a estrutura DDIC (somente leitura)", "estrutura DDIC"),
    "CAMPO_TABELA": ("Confirmar o campo na tabela", "estrutura DDIC"),
}


def plano(itens: list[Item]) -> list[Verificacao]:
    grupos: dict[tuple[str, str], list[str]] = {}
    for i in itens:
        if i.categoria != "REF_TECNICA" or i.escopo == "EXCLUIDO":
            continue
        obj, tipo = _VERIF.get(i.tipo_objeto or "", ("Identificar o tipo do objeto no repositório", "identificação"))
        grupos.setdefault((obj, tipo), []).append(i)
    out = []
    for n, ((obj, tipo), its) in enumerate(sorted(grupos.items(), key=lambda kv: kv[0][1]), start=1):
        pri = "ALTA" if any(i.escopo == "INCLUIDO" for i in its) else "MEDIA"
        out.append(Verificacao(id=f"V{n:02d}", objetivo=obj, alvos=[i.id for i in its], tipo=tipo, prioridade=pri))
    return out
