import os
import uuid

from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StatusSelecao
from app.schemas import (
    FuncionarioCreate,
    FuncionarioUpdate,
    FuncionarioResponse,
    CandidatoCreate,
    CandidatoUpdate,
    CandidatoResponse,
    MudarStatusRequest,
    ContratarRequest,
)
from app.service import (
    FuncionarioService,
    CandidatoService,
    FuncionarioNaoEncontrado,
    CandidatoNaoEncontrado,
    EmailJaCadastrado,
    SelecaoInvalida,
)

# Pasta onde os PDFs enviados serão guardados
UPLOAD_DIR = os.path.join("uploads", "curriculos")
os.makedirs(UPLOAD_DIR, exist_ok=True)
TAMANHO_MAX = 5 * 1024 * 1024  # 5 MB

# ============================================================================
# Funcionários
# ============================================================================
funcionarios_router = APIRouter(prefix="/funcionarios", tags=["Funcionários"])


def get_service(db: Session = Depends(get_db)) -> FuncionarioService:
    return FuncionarioService(db)


@funcionarios_router.post("", response_model=FuncionarioResponse, status_code=status.HTTP_201_CREATED)
def criar_funcionario(dados: FuncionarioCreate, service: FuncionarioService = Depends(get_service)):
    try:
        return service.criar(dados)
    except EmailJaCadastrado as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@funcionarios_router.get("", response_model=List[FuncionarioResponse])
def listar_funcionarios(
    busca: Optional[str] = Query(None, description="Nome, e-mail, cargo ou departamento"),
    service: FuncionarioService = Depends(get_service),
):
    return service.listar(busca=busca)


@funcionarios_router.get("/{funcionario_id}", response_model=FuncionarioResponse)
def obter_funcionario(funcionario_id: int, service: FuncionarioService = Depends(get_service)):
    try:
        return service.obter(funcionario_id)
    except FuncionarioNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@funcionarios_router.put("/{funcionario_id}", response_model=FuncionarioResponse)
def atualizar_funcionario(
    funcionario_id: int, dados: FuncionarioUpdate, service: FuncionarioService = Depends(get_service)
):
    try:
        return service.atualizar(funcionario_id, dados)
    except FuncionarioNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailJaCadastrado as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@funcionarios_router.delete("/{funcionario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_funcionario(funcionario_id: int, service: FuncionarioService = Depends(get_service)):
    try:
        service.remover(funcionario_id)
    except FuncionarioNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Candidatos (seleção)
# ============================================================================
candidatos_router = APIRouter(prefix="/candidatos", tags=["Seleção / Candidatos"])


def get_candidato_service(db: Session = Depends(get_db)) -> CandidatoService:
    return CandidatoService(db)


@candidatos_router.post("", response_model=CandidatoResponse, status_code=status.HTTP_201_CREATED)
def criar_candidato(dados: CandidatoCreate, service: CandidatoService = Depends(get_candidato_service)):
    try:
        return service.criar(dados)
    except EmailJaCadastrado as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@candidatos_router.get("", response_model=List[CandidatoResponse])
def listar_candidatos(
    busca: Optional[str] = Query(None, description="Nome, e-mail ou cargo pretendido"),
    status_selecao: Optional[StatusSelecao] = Query(None, description="Fase"),
    departamento: Optional[str] = Query(None),
    cargo: Optional[str] = Query(None),
    experiencia_min: Optional[int] = Query(None, ge=0),
    pontuacao_min: Optional[int] = Query(None, ge=0, le=100),
    habilidade: Optional[str] = Query(None),
    service: CandidatoService = Depends(get_candidato_service),
):
    return service.listar(
        busca=busca,
        status=status_selecao.value if status_selecao else None,
        departamento=departamento,
        cargo=cargo,
        experiencia_min=experiencia_min,
        pontuacao_min=pontuacao_min,
        habilidade=habilidade,
    )


@candidatos_router.get("/{candidato_id}", response_model=CandidatoResponse)
def obter_candidato(candidato_id: int, service: CandidatoService = Depends(get_candidato_service)):
    try:
        return service.obter(candidato_id)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@candidatos_router.put("/{candidato_id}", response_model=CandidatoResponse)
def atualizar_candidato(
    candidato_id: int, dados: CandidatoUpdate, service: CandidatoService = Depends(get_candidato_service)
):
    try:
        return service.atualizar(candidato_id, dados)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailJaCadastrado as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@candidatos_router.patch("/{candidato_id}/status", response_model=CandidatoResponse)
def mudar_status_candidato(
    candidato_id: int, dados: MudarStatusRequest, service: CandidatoService = Depends(get_candidato_service)
):
    try:
        return service.mudar_status(candidato_id, dados.novo_status)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (SelecaoInvalida, EmailJaCadastrado) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@candidatos_router.post(
    "/{candidato_id}/contratar", response_model=FuncionarioResponse, status_code=status.HTTP_201_CREATED
)
def contratar_candidato(
    candidato_id: int,
    dados: Optional[ContratarRequest] = None,
    service: CandidatoService = Depends(get_candidato_service),
):
    try:
        return service.contratar(candidato_id, dados)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (SelecaoInvalida, EmailJaCadastrado) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ---- Upload do PDF do currículo ----
@candidatos_router.post("/{candidato_id}/curriculo", response_model=CandidatoResponse)
async def enviar_curriculo(
    candidato_id: int,
    arquivo: UploadFile = File(...),
    service: CandidatoService = Depends(get_candidato_service),
):
    nome_ok = (arquivo.filename or "").lower().endswith(".pdf")
    tipo_ok = arquivo.content_type in ("application/pdf", "application/x-pdf")
    if not (nome_ok or tipo_ok):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie um arquivo PDF.")

    try:
        service.obter(candidato_id)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAX:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O arquivo excede 5 MB.")

    nome_armazenado = f"cand_{candidato_id}_{uuid.uuid4().hex}.pdf"
    destino = os.path.join(UPLOAD_DIR, nome_armazenado)
    with open(destino, "wb") as f:
        f.write(conteudo)

    return service.anexar_curriculo(candidato_id, nome_armazenado)


# ---- Download do PDF do currículo ----
@candidatos_router.get("/{candidato_id}/curriculo")
def baixar_curriculo(candidato_id: int, service: CandidatoService = Depends(get_candidato_service)):
    try:
        candidato = service.obter(candidato_id)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if not candidato.curriculo_arquivo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Este candidato não enviou currículo em PDF.")
    caminho = os.path.join(UPLOAD_DIR, candidato.curriculo_arquivo)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado no servidor.")
    return FileResponse(caminho, media_type="application/pdf", filename=f"curriculo_{candidato_id}.pdf")


@candidatos_router.delete("/{candidato_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_candidato(candidato_id: int, service: CandidatoService = Depends(get_candidato_service)):
    try:
        service.remover(candidato_id)
    except CandidatoNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
