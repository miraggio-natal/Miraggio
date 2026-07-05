import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Text, ForeignKey

from app.database import Base


class StatusSelecao(str, enum.Enum):
    INSCRITO = "inscrito"
    TRIAGEM = "triagem"
    ENTREVISTA = "entrevista"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"
    CONTRATADO = "contratado"


class Candidato(Base):
    __tablename__ = "candidatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, index=True)
    email = Column(String(120), nullable=False, unique=True, index=True)
    telefone = Column(String(30), nullable=True)
    cargo_pretendido = Column(String(80), nullable=False, index=True)
    departamento_pretendido = Column(String(80), nullable=True, index=True)
    resumo_profissional = Column(Text, nullable=True)
    experiencia_anos = Column(Integer, nullable=False, default=0)
    formacao = Column(String(160), nullable=True)
    habilidades = Column(Text, nullable=True)
    pretensao_salarial = Column(Float, nullable=True)
    curriculo_url = Column(String(255), nullable=True)
    curriculo_arquivo = Column(String(255), nullable=True)  # nome do PDF enviado
    status = Column(
        String(20), nullable=False, default=StatusSelecao.INSCRITO.value, index=True
    )
    pontuacao = Column(Integer, nullable=True, default=0)
    observacoes = Column(Text, nullable=True)
    data_inscricao = Column(Date, nullable=False, default=date.today)


class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, index=True)
    email = Column(String(120), nullable=False, unique=True, index=True)
    cargo = Column(String(80), nullable=False)
    departamento = Column(String(80), nullable=True, index=True)
    telefone = Column(String(30), nullable=True)
    salario = Column(Float, nullable=True, default=0.0)
    ativo = Column(Boolean, nullable=False, default=True)
    data_admissao = Column(Date, nullable=True, default=date.today)
    candidato_id = Column(
        Integer, ForeignKey("candidatos.id"), nullable=True, unique=True
    )
