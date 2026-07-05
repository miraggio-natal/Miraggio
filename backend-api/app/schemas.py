from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models import StatusSelecao


class FuncionarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    cargo: str = Field(..., min_length=1, max_length=80)
    departamento: Optional[str] = Field(None, max_length=80)
    telefone: Optional[str] = Field(None, max_length=30)
    salario: Optional[float] = Field(0.0, ge=0)
    ativo: bool = True
    data_admissao: Optional[date] = None


class FuncionarioCreate(FuncionarioBase):
    pass


class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    cargo: Optional[str] = Field(None, min_length=1, max_length=80)
    departamento: Optional[str] = Field(None, max_length=80)
    telefone: Optional[str] = Field(None, max_length=30)
    salario: Optional[float] = Field(None, ge=0)
    ativo: Optional[bool] = None
    data_admissao: Optional[date] = None


class FuncionarioResponse(FuncionarioBase):
    id: int
    candidato_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class CandidatoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=30)
    cargo_pretendido: str = Field(..., min_length=1, max_length=80)
    departamento_pretendido: Optional[str] = Field(None, max_length=80)
    resumo_profissional: Optional[str] = None
    experiencia_anos: int = Field(0, ge=0, le=60)
    formacao: Optional[str] = Field(None, max_length=160)
    habilidades: Optional[str] = None
    pretensao_salarial: Optional[float] = Field(None, ge=0)
    curriculo_url: Optional[str] = Field(None, max_length=255)
    pontuacao: Optional[int] = Field(0, ge=0, le=100)
    observacoes: Optional[str] = None


class CandidatoCreate(CandidatoBase):
    pass


class CandidatoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=30)
    cargo_pretendido: Optional[str] = Field(None, min_length=1, max_length=80)
    departamento_pretendido: Optional[str] = Field(None, max_length=80)
    resumo_profissional: Optional[str] = None
    experiencia_anos: Optional[int] = Field(None, ge=0, le=60)
    formacao: Optional[str] = Field(None, max_length=160)
    habilidades: Optional[str] = None
    pretensao_salarial: Optional[float] = Field(None, ge=0)
    curriculo_url: Optional[str] = Field(None, max_length=255)
    pontuacao: Optional[int] = Field(None, ge=0, le=100)
    observacoes: Optional[str] = None


class MudarStatusRequest(BaseModel):
    novo_status: StatusSelecao


class ContratarRequest(BaseModel):
    salario: Optional[float] = Field(None, ge=0)
    data_admissao: Optional[date] = None


class CandidatoResponse(CandidatoBase):
    id: int
    status: StatusSelecao
    data_inscricao: date
    curriculo_arquivo: Optional[str] = None  # nome do PDF, se enviado
    model_config = ConfigDict(from_attributes=True)
