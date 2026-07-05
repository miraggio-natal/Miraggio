from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Funcionario, Candidato, StatusSelecao
from app.repository import FuncionarioRepository, CandidatoRepository
from app.schemas import (
    FuncionarioCreate,
    FuncionarioUpdate,
    CandidatoCreate,
    CandidatoUpdate,
    ContratarRequest,
)


class FuncionarioNaoEncontrado(Exception):
    pass


class EmailJaCadastrado(Exception):
    pass


class CandidatoNaoEncontrado(Exception):
    pass


class SelecaoInvalida(Exception):
    pass


class FuncionarioService:
    def __init__(self, db: Session):
        self.repo = FuncionarioRepository(db)

    def criar(self, dados: FuncionarioCreate) -> Funcionario:
        if self.repo.buscar_por_email(dados.email):
            raise EmailJaCadastrado(f"Já existe um funcionário com o e-mail {dados.email}.")
        return self.repo.criar(dados)

    def listar(self, busca: Optional[str] = None, skip: int = 0, limit: int = 200) -> List[Funcionario]:
        return self.repo.listar(busca=busca, skip=skip, limit=limit)

    def obter(self, funcionario_id: int) -> Funcionario:
        funcionario = self.repo.buscar_por_id(funcionario_id)
        if not funcionario:
            raise FuncionarioNaoEncontrado(f"Funcionário {funcionario_id} não encontrado.")
        return funcionario

    def atualizar(self, funcionario_id: int, dados: FuncionarioUpdate) -> Funcionario:
        funcionario = self.obter(funcionario_id)
        if dados.email and dados.email != funcionario.email:
            existente = self.repo.buscar_por_email(dados.email)
            if existente and existente.id != funcionario_id:
                raise EmailJaCadastrado(f"O e-mail {dados.email} já está em uso.")
        return self.repo.atualizar(funcionario, dados)

    def remover(self, funcionario_id: int) -> None:
        funcionario = self.obter(funcionario_id)
        self.repo.remover(funcionario)


class CandidatoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CandidatoRepository(db)
        self.funcionario_service = FuncionarioService(db)

    def criar(self, dados: CandidatoCreate) -> Candidato:
        if self.repo.buscar_por_email(dados.email):
            raise EmailJaCadastrado(f"Já existe um candidato com o e-mail {dados.email}.")
        return self.repo.criar(dados)

    def listar(self, **filtros) -> List[Candidato]:
        return self.repo.listar(**filtros)

    def obter(self, candidato_id: int) -> Candidato:
        candidato = self.repo.buscar_por_id(candidato_id)
        if not candidato:
            raise CandidatoNaoEncontrado(f"Candidato {candidato_id} não encontrado.")
        return candidato

    def atualizar(self, candidato_id: int, dados: CandidatoUpdate) -> Candidato:
        candidato = self.obter(candidato_id)
        if dados.email and dados.email != candidato.email:
            existente = self.repo.buscar_por_email(dados.email)
            if existente and existente.id != candidato_id:
                raise EmailJaCadastrado(f"O e-mail {dados.email} já está em uso.")
        return self.repo.atualizar(candidato, dados)

    def anexar_curriculo(self, candidato_id: int, nome_arquivo: str) -> Candidato:
        candidato = self.obter(candidato_id)
        candidato.curriculo_arquivo = nome_arquivo
        return self.repo.salvar(candidato)

    def mudar_status(self, candidato_id: int, novo_status: StatusSelecao) -> Candidato:
        candidato = self.obter(candidato_id)
        if candidato.status == StatusSelecao.CONTRATADO.value:
            raise SelecaoInvalida("Candidato já foi contratado; a fase não pode ser alterada.")
        if novo_status == StatusSelecao.CONTRATADO:
            self.contratar(candidato_id)
            return self.obter(candidato_id)
        candidato.status = novo_status.value
        return self.repo.salvar(candidato)

    def contratar(self, candidato_id: int, dados: Optional[ContratarRequest] = None) -> Funcionario:
        candidato = self.obter(candidato_id)
        if candidato.status == StatusSelecao.CONTRATADO.value:
            raise SelecaoInvalida("Este candidato já foi contratado.")

        salario = dados.salario if dados else None
        data_admissao = dados.data_admissao if dados else None

        func_create = FuncionarioCreate(
            nome=candidato.nome,
            email=candidato.email,
            cargo=candidato.cargo_pretendido,
            departamento=candidato.departamento_pretendido,
            telefone=candidato.telefone,
            salario=(salario if salario is not None else candidato.pretensao_salarial) or 0.0,
            ativo=True,
            data_admissao=data_admissao or date.today(),
        )

        funcionario = self.funcionario_service.criar(func_create)
        funcionario.candidato_id = candidato.id
        candidato.status = StatusSelecao.CONTRATADO.value
        self.db.commit()
        self.db.refresh(funcionario)
        return funcionario

    def remover(self, candidato_id: int) -> None:
        candidato = self.obter(candidato_id)
        self.repo.remover(candidato)
