# Validação física — importação B3 local `v0.4.0`

## Objetivo

Validar no POCO X8 Pro que o XLSX da Área do Investidor B3 é processado no
aparelho, reduzido a uma prévia explícita e gravado somente no cofre local após
confirmação. O arquivo e seus valores não devem ser enviados pelo chat, anexados
ao repositório ou aparecer em captura de tela.

## Preparação

- para avaliar a utilidade atual, instalar o
  [APK `preview` `v0.5.2`](https://expo.dev/artifacts/eas/dvVgjSbINj4f3OdJ4CJXx_O651PcG-llvTyurlh0Ytc.apk),
  build `11`, EAS
  [`c08e5397-427f-42c2-a163-ab5cd815cb55`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/c08e5397-427f-42c2-a163-ab5cd815cb55);
- manter uma exportação XLSX original da Área do Investidor B3 apenas no
  aparelho ou em armazenamento pessoal controlado;
- não renomear PDF, CSV ou ZIP para `.xlsx`;
- se for registrar imagem, acionar **Ocultar valores** e evitar nome de arquivo
  ou ativo identificável;
- a importação substitui a carteira local inteira; use primeiro **Descartar
  prévia** para validar sem gravar.

## Matriz de evidência

| ID | Teste | Resultado esperado | Estado |
|---|---|---|---|
| BI-01 | Instalar/atualizar o `v0.4.0` | App abre e preserva as quatro abas | Aprovado |
| BI-02 | Carteira → Escolher planilha XLSX | Seletor nativo abre com feedback de leitura | Aprovado |
| BI-03 | Cancelar o seletor | Carteira e eventual prévia anterior permanecem intactas | Aprovado |
| BI-04 | Escolher exportação B3 válida | Prévia mostra posições, total, abas e exclusões; nada foi salvo | Pendente |
| BI-05 | Tocar “Ver todas” e “Recolher” | Lista expande/recolhe sem travar ou perder a prévia | Pendente |
| BI-06 | Tocar “Descartar prévia” | Prévia some e carteira anterior permanece | Pendente |
| BI-07 | Escolher novamente e confirmar substituição | Selo muda para “SÓ NO APARELHO” e posições importadas aparecem | Pendente |
| BI-08 | Fechar, ativar modo avião e reabrir | Carteira importada continua disponível sem rede | Pendente |
| BI-09 | Importar o mesmo arquivo novamente | Total e quantidade não duplicam; carteira é substituída | Pendente |
| BI-10 | Tentar arquivo não XLSX ou XLSX inválido | Mensagem explica a correção e carteira anterior permanece | Pendente |
| BI-11 | Planilha com linha ignorada/não suportada, se houver | Contagem é visível; nenhuma classe é remapeada silenciosamente | Pendente |
| BI-12 | TalkBack na área de importação | Botões, estado ocupado, prévia e expansão têm leitura coerente | Pendente |
| BI-13 | Texto ampliado e paisagem | Sem corte horizontal; ações continuam alcançáveis | Pendente |

Build: commit `c6bb875`, fingerprint
`4df3790bd18465bb8a429b23f9814aabf1ac6dc8`, status `FINISHED`, expiração em
2026-09-11. Nenhuma variável `Plain text` ou `Sensitive` foi configurada no
ambiente EAS do preview.

**Preview atual para avaliação de utilidade:** app `0.5.2`, build `11`, commit
`1c477f5d0c0da3f5980509a2f08f599016ffb1f4`, fingerprint
`4a0bc79db5a2beeb9b694f3ee8718ff13be38dff`, status `FINISHED`, expiração em
2026-09-14. Não possui variável `Plain text` ou `Sensitive`. Ainda não foi
instalado, portanto não altera os estados da matriz.

**Evidência física parcial em 2026-08-28:** no POCO X8 Pro com Android 16
(`BP2A.250605.031.A3`), o Raul confirmou que o `v0.4.0` abriu as quatro abas,
o seletor XLSX foi aberto e o cancelamento preservou a carteira. Isso aprova
BI-01 a BI-03; os demais itens continuam pendentes.

**Pausa de produto em 2026-08-28:** por decisão explícita do Raul, BI-04 a
BI-13 serão retomados somente depois da avaliação de utilidade do preview
`v0.4.4`. Os três itens aprovados permanecem como evidência histórica; nenhum
item pendente deve ser inferido como aprovado.

**Decisão posterior em 2026-08-31:** o Raul autorizou desenvolver a Etapa 5C
antes de retomar este checklist. Isso não muda nenhum estado da matriz e não
elimina este gate para o fechamento físico da Etapa 5B. O `v0.5.2/11` substitui
o `v0.4.4/8` apenas como binário recomendado para a próxima execução.

## O que relatar ao fechar o gate

Envie apenas:

- versão do Android;
- `BI-01` a `BI-13`: aprovado, falhou ou não se aplica;
- quantidade de posições somente se você se sentir confortável — é opcional;
- texto exato de eventual erro, removendo nome de arquivo, ativo e valor.

Não envie a planilha, carteira, patrimônio, CPF, conta, nome de arquivo ou
captura com valores visíveis.

## Gate de conclusão

A Etapa 5B.2 só muda para concluída quando um APK compatível com a importação
B3 estiver registrado e
BI-01 a BI-13 estiverem aprovados ou justificados. Falha de leitura, descarte,
confirmação, persistência offline ou preservação da carteira bloqueia o avanço
para produção e o fechamento da Etapa 5B.2. O desenvolvimento local da Etapa
5C foi liberado separadamente pelo Raul em 2026-08-31, sem inferir aprovação.
