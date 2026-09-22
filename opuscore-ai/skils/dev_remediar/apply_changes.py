# -*- coding: utf-8 -*-
"""
===============================================================================
 apply_changes.py  —  O APLICADOR DE CORREÇÕES (a parte SEM Inteligência Artificial)
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Ele pega a "lista de correções" que a IA produziu e aplica essas correções no
    código, de forma mecânica e 100% previsível (sem IA nesta etapa).

O PORQUÊ DESTA SEPARAÇÃO (é a ideia mais importante da solução):
    A remediação tem DUAS fases:
      Fase 1 (com IA)   : a IA LÊ o código e devolve uma lista dizendo
                          "troque ISTO por AQUILO, e revise MANUALMENTE aquele
                          outro trecho". Ela NÃO reescreve o arquivo inteiro.
      Fase 2 (este arquivo, SEM IA): o Python pega essa lista e faz as trocas.

    Por que separar? Segurança e economia. A IA pode errar ou "alucinar"; então
    nunca deixamos ela reescrever o arquivo direto. Em vez disso, ela só diz o
    que mudar, e o Python confere e aplica com regras rígidas. Bônus: a IA
    devolve pouco texto (só as trocas), o que gasta menos.

A REGRA DE SEGURANÇA:
    Cada correção tem o trecho EXATO do código original que deve
    ser trocado. O Python só aplica a troca se trecho aparecer EXATAMENTE
    UMA vez no código. Se não achar, ou se achar em vários lugares (ambíguo), a
    correção é RECUSADA e registrada — nunca aplicada no escuro. O código original
    jamais é corrompido.

TRÊS RESULTADOS POSSÍVEIS PARA CADA ITEM:
    - applied  (aplicado): a troca foi feita, envolta em marcadores BEGIN/END.
    - flagged  (sinalizado): não é uma troca, é um aviso "revise isto à mão".
    - rejected (recusado): a âncora não bateu direito => nada foi feito.
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ApplyResult:
    """A "ficha de resultado" da aplicação: o código novo + as listas do que foi
    aplicado, recusado e sinalizado."""
    new_source: str                                     # o código já corrigido
    applied: list[dict] = field(default_factory=list)   # trocas feitas
    rejected: list[dict] = field(default_factory=list)  # trocas recusadas
    flagged: list[dict] = field(default_factory=list)   # avisos de revisão manual
    flag_rejected: list[dict] = field(default_factory=list)  # avisos recusados

    @property
    def ok(self) -> bool:
        """Deu tudo certo? (nada foi recusado)"""
        return not self.rejected and not self.flag_rejected

    def summary(self) -> str:
        """Um resuminho em uma linha, para o relatório."""
        return (f"applied={len(self.applied)} "
                f"rejected={len(self.rejected)} "
                f"flagged={len(self.flagged)} "
                f"flag_rejected={len(self.flag_rejected)}")


def _begin(comment_style: str, reason: str, rule: Optional[str]) -> str:
    """Monta o cabeçalho do marcador de MODIFICAÇÃO (o bloco "BEGIN OF
    MODIFICATION" que aparece antes do código trocado, explicando o motivo)."""
    sep = comment_style + ("-" * 98)                    # a linha separadora
    rule_line = f"{comment_style} Rule   : {rule}\n" if rule else ""
    return (
        f"{sep}\n"
        f"{comment_style} BEGIN OF MODIFICATION - Capgemini SAP AI Remediation\n"
        f"{comment_style} Reason : {reason}\n"
        f"{rule_line}"
        f"{sep}\n"
    )


def _end(comment_style: str) -> str:
    """Monta o rodapé do marcador de MODIFICAÇÃO (o bloco "END OF MODIFICATION")."""
    sep = comment_style + ("-" * 98)
    return (
        f"{sep}\n"
        f"{comment_style} END OF MODIFICATION - Capgemini SAP AI Remediation\n"
        f"{sep}\n"
    )


def _flag(comment_style: str, reason: str, source: Optional[str] = None) -> str:
    """Monta o marcador de REVISÃO MANUAL (o aviso "MANUAL REVIEW REQUIRED", que é
    inserido acima do trecho sem alterá-lo)."""
    sep = comment_style + ("-" * 98)
    source_line = f"{comment_style} Source : {source}\n" if source else ""
    return (
        f"{sep}\n"
        f"{comment_style} MANUAL REVIEW REQUIRED - Capgemini SAP AI Remediation\n"
        f"{comment_style} Reason : {reason}\n"
        f"{source_line}"
        f"{sep}\n"
    )


def load_change_set(path_or_str: str) -> dict:
    """Carrega a lista de correções (o "change-set"), seja de um arquivo, seja de
    um texto JSON já pronto."""
    text = path_or_str
    if not path_or_str.lstrip().startswith("{"):       # não começa com '{' => é caminho
        with open(path_or_str, "r", encoding="utf-8") as f:
            text = f.read()
    return json.loads(text)                            # transforma o texto JSON em dados


def apply_change_set(source: str, change_set: dict, comment_style: str = '"') -> ApplyResult:
    """A FUNÇÃO PRINCIPAL: aplica a lista de correções ao código, de forma segura.

    A ordem importa: aplicamos uma troca de cada vez sobre o texto que vai
    evoluindo, exigindo a cada passo que a âncora apareça EXATAMENTE uma vez no
    texto atual. Isso mantém cada edição sem ambiguidade. Âncoras que não batem
    são recusadas, não forçadas."""
    result = ApplyResult(new_source=source)
    text = source

    # --- TROCAS (substituem a âncora pelo novo código, com os marcadores) ---
    for chg in change_set.get("changes", []):
        cid = chg.get("id", "?")
        anchor = chg.get("anchor", "")                 # o trecho exato a trocar
        replacement = chg.get("replacement", "")       # o código novo
        reason = chg.get("reason", "(no reason given)")
        rule = chg.get("rule")

        if not anchor:                                 # sem âncora => recusa
            result.rejected.append({"id": cid, "why": "empty anchor"})
            continue
        count = text.count(anchor)                     # quantas vezes a âncora aparece?
        if count == 0:                                 # nenhuma => recusa
            result.rejected.append({"id": cid, "why": "anchor not found"})
            continue
        if count > 1:                                  # várias => ambíguo => recusa
            result.rejected.append({"id": cid, "why": f"anchor ambiguous ({count} matches)"})
            continue

        # Monta o bloco: cabeçalho + código novo + rodapé, e faz a troca (1 vez).
        wrapped = _begin(comment_style, reason, rule) + \
            (replacement.rstrip("\n") + "\n") + _end(comment_style)
        text = text.replace(anchor, wrapped, 1)
        result.applied.append({"id": cid, "unit": chg.get("unit"), "rule": rule})

    # --- SINALIZAÇÕES (inserem o aviso acima do trecho, sem mudar o código) ---
    for flg in change_set.get("flags", []):
        fid = flg.get("id", "?")
        anchor = flg.get("anchor", "")
        reason = flg.get("reason", "(no reason given)")

        if not anchor:
            result.flag_rejected.append({"id": fid, "why": "empty anchor"})
            continue
        count = text.count(anchor)
        if count == 0:
            result.flag_rejected.append({"id": fid, "why": "anchor not found"})
            continue

        # Um aviso é uma nota de revisão, não uma mudança de código: se a âncora
        # aparece várias vezes, marcamos TODAS (diferente das trocas, que são
        # recusadas quando ambíguas, para evitar substituição errada).
        source = flg.get("source_practice") or ""
        marker = _flag(comment_style, reason, source or None)
        text = text.replace(anchor, marker + anchor)
        result.flagged.append({"id": fid, "unit": flg.get("unit"),
                               "occurrences": count, "source_practice": source})

    result.new_source = text                           # guarda o código final
    return result


def audit_report(change_set: dict, result: ApplyResult) -> str:
    """Monta um relatório legível (auditoria) do que foi aplicado, sinalizado e
    recusado — para a pessoa conferir depois."""
    obj = change_set.get("object", "?")
    mode = change_set.get("mode", "?")
    lines = [f"# Audit — object={obj} mode={mode}", result.summary(), ""]
    if result.applied:
        lines.append("APPLIED:")
        for a in result.applied:
            lines.append(f"  ✓ {a['id']}  unit={a.get('unit')}  rule={a.get('rule')}")
    if result.flagged:
        lines.append("FLAGGED (manual review):")
        for f in result.flagged:
            lines.append(f"  ⚑ {f['id']}  unit={f.get('unit')}")
    if result.rejected:
        lines.append("REJECTED changes (NOT applied — anchor did not match cleanly):")
        for r in result.rejected:
            lines.append(f"  ✗ {r['id']}  {r['why']}")
    if result.flag_rejected:
        lines.append("REJECTED flags:") 
        for r in result.flag_rejected:
            lines.append(f"  ✗ {r['id']}  {r['why']}")
    return "\n".join(lines)