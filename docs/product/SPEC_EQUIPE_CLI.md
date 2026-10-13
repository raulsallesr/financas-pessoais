# Especificação — `scripts/equipe.py` e verificações do protocolo (Fases B e C)

Implementa o protocolo de `docs/coordenacao/PROTOCOLO.md` (leia primeiro, junto com
`AGENTS.md` e `docs/coordenacao/QUADRO.md`). Plano aprovado pelo Raul em 2026-10-13.
Restrições e método seguem `SPEC_BUSCA_AVANCADA_ACOES.md` (seção Restrições): sem rede nos
testes, `ruff check .` limpo, `python -m pytest tests -q --cov=.` verde com cobertura ≥ 85%,
**sem `git push`** (o Claude revisa e publica). Não altere `focuslens/`, `mobile/` nem `ativos/`.

## Visão geral

Um único arquivo `scripts/equipe.py`, **só biblioteca padrão**, Python ≥ 3.10, que roda de
qualquer pasta dentro do repositório, **antes de instalar o ambiente**. Raiz do repositório:
variável `EQUIPE_RAIZ` (para testes) ou `git rev-parse --show-toplevel` ou a pasta pai de
`scripts/`. Saída em UTF-8 (`sys.stdout.reconfigure(encoding="utf-8")`), sem emoji.

Variáveis de ambiente: `EQUIPE_AGORA` (`AAAA-MM-DDTHH:MM`, fixa o relógio nos testes),
`EQUIPE_AGENTE`, `EQUIPE_MAQUINA` (padrões de `--agente` e `--maquina`), `EQUIPE_SEM_REDE=1`
(equivale a `--sem-rede`: pula `git fetch` e a API do GitHub). Nunca imprima variáveis de ambiente
nem credenciais.

Códigos de saída: `0` ok; `1` uso ou erro; `2` item já reservado; `3` conflito de git;
`4` gate falhou. `iniciar --hook` **sempre** sai com 0 e fica em silêncio se algo falhar.

Todo subprocesso com `timeout` (git: 20 s; fetch: 15 s; API: 5 s). Falha de rede nunca derruba
o comando: avisa e segue. Meta: `iniciar` em menos de 8 s mesmo sem rede.

## Formatos (resumo; a definição completa está em `PROTOCOLO.md`)

Bloco `---` com `chave: valor` (um por linha, listas separadas por vírgula) e texto livre.
Parser próprio e tolerante, sem dependências. Ignore arquivos que começam com `_` (moldes) e
`README.md`. IDs de item como texto (`1.2`, `1.6b`, `0.1`). `QUADRO.md`: tabela com colunas
`ID | Item | Status | Dono | Atualizado | Decisão do Raul | Notas`; edite **somente a linha do
ID**, preservando o restante do arquivo byte a byte.

## Comandos

### `iniciar [--prompt] [--hook] [--sem-rede]`

1. `git fetch` (exceto `--sem-rede`), depois situação da branch (`à frente N / atrás M de origin/main`).
2. **Commits novos** em `origin/main` que a branch local não tem, contados por autor: robô
   (nome termina em `[bot]`) e demais; mostre até 3 assuntos dos que não são do robô.
3. **Árvore suja** (`git status --porcelain`), **ignorando** `dados/` e `.pytest*`: liste até 8
   caminhos. Para cada um que case com `arquivos` de uma reserva ativa, mostre o dono provável.
   Sem reserva correspondente, avise: "pode ser trabalho de outra IA; veja o diário; não sobrescreva".
4. **Reservas**: ativas e vencidas (`expira` anterior ao agora), com agente, máquina, item e idade.
5. **Diário**: as 3 últimas sessões (data, agente, título, itens).
6. **Ideias** com `status: nova` (contagem e até 5 títulos).
7. **Quadro**: itens `em andamento` e, separadamente, itens com `Decisão do Raul = sim` que não
   estão `pronto` ("aguardam o Raul").
