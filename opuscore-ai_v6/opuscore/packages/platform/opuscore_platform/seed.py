"""Dados de demonstração (usuário local, projeto e ambientes) e sincronização dos
perfis dos consultores a partir dos plugins instalados (idempotente)."""
from __future__ import annotations

from sqlmodel import select

from .db.engine import get_session
from .db.modelos import (AgentProfile, AgentProfileVersion, AgentSkill, EmbeddingModel, KnowledgeCollection,
                         OwnerType, Project, ProjectAgentAssignment, SapProduct, SystemConnection, User, Visibility)


def seed_demo() -> bool:
    """Cria o usuário local e o projeto de demonstração se o banco estiver vazio."""
    with get_session() as s:
        if s.exec(select(Project)).first():
            return False
        if not s.exec(select(User).where(User.username == "local")).first():
            s.add(User(username="local", display_name="Usuário local", is_admin=True))
        if not s.exec(select(EmbeddingModel).where(EmbeddingModel.name == "bge-m3")).first():
            s.add(EmbeddingModel(name="bge-m3", dim=1024, provider="ollama"))
        proj = Project(name="Projeto Agro", client="Agro", description="Modernização S/4HANA")
        s.add(proj)
        s.commit()
        s.refresh(proj)
        s.add(SystemConnection(project_id=proj.id, product=SapProduct.S4_ADT, environment="DEV", name="S/4HANA DEV",
                               purpose="Análise ADT (leitura)", status="configured", allowed_operations=["read"],
                               read_only=True))
        s.add(SystemConnection(project_id=proj.id, product=SapProduct.BTP, environment="DEV", name="SAP BTP DEV",
                               purpose="Serviços/apps (futuro)", status="configured", allowed_operations=["read"],
                               read_only=True))
        s.add(KnowledgeCollection(project_id=proj.id, owner_type=OwnerType.PROJECT, owner_id=proj.id,
                                  visibility=Visibility.PROJECT_SHARED, name="RAG Global do Projeto"))
        s.commit()
    return True


def sincronizar_perfis(plugins: list) -> list[str]:
    """Para cada plugin: cria o perfil se faltar e o atribui a todos os projetos.
    Não sobrescreve um perfil existente (edições feitas na tela são preservadas)."""
    criados = []
    with get_session() as s:
        projetos = s.exec(select(Project)).all()
        for p in plugins:
            m, perfil = p.manifesto, p.perfil()
            prof = s.exec(select(AgentProfile).where(AgentProfile.key == m.key)).first()
            if prof is None:
                prof = AgentProfile(key=m.key, name=m.nome, role=m.area, specialty=m.especialidade, modules=[m.area],
                                    seniority="senior", description=perfil.persona[:180], owner="OPUS", status="active")
                s.add(prof)
                s.commit()
                s.refresh(prof)
                s.add(AgentProfileVersion(profile_id=prof.id, version=1, persona=perfil.persona,
                                          instructions=perfil.instrucoes))
                for sk in perfil.skills:
                    s.add(AgentSkill(profile_id=prof.id, name=sk))
                criados.append(m.key)
            for proj in projetos:
                ja = s.exec(select(ProjectAgentAssignment).where(ProjectAgentAssignment.project_id == proj.id,
                                                                 ProjectAgentAssignment.profile_id == prof.id)).first()
                if ja is None:
                    s.add(ProjectAgentAssignment(project_id=proj.id, profile_id=prof.id, profile_version=1,
                                                 status_label=m.status_label, current_work=m.trabalho_atual))
        s.commit()
    return criados
