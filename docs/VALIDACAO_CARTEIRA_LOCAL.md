# Validação — carteira local segura `v0.3.0`

**Status em 2026-08-28:** implementação, gates locais e preview EAS aprovados.
Build [`67b97c57-ce20-4cb6-8c21-570c4742762e`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/67b97c57-ce20-4cb6-8c21-570c4742762e),
commit `9308f02`, fingerprint
`a28c993ae571b5d58d7eea95f8fe6fc877c71023`. O ciclo foi executado no preview
`v0.4.0`: CL-02 a CL-10 estão aprovados no POCO X8 Pro; acessibilidade em
CL-11 a CL-13 continua pendente.

O [APK preview `v0.3.0`](https://expo.dev/artifacts/eas/ym42IqE6aIjdXG81aqx0ZotUZ0R3v6f2Twp5W_UNuwM.apk)
expira em 2026-09-11. Ele é distribuição interna e não publica em loja.

O ciclo físico atual deve preferir o
[APK `v0.4.0`](https://expo.dev/artifacts/eas/25BWk8wQe0mppgR7jumlP4VdI99WJctpNg_Nwjf5Cec.apk),
que inclui integralmente o cofre `v0.3.0`, usa build `4` e acrescenta a
importação B3. Assim CL-02 a CL-13 e BI-01 a BI-13 podem ser validados na mesma
instalação, sem manter dois APKs concorrentes.

Depois de CL-02 a CL-10 passarem, o Raul pausou CL-11 a CL-13 para avaliar
primeiro a utilidade do corte `v0.4.2`. A evidência aprovada abaixo permanece
válida; a pausa não fecha acessibilidade.

Este documento é a evidência operacional da seção 15 de
`PLANO_FOCUSLENS.md`. Não registrar aqui nome de ativo real, valor, conta,
instituição, print da carteira pessoal ou qualquer outro dado financeiro.

## 1. Fronteira que está sendo validada

- snapshot público `v1`: somente mercado, fontes, evidências e efeitos por
  classe;
- carteira privada `v1`: posições e valores somente no aparelho;
- chave AES-256: `expo-secure-store`;
- documento cifrado: AES-GCM autenticado em `Paths.document`;
- composição entre mercado e carteira: somente em memória;
- rede, backend, autenticação, telemetria e Open Finance: ausentes.

O renderer web permanece em demonstração e não é evidência do cofre nativo.
Como o corte adiciona módulos nativos, o preview anterior não valida esta etapa.

## 2. Dados seguros para o teste

Use exclusivamente posições fictícias, por exemplo:

| Campo | Valor sintético sugerido |
|---|---|
| Nome | Ativo Teste A |
| Classe | Renda fixa pós-fixada |
| Valor | R$ 1.250,50 |
| Segunda posição | Ativo Teste B · Bolsa brasileira · R$ 750,00 |

Esses valores existem somente como roteiro e não devem ser tratados como
carteira, recomendação ou evidência financeira.

## 3. Checklist no aparelho

| ID | Verificação | Estado | Evidência técnica esperada |
|---|---|---|---|
| CL-01 | Preview `v0.3.0` gerado | Aprovado | EAS `67b97c57-ce20-4cb6-8c21-570c4742762e`, `FINISHED`, commit `9308f02` |
| CL-02 | APK instalado | Aprovado | `v0.4.0` abriu sem Metro no POCO X8 Pro e mostrou o seletor XLSX da nova Carteira |
| CL-03 | Demo não vira carteira automaticamente | Aprovado | selo `DEMONSTRAÇÃO` confirmado antes do primeiro salvamento |
| CL-04 | Primeira posição cria o cofre | Aprovado | selo `SÓ NO APARELHO` e apenas a posição fictícia informada |
| CL-05 | Persistência offline | Aprovado | fechar, ativar modo avião e reabrir preservou a posição |
| CL-06 | Composição em memória | Aprovado | Hoje/Cenários refletiram a carteira local |
| CL-07 | Edição | Aprovado | alteração permaneceu após encerrar e reabrir o app |
| CL-08 | Ocultação | Aprovado | Ocultar mascarou os valores e Mostrar os restaurou |
| CL-09 | Exclusão | Aprovado | confirmação removeu somente a posição escolhida |
| CL-10 | Reset do cofre | Aprovado | confirmação apagou a carteira local e retornou à demo |
| CL-11 | TalkBack no editor | Pendente | labels, radios, erros e ações lidos em ordem lógica |
| CL-12 | Texto ampliado | Pendente | formulário e ações continuam alcançáveis por scroll |
| CL-13 | Alvos de toque | Pendente | criar, classes, salvar, editar, excluir e reset sem precisão fina |

## 4. Sequência mínima de execução

1. instalar o novo preview por cima do anterior;
2. abrir Carteira e confirmar `DEMONSTRAÇÃO`;
3. criar `Ativo Teste A` com `R$ 1.250,50`;
4. fechar o app, ativar modo avião e reabrir;
5. conferir o selo `SÓ NO APARELHO` e navegar por Hoje/Cenários;
6. editar o valor para `R$ 1.500,00` e reabrir novamente;
7. adicionar e depois excluir `Ativo Teste B`;
8. testar Ocultar/Mostrar;
9. acionar “Apagar carteira local”, confirmar e verificar o retorno à demo;
10. repetir o editor com TalkBack e texto do sistema ampliado.

## 5. Gates automatizados do corte

- TypeScript: aprovado;
- domínio móvel: 20/20 testes;
- contrato privado: schema, campos, classes, duplicidade, limite e UTF-8;
- configuração nativa: dependências e plugin do SecureStore validados;
- Expo Doctor: `21/21`;
- export web: aprovado, sem persistência privada;
- Android/Hermes: aprovado com 633 módulos;
- Python: 191 testes e `pip check` aprovados;
- npm: zero vulnerabilidade alta/crítica; 11 moderadas transitivas do toolchain,
  sem `audit fix --force` incompatível.

Os testes automatizados não simulam Android Keystore, Keychain ou filesystem
nativo. CL-04, CL-05, CL-07, CL-09 e CL-10 são o gate físico do armazenamento.

**Evidência física parcial em 2026-08-28:** no preview `v0.4.0`, o Raul
confirmou o selo `DEMONSTRAÇÃO` antes da primeira gravação, criou o cofre com a
posição sintética do roteiro, reabriu o app em modo avião com a posição
preservada e confirmou a composição da carteira local em Hoje/Cenários. Isso
aprova CL-03 a CL-06. Na continuação, confirmou persistência após edição,
ocultação e exibição dos valores, exclusão isolada da segunda posição sintética
e reset explícito com retorno à demo. Isso aprova CL-07 a CL-10.

## 6. Critério de conclusão

A Etapa 5B.1 só muda para concluída quando:

- o novo preview estiver `FINISHED` e instalado;
- CL-03 a CL-10 passarem com dados sintéticos;
- não houver posição ou valor no snapshot público, log ou evidência versionada;
- falhas encontradas forem registradas sem expor os dados usados no aparelho;
- `CONTEXT.md` registrar o resultado, ainda que o APK `v0.4.0` substitua o
  `v0.3.0` no ciclo físico e valide cofre + importação em conjunto.