8. **Dados**: lê `acoes_meta.json` na pasta de derivados (`LASTRO_DADOS_DIR`, senão
   `~/.cache/lastro/derived`): mostre `data_cotacao` e `gerado_em`; avise se `gerado_em` tiver
   mais de 3 dias ou se não existir (com o comando: `python -m scripts.baixar_dados_ativos` e
   `python -m scripts.atualizar_ativos`). Mostre também `atualizado_em` de
   `dados/curva_prefixada_cache.json`.
9. **CI**: `GET https://api.github.com/repos/<dono>/<repo>/actions/workflows/tests.yml/runs?branch=main&per_page=1`
   (dono e repo extraídos de `git remote get-url origin`; sem token; cabeçalho `User-Agent`).
   Mostre `conclusion` e a data; offline ou erro: "CI: indisponível".
10. Saída compacta (**máx. 40 linhas**), seções só quando houver o que mostrar, primeira linha
    `[EQUIPE] AAAA-MM-DD HH:MM — branch main @ <hash curto>`.

`--prompt`: em vez do relatório, imprime um prompt de retomada em texto corrido, pronto para
colar em qualquer IA: repositório, ordem de leitura (`AGENTS.md`, `CONTEXT.md`,
`docs/coordenacao/QUADRO.md`, `PROTOCOLO.md`), data e commit atuais, itens `em andamento` e
reservas ativas, itens que aguardam o Raul, próximo item `aberto` (primeiro por ordem do quadro),
e as três regras principais (reservar, suíte verde, fechar). Determinístico e sem dados pessoais.

`--hook`: igual a `iniciar`, mas silencioso em qualquer falha, sempre `exit 0`, e **sem** o
`git fetch` se a última busca tiver menos de 10 minutos (leia `.git/FETCH_HEAD`).

### `reservar <item> [--agente A] [--maquina M] [--arquivos a,b] [--horas 24] [--sem-push]`

`agente` e `maquina` são obrigatórios (flag ou variável de ambiente); sem eles, erro com dica.
1. `git pull --rebase --autostash` (se houver remoto e rede).
2. Se `docs/coordenacao/reservas/<item>.md` existe e **não** venceu: erro, `exit 2`, dizendo quem
   reservou e desde quando. Se venceu: substitui e avisa.
3. Cria a reserva (formato do protocolo; `expira` = agora + horas) e atualiza a linha do item no
   quadro: `Status = em andamento`, `Dono = <agente>-<maquina>`, `Atualizado = AAAA-MM-DD`. ID
   ausente no quadro: avisa e segue só com a reserva.
4. Commita **só** a reserva e o quadro (`Equipe: reserva do item X (agente/maquina)`), faz
   `pull --rebase --autostash` e `push`. Rejeição do push: refaz o rebase uma vez e tenta de novo.
   Conflito no mesmo arquivo de reserva: aborta o rebase, desfaz o commit local da reserva,
   `exit 3` com a mensagem "colisão: outra IA reservou este item".

### `fechar --resumo TEXTO --proximo TEXTO [--decisao TEXTO] [--itens 1.2,1.3] [--pronto 1.2] [--sem-gate] [--sem-push] [--forcar] [--agente A] [--maquina M]`

1. Recusa (exit 1) se houver **mudanças de código não commitadas** (fora de `docs/coordenacao/`,
   `dados/` e `.pytest*`), dizendo para commitar antes; `--forcar` ignora.
2. Gate (exceto `--sem-gate`): `ruff check .` e `python -m pytest tests -q -p no:cacheprovider
   --cov=.`; extrai "N passed" e a cobertura total (`Total coverage: 87.32%`). Gate vermelho:
   `exit 4`, não grava nada. Com `--sem-gate`, `suite: nao rodada`.
