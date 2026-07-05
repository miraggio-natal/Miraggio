from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Funcionario, Candidato
from app.schemas import (
    FuncionarioCreate,
    FuncionarioUpdate,
    CandidatoCreate,
    CandidatoUpdate,
)


class FuncionarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: FuncionarioCreate) -> Funcionario:
        funcionario = Funcionario(**dados.model_dump())
        self.db.add(funcionario)
        self.db.commit()
        self.db.refresh(funcionario)
        return funcionario

    def listar(
        self, busca: Optional[str] = None, skip: int = 0, limit: int = 200
    ) -> List[Funcionario]:
        query = self.db.query(Funcionario)
        if busca:
            termo = f"%{busca}%"
            query = query.filter(
                or_(
                    Funcionario.nome.ilike(termo),
                    Funcionario.email.ilike(termo),
                    Funcionario.cargo.ilike(termo),
                    Funcionario.departamento.ilike(termo),
                )
            )
        return query.order_by(Funcionario.nome).offset(skip).limit(limit).all()

    def buscar_por_id(self, funcionario_id: int) -> Optional[Funcionario]:
        return (
            self.db.query(Funcionario)
            .filter(Funcionario.id == funcionario_id)
            .first()
        )

    def buscar_por_email(self, email: str) -> Optional[Funcionario]:
        return (
            self.db.query(Funcionario).filter(Funcionario.email == email).first()
        )

    def atualizar(
        self, funcionario: Funcionario, dados: FuncionarioUpdate
    ) -> Funcionario:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(funcionario, campo, valor)
        self.db.commit()
        self.db.refresh(funcionario)
        return funcionario

    def remover(self, funcionario: Funcionario) -> None:
        self.db.delete(funcionario)
        self.db.commit()


class CandidatoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: CandidatoCreate) -> Candidato:
        candidato = Candidato(**dados.model_dump())
        self.db.add(candidato)
        self.db.commit()
        self.db.refresh(candidato)
        return candidato

    def listar(
        self,
        busca: Optional[str] = None,
        status: Optional[str] = None,
        departamento: Optional[str] = None,
        cargo: Optional[str] = None,
        experiencia_min: Optional[int] = None,
        pontuacao_min: Optional[int] = None,
        habilidade: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[Candidato]:
        query = self.db.query(Candidato)
        if busca:
            termo = f"%{busca}%"
            query = query.filter(
                or_(
                    Candidato.nome.ilike(termo),
                    Candidato.email.ilike(termo),
                    Candidato.cargo_pretendido.ilike(termo),
                )
            )
        if status:
            query = query.filter(Candidato.status == status)
        if departamento:
            query = query.filter(
                Candidato.departamento_pretendido.ilike(f"%{departamento}%")
            )
        if cargo:
            query = query.filter(Candidato.cargo_pretendido.ilike(f"%{cargo}%"))
        if experiencia_min is not None:
            query = query.filter(Candidato.experiencia_anos >= experiencia_min)
        if pontuacao_min is not None:
            query = query.filter(Candidato.pontuacao >= pontuacao_min)
        if habilidade:
            query = query.filter(Candidato.habilidades.ilike(f"%{habilidade}%"))
        return (
            query.order_by(Candidato.pontuacao.desc(), Candidato.nome)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def buscar_por_id(self, candidato_id: int) -> Optional[Candidato]:
        return (
            self.db.query(Candidato).filter(Candidato.id == candidato_id).first()
        )

    def buscar_por_email(self, email: str) -> Optional[Candidato]:
        return self.db.query(Candidato).filter(Candidato.email == email).first()

    def atualizar(self, candidato: Candidato, dados: CandidatoUpdate) -> Candidato:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(candidato, campo, valor)
        self.db.commit()
        self.db.refresh(candidato)
        return candidato

    def salvar(self, candidato: Candidato) -> Candidato:
        self.db.commit()
        self.db.refresh(candidato)
        return candidato

    def remover(self, candidato: Candidato) -> None:
        self.db.delete(candidato)
        self.db.commit()
