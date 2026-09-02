# Post — FocusLens Mobile v0.6.4

## Texto pronto

Dados de mercado costumam responder “o que aconteceu?”. Eu queria chegar à
pergunta que vem logo depois:

**onde isso encosta nos investimentos que eu já tenho — e o que esse dado não
prova?**

Foi daí que nasceu o FocusLens, um app pessoal e educacional para Android e iOS.
Ele transforma dados públicos do Boletim Focus e da Curva Tesouro em uma jornada
curta:

**mudança → evidência → carteira → cenário → limite**

O app tem quatro abas:

- **Hoje** começa pelo recorte da carteira, não por um painel genérico;
- **Carteira** importa um XLSX da B3 ou recebe posições manuais e guarda tudo
  cifrado somente no aparelho;
- **Cenários** deixa brincar com juros compostos, aportes, inflação, metas,
  tempo, parcelamento e retiradas sem indicar produto;
- **Entenda** conduz uma revisão opcional da semana e sempre fecha com o que a
  leitura não permite concluir.

Algumas escolhas de engenharia foram parte do produto desde o início:

- motores Python puros, separados de rede e interface;
- snapshot público versionado sem carteira;
- AES-256-GCM + cofre nativo para posições locais;
- fallback sintético identificado, sem chamar demonstração de dado real;
- estado das simulações e da revisão somente na sessão;
- nenhuma conta conectada, recomendação, ordem, telemetria financeira ou Open
  Finance.

O corte atual, `v0.6.4`, fecha com **301 testes automatizados**: 194 no núcleo
Python e 107 no mobile. O CI também verifica Ruff, cobertura Python com piso de
85%, TypeScript e o export Android.

É um beta honesto: a experiência foi aceita manualmente no POCO X8 Pro, mas
ADB, iOS, TalkBack e texto ampliado não foram executados como validação formal.
Eles ficam reservados para eventual distribuição em loja/produção e não são
substituídos por um print bonito ou por testes verdes.

Código, arquitetura e decisões:
https://github.com/raulsallesr/financas-pessoais

#Python #ReactNative #Expo #TypeScript #Finanças #OpenData #MobileDevelopment
#Portfolio

## Mídia sugerida

Use como mídia principal o arquivo
`docs/assets/focuslens-mobile-v0.6.4-demo.mp4`: são 21,2 segundos em formato
vertical, sem áudio, com texto legível no próprio app. A sequência mostra:

1. o recorte pessoal e a fotografia pública em Hoje;
2. o laboratório de juros compostos com exemplo fictício;
3. a revisão guiada terminando no que a leitura não prova.

Envie o MP4 diretamente ao LinkedIn, em vez de publicar apenas um link. O GIF
`docs/assets/focuslens-mobile-v0.6.4-demo.gif` é a prévia leve para o README.

Se vídeo não estiver disponível, use o carrossel nesta ordem:

1. `docs/assets/focuslens-mobile-v0.6.4-hoje.png`;
2. `docs/assets/focuslens-mobile-v0.6.4-cenarios.png`;
3. `docs/assets/focuslens-mobile-v0.6.4-entenda.png`.

O vídeo, o GIF e as três imagens são capturas reais do renderer web da mesma
árvore React Native, com fotografia pública e carteira fictícia.

## Antes de publicar

- repositório público por decisão explícita do titular;
- CI público `quality` conferido verde;
- abrir o link em sessão anônima e validar README, licença, GIF e MP4;
- não chamar o beta de “validado em produção” ou dizer que os gates físicos
  dispensados no escopo pessoal foram tecnicamente aprovados;
- não expor APK temporário como distribuição pública permanente.
