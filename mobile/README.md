# FocusLens Mobile

Primeiro corte móvel do FocusLens BR em React Native, Expo e TypeScript. A
experiência responde a uma pergunta simples: **o que o mercado está dizendo e
onde isso encosta na minha carteira?**

![FocusLens Mobile v0.1](../docs/assets/focuslens-mobile-v0.1.png)

## O que já funciona

- **Hoje:** quatro sinais tocáveis com valor, movimento, data e fonte;
- **impacto personalizado:** cada sinal revela somente as posições e classes
  relacionadas na carteira de demonstração;
- **Carteira:** exposição, peso por posição e controle para ocultar valores;
- **Cenários:** choque ilustrativo de −100 a +100 bps com mudança imediata da
  leitura por posição;
- **Entenda:** fluxo Sinal → Evidência → Exposição → Limite;
- navegação inferior persistente, alvos de toque de pelo menos 44 px, tema
  claro e nenhuma informação transmitida somente por cor.

Este corte usa dados e valores **sintéticos**. Ele não conecta conta, corretora
ou Open Finance, não persiste carteira real e não produz recomendação.

## Como visualizar agora

Pré-requisito: Node.js LTS.

```powershell
cd mobile
npm ci
npm run web
```

Esse comando abre a mesma árvore de componentes React Native no renderer web e
é o caminho imediato para revisar a experiência. O produto continua sendo
React Native; o renderer web é somente uma bancada de desenvolvimento.

### Atalho validado nesta máquina

No computador de trabalho, o Node portátil e as dependências externas ao
OneDrive já estão preparados. Abra um PowerShell novo e cole:

```powershell
$nodeRoot = "$env:LOCALAPPDATA\focuslens-tools\node-v24.20.0-win-x64"
$env:Path = "$nodeRoot;$env:Path"
$mobileRoot = Join-Path $env:USERPROFILE "OneDrive - FitBank Pagamentos Eletrônicos\Documentos\AI-Handoff-Hub-Starter\01_Projetos\Financas-Pessoais\mobile"
Set-Location -LiteralPath $mobileRoot
npm run web
```

Se o navegador não abrir sozinho, use o endereço exibido pelo Expo no terminal,
normalmente `http://localhost:8081`. `Ctrl+C` encerra o servidor. Essas linhas
precisam ser executadas na mesma janela do PowerShell para que o `npm` portátil
permaneça no `PATH`.

Nesta máquina, `mobile/node_modules` é uma junção local ignorada pelo Git para
`%LOCALAPPDATA%\focuslens-mobile\runtime\node_modules`. Não remover ou
versionar essa junção. Em outra máquina, prefira um clone curto, como
`C:\dev\financas-pessoais`, e então rode `npm ci` dentro de `mobile/`.

## Como rodar em um aparelho

Este corte usa Expo SDK 57. Para um projeto de produto, o caminho recomendado é
um **development build** próprio, não depender do aplicativo genérico Expo Go.
Depois que esse build estiver instalado no Android/iOS, inicie o Metro com:

```powershell
npm start
```

O empacotamento instalável e a assinatura do development build são o próximo
incremento de distribuição. O gate atual já gera o bundle Android, mas ainda
não publica APK, AAB ou build iOS. O incremento de produto imediatamente
priorizado antes dele é o snapshot vivo Python → mobile.

Se o checkout estiver dentro de OneDrive e a instalação encontrar limites de
caminho, prefira um clone local curto para o desenvolvimento móvel. Nesta
máquina, as dependências foram mantidas fora do OneDrive e ligadas por um
`node_modules` local ignorado pelo Git.

## Gates

```powershell
npm run typecheck
npm run test:domain
npm run export:android
```

O gate atual cobre contrato demo, cálculo de peso, filtro por classe, impacto
por sinal, limites do cenário e linguagem não imperativa. O bundle Android é
gerado pelo Metro sem depender do Streamlit.

## Estrutura

```text
App.tsx                 estado e navegação principal
src/components/         componentes móveis reutilizáveis
src/data/               fotografia sintética versionada
src/domain/             contrato, filtros e sensibilidade educacional
src/screens/            Hoje, Carteira, Cenários e Entenda
assets/                 marca determinística em SVG e PNG
tests/                  testes do domínio TypeScript
```

A arquitetura e a fronteira entre os motores Python e o app estão em
[`docs/ARQUITETURA_MOBILE.md`](../docs/ARQUITETURA_MOBILE.md).
