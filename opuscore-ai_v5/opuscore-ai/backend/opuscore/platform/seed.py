"""Semente do MVP: usuário local, catálogo de agentes e um projeto-demo.

Cria 7 perfis de consultor (Fase 1 tem Arquiteto e Dev ABAP servidos pelo ADT;
os demais entram no catálogo e analisam documentos até seu MCP de dados existir),
um projeto "Projeto Agro" com os agentes associados e dois ambientes cadastrados.

Idempotente por 'key' (perfil) e por nome (projeto). Rode:
    python -m opuscore.platform.seed
"""
from __future__ import annotations

from sqlmodel import select

from .db import get_session, init_db
from .models import (
    AgentProfile,
    AgentProfileVersion,
    AgentSkill,
    EmbeddingModel,
    KnowledgeCollection,
    OwnerType,
    Project,
    ProjectAgentAssignment,
    SapProduct,
    SystemConnection,
    User,
    Visibility,
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

SAP_TOOLS = ["sap_object_report", "sap_where_used", "sap_get_source"]

# key, nome, role(área), specialty(subtítulo), tools, persona, instrução curta
PROFILES = [
    ("orquestrador", "Orquestrador", "Coordenação", "Fluxo e gates", [],
     "Orquestrador do squad: coordena tarefas, aprovações e handoffs entre consultores.",
     "Coordene o fluxo (gates, tarefas, handoffs). Não invente decisões nem aprove em nome do usuário."),
    ("arquiteto", "Arquiteto de Soluções", "Arquitetura SAP", "Solução e Clean Core",
     SAP_TOOLS + ["rag_search"],
     "Arquiteto de Soluções SAP sênior, rigoroso e evidence-based.",
     "Produza AS-IS, TO-BE, riscos, lacunas e recomendações a partir de evidência. Avalie Clean Core."),
    ("funcional-sd", "Consultor Funcional SD", "Processos SAP", "Vendas e distribuição",
     ["rag_search"],
     "Consultor Funcional SAP SD sênior (vendas, pricing, remessa, faturamento).",
     "Analise processos e requisitos de SD com base em documentos. Declare quando não puder verificar o sistema."),
    ("integracao", "Arquiteto de Integração", "Integração SAP", "Interfaces e SAP CI",
     ["rag_search"],
     "Arquiteto de Integração SAP (Integration Suite/CI, eventos, IDoc, APIs).",
     "Mapeie interfaces, padrões e impactos de integração a partir de documentos."),
    ("lider-tecnico", "Líder Técnico", "Revisão técnica", "Viabilidade e padrões",
     ["rag_search"],
     "Líder Técnico SAP: revisa viabilidade técnica e aderência a padrões.",
     "Revise completude e consistência dos entregáveis; registre parecer e pendências."),
    ("dev-abap", "Desenvolvedor ABAP", "Desenvolvimento", "ABAP e remediação",
     SAP_TOOLS + ["rag_search"],
     "Desenvolvedor ABAP/RAP sênior; especialista em ABAP Cloud e S/4HANA.",
     "Analise objetos via ADT (source, DDIC, where-used), avalie impacto e Clean Core. Somente leitura."),
    ("qualidade", "Analista de Qualidade", "Testes SAP", "Cenários e evidências",
     ["rag_search"],
     "Analista de Qualidade SAP: cenários de teste e evidências ponta a ponta.",
     "Monte cenários e critérios de teste a partir dos entregáveis aprovados."),
]

# rótulos de status/trabalho no projeto-demo (para a lista de consultores)
PROJECT_STATE = {
    "orquestrador": ("Ativo", "2 handoffs pendentes"),
    "arquiteto": ("Em análise", "Relatório de Arquitetura"),
    "funcional-sd": ("Ativo", "EF preliminar aguarda arquitetura"),
    "integracao": ("Ativo", "Mapeamento de interfaces"),
    "lider-tecnico": ("Ativo", "Revisão da EF"),
    "dev-abap": ("Ativo", "Aguardando EF aprovada"),
    "qualidade": ("Ativo", "Preparação de cenários"),
}


def _skills_for(key: str, tools: list[str]) -> list[dict]:
    skills = []
    if any(t.startswith("sap_") for t in tools):
        skills.append({
            "name": "Análise de Objeto", "category": "análise",
            "description": "Source, DDIC e where-used de um objeto + grafo de dependências.",
            "allowed_tools": [t for t in tools if t.startswith("sap_")],
            "quality_checklist": ["finalidade", "quem usa", "risco de impacto"],
        })
        skills.append({
            "name": "Clean Core Check", "category": "clean-core",
            "description": "Rubrica verificável de aderência a Clean Core.",
            "allowed_tools": ["sap_object_report", "sap_where_used"],
            "steps": "\n".join(CLEAN_CORE_RUBRIC),
            "quality_checklist": ["evidência do ADT por item", "compliant/atenção/bloqueador"],
        })
    else:
        skills.append({
            "name": "Análise documental", "category": "análise",
            "description": "Analisa documentos autorizados do projeto (RAG).",
            "allowed_tools": ["rag_search"],
            "quality_checklist": ["fato vs interpretação", "citação de fonte"],
        })
    return skills


def _ensure_profile(sess, key, name, role, specialty, tools, persona, instr):
    prof = sess.exec(select(AgentProfile).where(AgentProfile.key == key)).first()
    if prof:
        return prof
    prof = AgentProfile(
        key=key, name=name, role=role, specialty=specialty, modules=[role],
        seniority="senior", description=persona[:180], owner="OPUS", status="active",
    )
    sess.add(prof); sess.commit(); sess.refresh(prof)
    sess.add(AgentProfileVersion(
        profile_id=prof.id, version=1, persona=persona, instructions=instr,
        output_format="Markdown; classifique conclusões como FATO DA FONTE / ENTENDIMENTO / "
                      "RECOMENDAÇÃO / RISCO / PONTO A CONFIRMAR.",
    ))
    for sk in _skills_for(key, tools):
        sess.add(AgentSkill(profile_id=prof.id, **sk))
    sess.commit()
    return prof


def seed() -> None:
    init_db()
    with get_session() as sess:
        if not sess.exec(select(User).where(User.username == "local")).first():
            sess.add(User(username="local", display_name="Renato Leite", is_admin=True))
            sess.commit()
        user = sess.exec(select(User).where(User.username == "local")).first()

        if not sess.exec(select(EmbeddingModel).where(EmbeddingModel.name == "bge-m3")).first():
            sess.add(EmbeddingModel(name="bge-m3", dim=1024, provider="ollama")); sess.commit()

        profiles = {}
        for key, name, role, spec, tools, persona, instr in PROFILES:
            profiles[key] = _ensure_profile(sess, key, name, role, spec, tools, persona, instr)

        proj = sess.exec(select(Project).where(Project.name == "Projeto Agro")).first()
        if not proj:
            proj = Project(name="Projeto Agro", client="Agro", description="Modernização S/4HANA")
            sess.add(proj); sess.commit(); sess.refresh(proj)
            for key, prof in profiles.items():
                st, work = PROJECT_STATE.get(key, ("Ativo", ""))
                sess.add(ProjectAgentAssignment(
                    project_id=proj.id, profile_id=prof.id, profile_version=1,
                    status_label=st, current_work=work,
                ))
            sess.add(SystemConnection(
                project_id=proj.id, product=SapProduct.S4_ADT, environment="DEV",
                name="S/4HANA DEV", purpose="Análise ADT (leitura)", status="configured",
                allowed_operations=["read"], read_only=True,
            ))
            sess.add(SystemConnection(
                project_id=proj.id, product=SapProduct.BTP, environment="DEV",
                name="SAP BTP DEV", purpose="Serviços/apps (futuro)", status="configured",
                allowed_operations=["read"], read_only=True,
            ))
            sess.add(KnowledgeCollection(
                project_id=proj.id, owner_type=OwnerType.PROJECT, owner_id=proj.id,
                visibility=Visibility.PROJECT_SHARED, name="RAG Global do Projeto",
            ))
            sess.commit()
    print("Seed concluído: usuário 'local', 7 consultores e projeto 'Projeto Agro' com 2 ambientes.")




# ---------------------------------------------------------------------------
# Consultores acrescentados depois do seed inicial: garantidos a cada início
# da API (idempotente), para aparecerem também em bancos já existentes.
# ---------------------------------------------------------------------------
CONSULTORES_EXTRAS = [
    # (key, name, role, specialty, tools, persona, instructions, status_label, current_work)
    ("funcional-mm", "Consultor Funcional MM", "Funcional", "Materiais e compras",
     ["Geração de EF a partir do Workshop B", "Validação de EF por seção"],
     "Consultor funcional SAP MM sênior: gera o rascunho da EF a partir do Workshop B e valida EFs seção por "
     "seção, apontando o que falta e sugerindo a correção.",
     "Ajude a escrever e revisar Especificações Funcionais claras, testáveis e aderentes ao Clean Core. "
     "Nunca invente objetos, transações ou números de SAP Note.",
     "Ativo", "Gerar e validar EF"),
]


def garantir_consultores() -> None:
    """Idempotente: cria o perfil (se faltar) e o atribui a todos os projetos (se faltar)."""
    from .db import get_session
    from .models import Project, ProjectAgentAssignment

    with get_session() as sess:
        for key, name, role, spec, tools, persona, instr, st, work in CONSULTORES_EXTRAS:
            prof = _ensure_profile(sess, key, name, role, spec, tools, persona, instr)
            for proj in sess.exec(select(Project)).all():
                ja = sess.exec(select(ProjectAgentAssignment).where(
                    ProjectAgentAssignment.project_id == proj.id,
                    ProjectAgentAssignment.profile_id == prof.id)).first()
                if ja is None:
                    sess.add(ProjectAgentAssignment(project_id=proj.id, profile_id=prof.id, profile_version=1,
                                                    status_label=st, current_work=work))
        sess.commit()


def _listar_consultores() -> None:
    from .db import get_session
    from .models import AgentProfile, Project, ProjectAgentAssignment
    with get_session() as sess:
        for proj in sess.exec(select(Project)).all():
            rows = sess.exec(select(ProjectAgentAssignment, AgentProfile)
                             .where(ProjectAgentAssignment.project_id == proj.id)
                             .where(ProjectAgentAssignment.profile_id == AgentProfile.id)).all()
            print(f"Projeto '{proj.name}': {len(rows)} consultor(es)")
            for _, prof in rows:
                print(f"   - {prof.name} ({prof.key})")


if __name__ == "__main__":
    import sys
    from .db import init_db
    init_db()
    if "--consultores" in sys.argv:      # só garante os consultores extras (idempotente)
        garantir_consultores()
        _listar_consultores()
    else:
        seed()
