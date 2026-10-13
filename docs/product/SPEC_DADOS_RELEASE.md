# Especificação — dados de mercado iguais nas duas máquinas (item 0.2 / 1.4)

Hoje os Parquet do módulo Ativos só existem na máquina que rodou o pipeline (baixar ~300 MB e
processar). Esta spec faz um workflow do GitHub gerá-los todo dia útil e publicá-los como
**assets de uma release fixa**, e cria um comando que os baixa em segundos (cerca de 150 KB).
Contexto: [`PROTOCOLO.md`](../coordenacao/PROTOCOLO.md), [`SPEC_BUSCA_AVANCADA_ACOES.md`](SPEC_BUSCA_AVANCADA_ACOES.md)
(restrições: sem rede nos testes, `ruff` limpo, **o comando do CI** `pytest tests/ -q --cov=.` verde
com cobertura ≥ 85%, sem `git push`, não alterar `focuslens/` nem `mobile/`).

## Decisões de desenho

- **Release fixa `dados-ativos`**, marcada como pré-lançamento e **sem ser a "latest"** (para
  não esconder a `v0.6.4-beta`). Os assets são sobrescritos a cada rodada (`--clobber`). Nunca
  commitar Parquet no histórico do git.
- **Assets:** `acoes.parquet`, `acoes_meta.json`, `fiis.parquet`, `fiis_meta.json`. Dados públicos
  (CVM e B3); nenhum dado pessoal.
- **Permissão mínima** do workflow: `contents: write`, com o `GITHUB_TOKEN` padrão. Sem segredos.
- **Repositório público:** o download no cliente usa a API pública, sem token.

## 1. `.github/workflows/atualizar-ativos.yml`

- **Gatilhos:** `schedule` em dias úteis às **22:00 UTC** (19:00 em Brasília, depois do fechamento
  da B3); `workflow_dispatch`; e `push` **somente** com `paths: [".github/workflows/atualizar-ativos.yml"]`
  (permite validar o workflow no próprio commit que o cria; um comentário no YAML explica isso e
  que o gatilho pode sair depois).
- **`concurrency`:** grupo `atualizar-ativos`, sem cancelar execução em andamento.
- **Passos:** checkout; `actions/setup-python@v5` (3.13, `cache: pip`, `cache-dependency-path:
  requirements.txt`); `pip install -r requirements.txt` (sem as dependências de desenvolvimento);
  `actions/cache@v4` do cache bruto (`~/.cache/lastro/raw`) com chave `lastro-raw-v1-${{ github.run_id }}`
  e `restore-keys: lastro-raw-v1-` (cada rodada restaura o mais recente e salva um novo);
  `python -m scripts.baixar_dados_ativos`; `python -m scripts.atualizar_ativos`;
  publicação com `gh` (já instalado no runner), `GH_TOKEN: ${{ github.token }}`:
  1. criar a release se não existir: `gh release create dados-ativos --prerelease --latest=false
     --title "Dados do Lastro (atualização diária)" --notes "..."`;
  2. `gh release upload dados-ativos <4 arquivos da pasta de derivados> --clobber`;
  3. `gh release edit dados-ativos --notes "<data da cotação, gerado em, contagens>"` com os valores
     lidos de `acoes_meta.json` e `fiis_meta.json`.
  Variáveis de ambiente do job: `LASTRO_CACHE_DIR` e `LASTRO_DADOS_DIR` apontando para pastas dentro de
  `${{ runner.temp }}` (determinístico e sem depender de `$HOME`).
- **Falha explícita:** se o pipeline não gerar os 4 arquivos, o job falha **antes** de tocar na release
  (nunca sobrescrever dados bons por vazio). Se `acoes.parquet` tiver menos de 100 linhas ou
  `fiis.parquet` menos de 50, falha com mensagem (guarda de sanidade; use `python -c` ou um script).
