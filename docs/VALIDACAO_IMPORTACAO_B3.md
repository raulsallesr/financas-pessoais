# Validação física — importação B3 local `v0.4.0`

## Objetivo

Validar no POCO X8 Pro que o XLSX da Área do Investidor B3 é processado no
aparelho, reduzido a uma prévia explícita e gravado somente no cofre local após
confirmação. O arquivo e seus valores não devem ser enviados pelo chat, anexados
ao repositório ou aparecer em captura de tela.

## Preparação

- instalar o APK `preview` `v0.4.0` quando o link estiver registrado aqui;
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
| BI-01 | Instalar/atualizar o `v0.4.0` | App abre e preserva as quatro abas | Pendente |
| BI-02 | Carteira → Escolher planilha XLSX | Seletor nativo abre com feedback de leitura | Pendente |
| BI-03 | Cancelar o seletor | Carteira e eventual prévia anterior permanecem intactas | Pendente |
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

## O que relatar ao fechar o gate

Envie apenas:

- versão do Android;
- `BI-01` a `BI-13`: aprovado, falhou ou não se aplica;
- quantidade de posições somente se você se sentir confortável — é opcional;
- texto exato de eventual erro, removendo nome de arquivo, ativo e valor.

Não envie a planilha, carteira, patrimônio, CPF, conta, nome de arquivo ou
captura com valores visíveis.

## Gate de conclusão

A Etapa 5B.2 só muda para concluída quando o APK `v0.4.0` estiver registrado e
BI-01 a BI-13 estiverem aprovados ou justificados. Falha de leitura, descarte,
confirmação, persistência offline ou preservação da carteira bloqueia o avanço
para a Etapa 5C.
