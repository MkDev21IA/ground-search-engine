# Search proxy

Camada de normalização entre "uma query de pesquisa" e os motores de busca
candidatos (hoje só **SearXNG** — Brave, Tavily e Exa foram excluídas por
privacidade; ver
[decisions/0006](../decisions/0006-metodologia-e-infraestrutura-de-avaliacao-de-busca.md)
e [decisions/0005](../decisions/0005-verificacao-e-citacao-de-fontes.md)).

## Por quê

Cada motor tem sua própria API, formato de request/response e comportamento
default (nº de resultados, idioma, filtros). Comparar os motores testando cada um
"do seu jeito" contamina a avaliação — não dá pra saber se uma diferença de
resultado é do motor em si ou de como a query foi formatada/parametrizada para
aquele motor especificamente. O proxy existe para eliminar essa variável: toda
query passa pelo **mesmo formato de entrada**, e cada motor é só um adaptador que
traduz esse formato pro dele e traduz a resposta de volta pro **mesmo formato de
saída**. Isso garante uma avaliação comparável (ver
[decisions/0006](../decisions/0006-metodologia-e-infraestrutura-de-avaliacao-de-busca.md)).

Este componente nasce para viabilizar a avaliação (rodar a versão de prompts ativa
em [`../prompts/`](../prompts/) contra cada motor e salvar em
[`../results/`](../results/)), mas a intenção é que ele vire a peça real de busca do
pipeline de RAG do produto depois — não é código descartável. Ao rodar uma
avaliação, registrar em `results/` qual versão de `prompts_vN.yaml` foi usada (ver
convenção em [`../prompts/README.md`](../prompts/README.md)) — o `--prompts` do CLI
já aponta pro arquivo específico usado, então basta copiar esse caminho pro
`notas.md` da rodada.

## Contrato

Entrada (canônica, independente de motor) — `search_proxy.models.Query`:

```
text: str
lang: str = "pt"
max_results: int = 10
```

Saída (canônica, uma lista por resultado) — `search_proxy.models.Result`:

```
engine: str          # qual motor gerou este resultado
url: str
title: str
snippet: str
rank: int            # posição no ranking retornado pelo motor (0 se error)
fetched_at: str      # timestamp UTC da chamada
error: str | None    # preenchido em vez de levantar exceção quando a chamada falha
```

Cada motor é um adaptador (`search_proxy.base.SearchAdapter`) que implementa
"canônico → request do motor" e "response do motor → canônico".

## Como rodar

```bash
cd search-proxy
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
cp .env.example .env   # preencher SEARXNG_BASE_URL

# testes (HTTP mockado, não bate em API real)
.venv/bin/python -m pytest -q

# rodar de verdade contra um motor
.venv/bin/python -m search_proxy.cli \
  --engine searxng \
  --prompts ../prompts/prompts_v1.yaml \
  --out ../results/AAAA-MM-DD-descricao
```

### SearXNG local (adapter `searxng`)

Requer uma instância rodando com o formato JSON habilitado (vem desligado por
padrão). Exemplo mínimo de `docker-compose.yml`:

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    ports:
      - "8080:8080"
    volumes:
      - ./searxng-config:/etc/searxng
```

Depois de subir uma vez, editar `searxng-config/settings.yml` e garantir:

```yaml
search:
  formats:
    - html
    - json
```

e reiniciar o container.

## Stack

Python — SDKs/HTTP clients de todos os motores candidatos têm binding Python, e a
API do LM Studio (usada para os modelos locais, ver
[decisions/0003](../decisions/0003-arquitetura-do-modelo-llm.md)) é compatível com o
formato OpenAI, fácil de consumir do mesmo processo. Decisão registrada em
[decisions/0006](../decisions/0006-metodologia-e-infraestrutura-de-avaliacao-de-busca.md).

## Status

Implementado: modelos canônicos, `SearchAdapter` base, adapter `searxng`, runner +
CLI, testes (HTTP mockado). Adapter `brave` foi removido em 2026-09-04 (sem tier
grátis desde fev/2026 + cada query fica ligada a uma conta com cartão — ver
decisions/0006, seção "Revisão"); recuperável do histórico do git se a decisão for
revisitada. Tavily e Exa foram excluídas pelo mesmo motivo (conta + API key
ligando cada busca e o conteúdo extraído a uma identidade nossa), sem nunca terem
sido implementadas. Falta: formalizar a rubrica de avaliação sobre os resultados
salvos em `results/`.
