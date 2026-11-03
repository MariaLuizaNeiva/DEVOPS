# Changelog

Este projeto segue [Versionamento Semântico](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`).

## [1.0.0]
- API de tarefas (CRUD) com persistência em PostgreSQL.
- Endpoints `/health` e `/version`.
- Imagem Docker multi-stage, com usuário não-root e healthcheck.
- Pipeline de CI (testes + build) e CD (publicação no GHCR + deploy em homologação).
