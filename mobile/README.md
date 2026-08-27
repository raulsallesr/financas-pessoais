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
npm install
npm run web
```

Esse comando abre a mesma árvore de componentes React Native no renderer web e
é o caminho imediato para revisar a experiência. O produto continua sendo
React Native; o renderer web é somente uma bancada de desenvolvimento.

## Como rodar em um aparelho

Este corte usa Expo SDK 57. Para um projeto de produto, o caminho recomendado é
um **development build** próprio, não depender do aplicativo genérico Expo Go.
Depois que esse build estiver instalado no Android/iOS, inicie o Metro com:

```powershell
npm start
```

O empacotamento instalável e a assinatura do development build são o próximo
incremento. O gate atual já gera o bundle Android, mas ainda não publica APK,
AAB ou build iOS.

Se o checkout estiver dentro de OneDrive e o `npm install` encontrar limites de
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
