# Finanças Pessoais

App pessoal (Streamlit) para aprender e acompanhar mercado financeiro,
começando pelo **Boletim Focus** do Banco Central — a pesquisa semanal de
expectativas de mercado (Selic, IPCA, câmbio, PIB...) publicada toda
segunda-feira.

## O que faz hoje (v1.4)

- Busca Selic, IPCA, câmbio, PIB Total, IGP-M e dívida líquida do setor
  público direto da API pública do BACEN (Sistema de Expectativas de Mercado
  / Olinda), sem precisar de PDF nem chave de acesso.
- Verifica novas leituras automaticamente uma vez por dia útil. Na primeira
  execução, preenche até 12 semanas recentes para o gráfico já nascer útil;
  se o BACEN estiver indisponível, preserva e identifica a última coleta.
- Mantém o histórico atualizado no GitHub toda segunda-feira por uma rotina
  agendada, mesmo quando o app não é aberto.
- Resume primeiro o que mais importa: Selic, IPCA e câmbio, com comparação
  entre as duas datas disponíveis e destaque para a principal mudança.
- Permite explorar os impactos por classe de investimento e escolher qual
  série histórica visualizar; indicadores secundários, explicações e dados
  completos ficam disponíveis sob demanda.
- Mostra efeitos historicamente esperados por classe de investimento
  (pós-fixado, prefixado, IPCA+, bolsa, câmbio) — conteúdo educacional, não é
  recomendação personalizada.
- Reúne três manchetes relevantes de InfoMoney e Brazil Journal via RSS, com
  cache, deduplicação e fallback independente por fonte. O app exibe apenas
  título, fonte, horário e link para a publicação original.

## Como rodar

Desde 2026-08-04 este projeto mora dentro do hub da Fits, que é uma pasta
sincronizada pelo OneDrive. **Crie o `.venv` fora dessa árvore** — instalar
pacotes com o `.venv` dentro de uma pasta sincronizada pode travar no meio
(o OneDrive intercepta rename/hardlink que o `pip` usa para instalar cada
wheel, e a instalação quebra com `AssertionError` ou termina faltando
módulo):

```
python -m venv "%USERPROFILE%\.venvs\financas-pessoais"
%USERPROFILE%\.venvs\financas-pessoais\Scripts\activate
pip install -r requirements.txt
streamlit run app_financas.py
```

(No PowerShell, ative com
`& "$env:USERPROFILE\.venvs\financas-pessoais\Scripts\Activate.ps1"`.) O
`cd` continua sendo a pasta deste projeto — só o `.venv` em si vive fora do
OneDrive.

Depois use **Abrir panorama** na home. A atualização acontece
automaticamente; o botão **Atualizar dados** continua disponível para uma
verificação manual.

## Trabalhando de mais de uma máquina (casa + trabalho)

O `.venv` é local a cada máquina (não é versionado — recrie com os passos
acima em cada lugar). Já o histórico de dados do Focus
(`dados/focus_cache.json`) **é versionado de propósito** — é só dado público
do BACEN, sem nada sensível — para as duas máquinas acumularem o mesmo
histórico em vez de cada uma ter o seu. A rotina
`.github/workflows/atualizar-focus.yml` também atualiza esse arquivo toda
segunda-feira; por isso, faça `git pull` antes de trabalhar.

Rotina simples para não perder nada:

```
git pull                              # antes de abrir o app
streamlit run app_financas.py         # usa/atualiza o app normalmente
git add -A && git commit -m "..."     # depois de qualquer mudança (inclusive só o cache)
git push
```

O Claude Code lê `CLAUDE.md` e `CONTEXT.md` automaticamente em qualquer
máquina com o repositório clonado — é isso (não a conversa do chat) que
mantém o contexto entre casa e trabalho.

## Roadmap

- Depois: página de carteira (organizar seus investimentos) e calculadora de
  projeção de rentabilidade (juros compostos, aportes).
- Avaliado e descartado por ora: deploy público (Streamlit Community Cloud).

## Fonte oficial dos dados

BACEN — Sistema de Expectativas de Mercado (Boletim Focus):
https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata
