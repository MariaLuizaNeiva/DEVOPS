# Versionamento semântico e Rollback

## 1. Versionamento

Cada release é identificada por uma **tag Git semântica** (`vMAJOR.MINOR.PATCH`). Ao enviar a tag, o pipeline de CD:

1. roda o CI (testes + build);
2. publica a imagem no GHCR com as tags `1.0.0`, `1.0` e `latest`;
3. cria uma **GitHub Release** com notas geradas automaticamente;
4. faz o deploy da versão em homologação e valida via `/health` e `/version`.

```bash
git checkout main && git pull
git tag v1.0.0
git push origin v1.0.0
```

| Mudança                            | Exemplo de versão |
|------------------------------------|-------------------|
| Correção de bug                    | 1.0.0 → 1.0.1     |
| Funcionalidade compatível          | 1.0.1 → 1.1.0     |
| Mudança que quebra compatibilidade | 1.1.0 → 2.0.0     |

A versão em execução pode ser conferida a qualquer momento em `GET /version`:

```json
{"storage": "postgres", "version": "1.0.0"}
```

## 2. Estratégia de rollback

Existem dois mecanismos:

**Rollback automático** (job `deploy-staging` do `cd.yml`): após o deploy da nova versão, o *smoke test* valida `/health` e confere se `/version` retorna a versão esperada. Se qualquer verificação falhar, o pipeline:

1. identifica a versão imediatamente anterior pelas tags Git;
2. refaz o deploy dessa versão e roda o smoke test nela;
3. registra o rollback no resumo da execução e marca o pipeline como **falho** (a release defeituosa precisa de correção).

**Rollback manual** (`rollback.yml`): em *Actions → Rollback manual → Run workflow*, informe a versão estável (ex.: `1.0.0`). Útil quando o problema só é percebido depois do deploy.

Como as imagens são imutáveis e versionadas, o rollback é só "subir de novo a imagem da versão anterior", sem rebuild.

> Observação: o ambiente de homologação é **simulado** com Docker Compose dentro do runner do GitHub Actions. Em um ambiente real, `scripts/deploy.sh` seria executado no servidor de destino (por exemplo via SSH) e o restante do fluxo continuaria igual.

## 3. Simulação documentada do fluxo de rollback

Passo a passo para reproduzir e **tirar os prints de evidência**:

| # | Ação | Resultado esperado | Print |
|---|------|--------------------|-------|
| 1 | Criar e enviar a tag `v1.0.0` | Pipeline verde; imagem `1.0.0` em *Packages*; Release `v1.0.0` criada; resumo "Deploy concluído" | ☐ |
| 2 | Em *Settings → Secrets and variables → Actions → Variables*, criar a variável `SIMULATE_FAILURE` = `true` | Faz o smoke test da próxima release apontar para uma rota inexistente (simula release defeituosa) | ☐ |
| 3 | Criar e enviar a tag `v1.1.0` | Deploy de `1.1.0` é feito, o smoke test **falha**, o rollback automático sobe `1.0.0` e o smoke test passa; pipeline termina marcado como falho | ☐ |
| 4 | Abrir o resumo da execução e os logs do passo "Rollback automático" | Mostra `Deploy de v1.1.0 falhou. Executando rollback para v1.0.0` e `OK: versão 1.0.0 saudável` | ☐ |
| 5 | Apagar a variável `SIMULATE_FAILURE` (ou colocar `false`) | Próximas releases voltam ao fluxo normal | ☐ |
| 6 | (Opcional) Rodar *Rollback manual* informando `1.0.0` | Smoke test confirma a versão 1.0.0 | ☐ |
