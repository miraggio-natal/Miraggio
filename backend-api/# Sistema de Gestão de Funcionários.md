# Sistema de Gestão de Funcionários

Monorepo para uma plataforma de cadastro e gestão de colaboradores, com **portal público** (autocadastro via QR Code/link) e **painel administrativo** (RH/gestão), API REST e banco PostgreSQL.

---

## ⚠️ Sobre o escopo desta entrega

O documento original descreve um **sistema de porte empresarial** (duas interfaces, autenticação com 2FA, RBAC, upload de documentos, assinatura eletrônica, dashboard, relatórios, auditoria, i18n, PWA, Docker/NGINX...). Isso é, realisticamente, **semanas de trabalho** e não cabe, 100% funcional, em uma única entrega. Por isso o projeto avança **por fases**, entregando peças reais e utilizáveis a cada passo.

Já entregue e utilizável:

- ✅ **Modelo de dados completo e normalizado** (`database/schema.sql`) — Fase 0
- ✅ **Infraestrutura de desenvolvimento** (`docker/`) — Fase 0
- ✅ **Painel administrativo navegável** (`frontend-admin/index.html`) — Fase 5, protótipo com dados simulados
- ✅ **Portal público de cadastro navegável** (`frontend-publico/index.html`) — Fase 4, protótipo
- ✅ **Base do backend** (`backend-api/`) — Fase 1: auth JWT + 2FA, RBAC, auditoria, dashboard e busca de funcionários (código real, sintaxe validada, ainda não compilado)
- ✅ **Plano de construção por fases** (`docs/ROADMAP.md`)

Os dois protótipos de interface rodam sobre **dados simulados**; a base do backend liga tudo a dados reais. O que falta (CRUD completo de todos os módulos, storage de arquivos/S3, relatórios PDF/Excel/Word, i18n/PWA, testes e endurecimento de produção) segue no roadmap, fase a fase.

---

## Stack

| Camada     | Tecnologias |
|------------|-------------|
| Frontend   | HTML5, CSS3, JavaScript (ES2025), Bootstrap 5 / Tailwind, PWA, tema claro/escuro |
| Backend    | Node.js, Express, TypeScript, Prisma ORM, JWT, Multer |
| Banco      | PostgreSQL, Redis (cache/filas) |
| Infra      | Docker, NGINX |
| Princípios | Clean Architecture, SOLID, RBAC, LGPD |

---

## Estrutura do monorepo

```
employee-system/
├─ frontend-publico/     # Portal do colaborador (QR/link)          — ✅ protótipo (Fase 4)
├─ frontend-admin/       # Painel RH/gestão                          — ✅ protótipo (Fase 5)
├─ backend-api/          # API REST (Node + Express + TS + Prisma)   — ✅ base (Fase 1)
│  └─ prisma/            # schema.prisma (base) + migrations
├─ database/             # schema.sql (PostgreSQL)                   — ✅ ENTREGUE
├─ docker/               # docker-compose + .env.example             — ✅ ENTREGUE
├─ docs/                 # ROADMAP, arquitetura, LGPD                — ✅ ENTREGUE
├─ scripts/              # utilitários (seed, backup)                — a implementar
└─ tests/                # testes automatizados                      — a implementar
```

---

## O que está incluído nesta entrega

- **`database/schema.sql`** — ~25 tabelas normalizadas cobrindo dados pessoais, contatos, endereços, dados bancários, profissionais e médicos, dependentes, escolaridade, histórico, currículo, documentos, benefícios, uniformes, treinamentos, usuários/RBAC, assinaturas e auditoria. Inclui **enums, índices** (com busca por nome via trigramas), **views** (controle de vencimentos e dashboard), **triggers** (`updated_at` e auditoria automática), **função** parametrizada e **seeds**.
- **`docker/docker-compose.yml` + `.env.example`** — PostgreSQL + Redis prontos; o `schema.sql` é carregado automaticamente na primeira subida.
- **`backend-api/prisma/schema.prisma`** — datasource/generator + modelos de exemplo e o fluxo recomendado para gerar o schema completo.
- **`docs/ROADMAP.md`** — plano por fases e checklist de segurança/LGPD.

---

## Como executar o banco (ambiente de dev)

**Opção A — Docker (recomendada):**
```bash
cd docker
cp .env.example .env      # ajuste as senhas
docker compose up -d      # sobe Postgres + Redis; o schema é criado sozinho
```

**Opção B — psql (banco já existente):**
```bash
psql "postgresql://usuario:senha@localhost:5432/rh" -f database/schema.sql
```

**Login master de desenvolvimento:** `admin@empresa.local` / `Trocar@123`
> Altere a senha imediatamente em qualquer ambiente real.

---

## Fluxo com Prisma

O `schema.sql` é a **fonte canônica** do modelo. No backend em Prisma, o caminho mais seguro é:

```bash
cd backend-api
npx prisma db pull      # introspecta o banco e gera o schema.prisma completo
npx prisma generate     # gera o client tipado
```

Assim o schema Prisma reflete exatamente o banco (sem risco de divergência). Objetos avançados (views, triggers, funções) permanecem no SQL — o Prisma os acessa via `Unsupported`/queries. O `schema.prisma` versionado aqui serve como base/exemplo de convenções.

---

## Próximos passos

Ver **`docs/ROADMAP.md`** para o plano completo. Em resumo: backend base (auth + 2FA + RBAC) → módulo de funcionários → documentos/assinatura → portal público → painel admin/dashboard → relatórios → extras → testes/produção.
