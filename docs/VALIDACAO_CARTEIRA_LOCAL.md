# Validação — carteira local segura `v0.3.0`

**Status em 2026-08-28:** implementação, gates locais e preview EAS aprovados.
Build [`67b97c57-ce20-4cb6-8c21-570c4742762e`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/67b97c57-ce20-4cb6-8c21-570c4742762e),
commit `9308f02`, fingerprint
`a28c993ae571b5d58d7eea95f8fe6fc877c71023`. Instalação e ciclo completo no
POCO X8 Pro ainda pendentes.

O [APK preview `v0.3.0`](https://expo.dev/artifacts/eas/ym42IqE6aIjdXG81aqx0ZotUZ0R3v6f2Twp5W_UNuwM.apk)
expira em 2026-09-11. Ele é distribuição interna e não publica em loja.

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
| CL-02 | APK instalado | Pendente | app abre sem Metro e mostra versão nova da Carteira |
| CL-03 | Demo não vira carteira automaticamente | Pendente | selo `DEMONSTRAÇÃO` antes do primeiro salvamento |
| CL-04 | Primeira posição cria o cofre | Pendente | selo `SÓ NO APARELHO` e apenas a posição fictícia informada |
| CL-05 | Persistência offline | Pendente | fechar, ativar modo avião e reabrir preserva a posição |
| CL-06 | Composição em memória | Pendente | Hoje/Cenários refletem somente classes da carteira local |
| CL-07 | Edição | Pendente | nome, classe ou valor alterado permanece após reabrir |
| CL-08 | Ocultação | Pendente | botão Ocultar mascara os valores da Carteira |
| CL-09 | Exclusão | Pendente | confirmação remove somente a posição escolhida |
| CL-10 | Reset do cofre | Pendente | confirmação apaga chave/documento e retorna à demo |
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

## 6. Critério de conclusão

A Etapa 5B.1 só muda para concluída quando:

- o novo preview estiver `FINISHED` e instalado;
- CL-03 a CL-10 passarem com dados sintéticos;
- não houver posição ou valor no snapshot público, log ou evidência versionada;
- falhas encontradas forem registradas sem expor os dados usados no aparelho;
- `CONTEXT.md` registrar o resultado, ainda que o APK `v0.4.0` substitua o
  `v0.3.0` no ciclo físico e valide cofre + importação em conjunto.