- **Risco conhecido a provar rodando:** as fontes (CVM e B3) precisam responder aos IPs do GitHub. Se a
  B3 bloquear, o job falha no download com mensagem clara (não esconda o erro).

## 2. `scripts/sincronizar_dados.py`

Só biblioteca padrão para o download (a validação do Parquet pode usar `pandas`/`pyarrow`, que já são
dependências). Uso: `python -m scripts.sincronizar_dados [--repo dono/nome] [--forcar] [--sem-rede]`.

1. Repositório: `--repo`, senão extraído de `git remote get-url origin`, senão
   `raulsallesr/financas-pessoais`.
2. `GET https://api.github.com/repos/<repo>/releases/tags/dados-ativos` (sem token, `User-Agent`);
   lista os assets. Release ausente (404): mensagem clara e `exit 1`.
3. Lê o `gerado_em` do `acoes_meta.json` da release (baixe o meta primeiro) e o compara com o local
   (pasta de derivados: `LASTRO_DADOS_DIR` ou `~/.cache/lastro/derived`). Sem `--forcar`, não baixa se o
   local já for **igual ou mais novo**; diz isso e sai com 0.
4. Baixa os 4 assets para uma pasta temporária ao lado do destino, **valida** (Parquet legível com as
   colunas mínimas `ticker` e `preco`; JSON com `schema_version` e `data_cotacao`; esquema suportado:
   o mesmo número que o pipeline atual grava) e só então substitui os arquivos de forma atômica. Falha
   de qualquer validação: não altera nada local, `exit 1`.
5. Imprime um resumo (data da cotação, gerado em, linhas por classe). Timeout de rede 30 s por arquivo.
   Nunca imprime variáveis de ambiente.

## 3. Integração com o resto

- Telas de ativos (mensagem de "sem derivados"): o comando principal passa a ser
  `python -m scripts.sincronizar_dados` (rápido), com o par `baixar_dados_ativos` + `atualizar_ativos`
  como alternativa.
- `scripts/equipe.py iniciar`: a mensagem de dados ausentes ou defasados sugere primeiro
  `python -m scripts.sincronizar_dados`.
- `docs/RETOMADA_EM_OUTRA_MAQUINA.md` e `README.md`: o caminho rápido do passo 5 vira o sincronizar
  (segundos); o caminho completo (300 MB) continua como alternativa.
- `docs/coordenacao/QUADRO.md`: **não edite** (o integrador atualiza).

## 4. Testes

Cliente HTTP injetável (como em `scripts/baixar_dados_ativos.py`), sem rede:
- Sincronizar baixa os 4 assets para pasta temporária, valida e substitui; segunda execução com local
  igual não baixa; `--forcar` baixa de novo.
- Release 404, asset ausente, Parquet corrompido, JSON sem `schema_version` e esquema não suportado:
  nenhuma alteração local e `exit 1`; o arquivo bom anterior permanece intacto.
- Comparação de `gerado_em` (local mais novo, igual, mais velho, local ausente).
- Teste de texto sobre o workflow em `tests/test_coordenacao.py` (ou arquivo novo): contém `schedule`,
  `contents: write`, `--clobber`, `--prerelease`, `--latest=false`, `actions/cache@v4` e a guarda de
  sanidade; **não** contém `secrets.` nem `pull_request_target`.
- Mensagens das telas e do `equipe iniciar` citam `scripts.sincronizar_dados`.

## Fora de escopo

Download automático de dentro do app, token ou autenticação, Parquet de histórico, mobile, hospedagem.

## Ao terminar

Gate com o comando exato do CI (`ruff check .` e `pytest tests/ -q --cov=.`), `CONTEXT.md` não precisa
mudar (o Claude atualiza), **sem `git push`**. Devolva: o que foi feito, decisões fora desta spec e a
saída de `python -m scripts.sincronizar_dados --sem-rede` (deve falhar de forma limpa e clara).
