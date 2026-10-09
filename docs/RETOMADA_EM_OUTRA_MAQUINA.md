# Retomada em outra máquina (do zero)

Guia para abrir o projeto num PC que nunca o viu: instalar, baixar os dados, gerar as
tabelas e ver as telas. Escrito para Windows (PowerShell); no Linux/macOS troque os
caminhos do ambiente virtual. O que **não** vem do Git: dados públicos brutos, tabelas
derivadas (Parquet) e o ambiente Python. Os três se recriam com os comandos abaixo.

## 1. Pré-requisitos

- Git e Python 3.13 (`python --version`).
- Node só é preciso para o app `mobile/` (nada do módulo Ativos usa Node).
- Opcional: Claude Code e Codex CLI (ver seção 7).

## 2. Clonar

Use uma pasta curta e **fora do OneDrive** (o OneDrive trava instalações e cria
travas de arquivo):

```powershell
git clone https://github.com/raulsallesr/financas-pessoais.git C:\dev\financas-pessoais
cd C:\dev\financas-pessoais
git log --oneline -3
```

## 3. Ambiente Python (fora da pasta do projeto)

```powershell
python -m venv $env:USERPROFILE\.venvs\financas-pessoais
& $env:USERPROFILE\.venvs\financas-pessoais\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## 4. Conferir que está tudo certo (sem rede, sem dados reais)

```powershell
ruff check .
python -m pytest tests -q --cov=.
```

Esperado: ruff limpo e todos os testes passando, cobertura ≥ 85%. Os testes usam só
dados sintéticos; se algum falhar aqui, o problema é de ambiente, não de dados.

## 5. Baixar os dados públicos e gerar as tabelas

```powershell
python -m scripts.baixar_dados_ativos      # ~300 MB, alguns minutos; mostra progresso
python -m scripts.atualizar_ativos         # gera acoes.parquet e fiis.parquet
```

- Os brutos vão para `%USERPROFILE%\.cache\lastro\raw` e os derivados para
  `%USERPROFILE%\.cache\lastro\derived` (sobrescreva com `LASTRO_CACHE_DIR` e
  `LASTRO_DADOS_DIR`).
- O download é idempotente: ano encerrado não baixa de novo; o corrente renova se
  passou de um dia. `--listar` mostra o plano sem baixar.
- O resumo final do pipeline deve mostrar, em ordem de grandeza: ~244 ações (P/L ≈ 82%,
  DY ≈ 95%) e ~155 FIIs (P/VP 100%, DY ≈ 99%). Números exatos mudam com os dados do dia.
- `python -m scripts.atualizar_ativos --classe acoes` (ou `fiis`) roda só uma classe.

## 6. Abrir o app

```powershell
streamlit run app_financas.py --server.port 8551
```

Abra http://localhost:8551. Páginas (menu no topo): **Macro · FocusLens**, **Ativos B3**
(visão geral e fases), **Busca avançada** (ações), **Busca de FIIs** e **Ficha do ativo**.
Sem as tabelas derivadas, as páginas de ativos mostram o comando para gerá-las.

## 7. Trabalhar com Claude Code e Codex em casa

- **Claude Code não tem memória das conversas de outro PC.** Abra a pasta do repositório
  e peça para ler, nesta ordem: `CLAUDE.md`, `CONTEXT.md`, este guia,
  `docs/product/ROTEIRO_PROXIMAS_FASES.md` e `docs/validation/LICOES_DADOS_PUBLICOS.md`.
  O prompt pronto está no fim do `CONTEXT.md`.
- **Codex CLI** (opcional, mas é como a implementação pesada foi feita):

  ```powershell
  '' | codex exec --sandbox workspace-write --cd C:\dev\financas-pessoais "<instrução>"
  ```

  O `'' |` fecha o stdin (sem ele o comando trava). Sem `--sandbox workspace-write` ele
  pode subir somente leitura e se recusar a escrever. O sandbox dele costuma **não
  conseguir gravar em `%USERPROFILE%\.cache`**: se isso ocorrer, ele deve usar uma
  pasta temporária via `LASTRO_DADOS_DIR` e você roda o pipeline real depois, fora do
  sandbox. Nunca dê `git push` pelo Codex.
- Fluxo que funcionou: especificação em `docs/product/SPEC_*.md` → Codex implementa →
  Claude revisa (ver `CLAUDE.md`, seção "Lastro").

## 8. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `ModuleNotFoundError: pyarrow` | Instalou só `requirements.txt` sem o ambiente certo; rode `pip install -r requirements-dev.txt` |
| Página de ativos pede para rodar o pipeline | Faltam os derivados; passos 5 |
| Pipeline diz que falta arquivo bruto | Rode `scripts.baixar_dados_ativos`; anos recentes podem ainda não existir (aviso é normal) |
| `WinError 5` na limpeza de pasta temporária de teste | Ruído do Windows/OneDrive após os testes; ignore se o resultado foi "passed" |
| Instalação do pip quebra no meio | Venv dentro do OneDrive; recrie em `%USERPROFILE%\.venvs` |
| Preview pelo painel do Claude não acha servidor | O projeto não está no `launch.json` do hub; rode o `streamlit run` acima |
| Números diferentes dos documentados | Os dados públicos mudam; compare ordens de grandeza, não dígitos |

## 9. Fluxo de commit

O projeto tem git e remote próprios. Depois do gate verde (`ruff` + `pytest`), commit
escopado por caminho (nunca `git add -A` às cegas: `dados/*.json` muda sozinho pelos
workflows) e `git push` estão autorizados pelo Raul. Mensagem sem acentos problemáticos
via arquivo (`git commit -F`). Antes de começar, `git pull --ff-only`: os workflows do
GitHub commitam o cache do Macro (`Atualiza Curva Tesouro [skip ci]`).