3. Grava `diario/AAAA-MM-DD_HHMM_<maquina>-<agente>.md` (formato do protocolo) com `commit` = hash
   curto do HEAD, `itens`, `suite`, `cobertura`, título derivado de `--resumo` (primeira frase,
   até 80 caracteres) e as seções preenchidas: "O que fiz" = resumo; "Decisões" = `--decisao`
   ou "Nenhuma"; "O que falta" = `--proximo`; "Perguntas ao Raul" = "Nenhuma". Mais um bloco
   "Fatos automáticos" com os arquivos alterados desde o último diário (via `git diff --name-only
   <commit do último diário>..HEAD`, fora de `dados/`).
4. Remove as reservas do próprio agente e máquina (ou dos `--itens`) com `git rm`; no quadro,
   itens em `--pronto` viram `pronto`, os demais reservados voltam a `aberto` (dono vazio).
5. Regenera `INDICE.md` (comando `indice`).
6. Commita **só** diário, quadro, índice e reservas removidas
   (`Equipe: diário da sessão <agente>-<maquina>`), `pull --rebase --autostash`, `push`. Conflito
   **somente** em `INDICE.md`: resolva sozinho (aceite qualquer lado, regenere o índice, `git add`,
   `git rebase --continue`). Qualquer outro conflito: `git rebase --abort`, `exit 3`.

### `ideia TÍTULO [--origem O] [--corpo TEXTO] [--sem-push]` e `decisao TÍTULO --decisao T --porque T [--alternativas T] [--quem Q] [--substitui ARQUIVO] [--sem-push]`

Criam o arquivo (`ideias/AAAA-MM-DD_<slug>.md` com `status: nova`; `decisoes/AAAA-MM-DD_<slug>.md`
com `status: vigente`), slug em ASCII minúsculo com hífens (até 60 caracteres; nome repetido no
mesmo dia recebe sufixo `-2`). `--substitui` troca `status: vigente` por `status: substituida` no
arquivo antigo. Commit escopado, `pull --rebase --autostash`, `push`.

### `checkpoint [--tag] [--ciclo N] [--sem-gate] [--sem-push]`

Gate (como em `fechar`). Próximo número `NNN` = maior `ckpt-NNN` existente + 1 (começa em 001).
Grava `checkpoints/ckpt-NNN.md` com `data`, `commit`, `suite`, `cobertura`, `ciclo`,
`dados_cotacao` e `dados_gerado_em` (de `acoes_meta.json`; `nao disponivel` se faltar) e um corpo com
o estado dos itens por status (contagens e lista dos `pronto`). `--tag` cria a tag anotada
`ckpt-NNN` e a empurra. Commit escopado.

### `indice`

