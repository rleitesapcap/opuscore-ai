"""Semente do MVP: usuário local + os dois agentes da Fase 1.

Idempotente: se o perfil (por 'key') já existir, não duplica.
Rode: python -m opuscore.platform.seed
"""
from __future__ import annotations

from sqlmodel import select

from .db import get_session, init_db
from .models import (
    AgentProfile,
    AgentProfileVersion,
    AgentSkill,
    EmbeddingModel,
    User,
)

CLEAN_CORE_RUBRIC = [
    "É modificação de objeto SAP standard? (se sim: bloqueador)",
    "Acessa objeto SAP não liberado? (atenção/bloqueador)",
    "Usa released API / released CDS (contrato C1)? (favorável)",
    "Tipo de extensibilidade: key-user / developer (ABAP Cloud) / side-by-side (BTP)?",
    "Enhancement liberado (BAdI) vs implícito/explícito não recomendado (atenção)?",
    "Acesso a dado via CDS/OData liberado vs SELECT direto em tabela standard (atenção)?",
    "Language version: ABAP Cloud vs ABAP clássico irrestrito (atenção)?",
    "Impacto de Simplification Item / objeto deprecado na release-alvo?",
]


def _ensure_profile(sess, *, key, name, role, specialty, modules, persona, instructions, skills):
    exists = sess.exec(select(AgentProfile).where(AgentProfile.key == key)).first()
    if exists:
        return exists
    prof = AgentProfile(
        key=key, name=name, role=role, specialty=specialty, modules=modules,
        seniority="senior", description=persona[:180], owner="OPUS", status="active",
    )
    sess.add(prof)
    sess.commit()
    sess.refresh(prof)
    sess.add(AgentProfileVersion(
        profile_id=prof.id, version=1, persona=persona, instructions=instructions,
        output_format="Markdown; classifique cada conclusão como FATO DA FONTE / "
        "ENTENDIMENTO DO AGENTE / RECOMENDAÇÃO / RISCO / PONTO A CONFIRMAR.",
    ))
    for sk in skills:
        sess.add(AgentSkill(profile_id=prof.id, **sk))
    sess.commit()
    return prof


def seed() -> None:
    init_db()
    with get_session() as sess:
        if not sess.exec(select(User).where(User.username == "local")).first():
            sess.add(User(username="local", display_name="Operador local", is_admin=True))
            sess.commit()

        if not sess.exec(select(EmbeddingModel).where(EmbeddingModel.name == "bge-m3")).first():
            sess.add(EmbeddingModel(name="bge-m3", dim=1024, provider="ollama"))
            sess.commit()

        _ensure_profile(
            sess,
            key="arquiteto",
            name="Arquiteto de Soluções SAP",
            role="Arquitetura de soluções",
            specialty="S/4HANA, Clean Core, integração",
            modules=["cross"],
            persona="Arquiteto de Soluções SAP sênior, rigoroso e evidence-based.",
            instructions=(
                "Analise a solução proposta produzindo AS-IS, TO-BE, riscos, lacunas, "
                "recomendações e insumos funcionais. Baseie-se em evidência (documentos "
                "do projeto e leitura do sistema via ADT). Avalie Clean Core. Nunca invente "
                "objeto, campo ou número de SAP Note."
            ),
            skills=[
                {
                    "name": "Análise de Arquitetura",
                    "category": "arquitetura",
                    "description": "Produz visão arquitetural rastreável a partir do insumo.",
                    "allowed_tools": ["rag_search", "sap_object_report", "sap_where_used"],
                    "allowed_sources": ["PROJECT_SHARED", "AGENT_PROFILE_PRIVATE"],
                    "quality_checklist": ["AS-IS", "TO-BE", "riscos", "lacunas", "rastreabilidade"],
                },
                {
                    "name": "Avaliação Clean Core",
                    "category": "clean-core",
                    "description": "Classifica aderência Clean Core com rubrica objetiva.",
                    "allowed_tools": ["sap_object_report", "sap_where_used"],
                    "steps": "\n".join(CLEAN_CORE_RUBRIC),
                    "quality_checklist": ["evidência do ADT por item", "veredito justificado"],
                },
            ],
        )

        _ensure_profile(
            sess,
            key="dev-abap",
            name="Desenvolvedor ABAP/RAP",
            role="Desenvolvimento",
            specialty="ABAP, ABAP Cloud, RAP, CDS, OData",
            modules=["dev"],
            persona="Desenvolvedor ABAP/RAP sênior; especialista em ABAP Cloud e S/4HANA.",
            instructions=(
                "Analise objetos do repositório via ADT (source, DDIC, where-used). Monte "
                "relatórios com evidência, avalie impacto de mudança e aplique a rubrica de "
                "Clean Core. Nunca altera o sistema (somente leitura). Nunca invente objeto, "
                "campo ou número de SAP Note."
            ),
            skills=[
                {
                    "name": "Análise de Objeto",
                    "category": "análise",
                    "description": "Source, DDIC e where-used de um objeto + grafo de dependências.",
                    "allowed_tools": ["sap_object_report", "sap_where_used", "sap_get_source"],
                    "allowed_sources": ["PROJECT_SHARED", "AGENT_PROFILE_PRIVATE"],
                    "quality_checklist": ["finalidade", "quem usa", "risco de impacto"],
                },
                {
                    "name": "Clean Core Check",
                    "category": "clean-core",
                    "description": "Rubrica verificável de aderência a Clean Core.",
                    "allowed_tools": ["sap_object_report", "sap_where_used"],
                    "steps": "\n".join(CLEAN_CORE_RUBRIC),
                    "quality_checklist": ["evidência do ADT por item", "compliant/atenção/bloqueador"],
                },
            ],
        )
    print("Seed concluído: usuário 'local' + agentes 'arquiteto' e 'dev-abap'.")


if __name__ == "__main__":
    seed()