Regenera `docs/coordenacao/INDICE.md` (primeira linha: "Gerado por `scripts/equipe.py indice`
em AAAA-MM-DD. Não edite."): reservas ativas e vencidas; as 10 últimas sessões; ideias `nova` e
`aceita`; decisões `vigente`; itens que aguardam o Raul; último checkpoint. Idempotente: sem
mudanças de conteúdo, o arquivo sai idêntico (use só a data, não a hora).

## `.claude/settings.json` (novo, versionado)

```json
{
  "hooks": {
    "SessionStart": [
      {"hooks": [{"type": "command", "command": "python scripts/equipe.py iniciar --hook"}]}
    ]
  }
}
```

Sem `permissions`. Vale para sessões abertas **na pasta do Lastro** (casa, ou trabalho quando
aberta ali). Documente em `AGENTS.md` que, se `python` não existir, use `python3` ou `py`.

## Testes (`tests/test_equipe.py`, `tests/test_coordenacao.py`)

Use `tmp_path`, repositórios git temporários e um **remoto bare** local (sem rede). Fixe o
relógio com `EQUIPE_AGORA`. Cubra, no mínimo:

- Parser de front matter e do `QUADRO.md`; edição que muda **só** a linha do ID.
- `reservar`: cria e empurra; segunda reserva do mesmo item falha com `exit 2`; reserva vencida é
  substituída; colisão de push entre dois clones vira `exit 3` e desfaz o commit local; agente
  ou máquina ausentes dão erro.
- `fechar`: gate verde grava diário com campos corretos e libera a reserva; gate vermelho dá
  `exit 4` sem gravar nada; recusa com código sujo e aceita com `--forcar`; conflito em
  `INDICE.md` entre dois clones é resolvido sozinho; conflito em outro arquivo dá `exit 3`.
- `iniciar`: relatório com commits do robô e de outros; árvore suja ignora `dados/`; reserva
  vencida aparece; **offline** (sem remoto ou `--sem-rede`) não quebra; `--hook` sempre `exit 0`;
  saída ≤ 40 linhas; `--prompt` contém data, commit e itens esperados.
- `ideia` e `decisao` (slug, sufixo, `--substitui`), `checkpoint` (numeração, `--tag`), `indice`
  (idempotência).
- **Validadores sobre o repositório real** (`tests/test_coordenacao.py`): todo arquivo de
  `docs/coordenacao/` tem os campos obrigatórios; nomes do diário no padrão
  `AAAA-MM-DD_HHMM_<maquina>-<agente>.md`; nenhuma reserva com `expira` anterior a `desde` nem
  duas reservas do mesmo item; `QUADRO.md` com IDs únicos e status válidos; `.claude/settings.json`
  é JSON válido e o hook chama `scripts/equipe.py iniciar --hook`.
- **Varredura de segredos** em `docs/coordenacao/**`, `AGENTS.md`, `CLAUDE.md` e
  `scripts/equipe.py`: padrões `ghp_[A-Za-z0-9]{20,}`, `github_pat_[A-Za-z0-9_]{20,}`,
  `AKIA[0-9A-Z]{16}`, `-----BEGIN [A-Z ]*PRIVATE KEY-----`, `sk-[A-Za-z0-9]{20,}`,
  `xox[baprs]-[A-Za-z0-9-]{10,}` e e-mails reais (permitidos: `noreply@anthropic.com` e
  `*@users.noreply.github.com`). Inclua um teste que **planta** um segredo falso num arquivo
  temporário e confirma que o scanner acusa.

## Workflows e documentos (Fase C)

- `.github/workflows/atualizar-curva.yml` e `atualizar-focus.yml`: antes do `git push` do robô,
  `git pull --rebase --autostash origin main` com até 3 tentativas (espera curta entre elas);
  mantenha `[skip ci]`, `contents: write` e o restante. Não renomeie nada. Teste de texto em
  `tests/test_coordenacao.py` confirmando `pull --rebase` nos dois.
- `CONTRIBUTING.md`: realinhar ao fluxo real (commit direto na `main` com disciplina, protocolo em
  `AGENTS.md` e `docs/coordenacao/PROTOCOLO.md`, gate); remova o fluxo de PR de colaborador externo.
- `README.md`: seção curta "Como as IAs trabalham aqui" com link para o protocolo (também serve de
  portfólio).
- `docs/RETOMADA_EM_OUTRA_MAQUINA.md`: acrescente o passo `python scripts/equipe.py iniciar` e
  `--prompt` na seção de IAs.

## Fora de escopo

Dados de mercado e workflow `atualizar-ativos` (Fase D), simulação de duas máquinas (Fase E),
ponte com o hub, Issues, Project, PR obrigatório.

## Ao terminar

Rode o gate completo, rode `python scripts/equipe.py iniciar --sem-rede` e `python
scripts/equipe.py indice` no repositório real e cole a saída do `iniciar` no resumo. **Não crie
reservas nem diário no repositório real** (todo teste de escrita vai em pastas temporárias),
**não faça push**. Devolva: o que foi feito, decisões fora desta spec e qualquer ponto em que o
protocolo precisou de ajuste.
