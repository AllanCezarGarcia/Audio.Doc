# 📋 Ficha de Acompanhamento e Diagnóstico do Projeto

> *Orientações para a Equipe:* Este documento deve ser preenchido pela equipe para alinhar as expectativas do projeto com os mentores e organizadores. Sejam diretos, honestos e realistas nas respostas.

---

## 🏛️ 1. Identificação da Equipe

- *Nome da Equipe:* 6
- *Nome dos Integrantes e Períodos:* Guilherme Muniz Narciso[7º Período] | Allan Cezar Teodosio Garcia [2º Período] | Lucas Carvalho Uchikado [2º Período] | Caio Santos Gil [7º Período]
- *Link do Repositório (GitHub/GitLab):* https://github.com/AllanCezarGarcia/Audio.Doc
  
---

## 💡 2. O Problema e a Proposta de Valor (O Coração da Ideia)

### 2.1. Qual problema real e específico vocês estão resolvendo?

> *Descrição:*
> Hoje em dia, graças aos incentivos das universidades, muitos alunos com deficiência — em especial deficiência visual — estão tendo um acesso mais justo e completo ao ensino superior, podendo concluir uma formação e atuar no mercado de trabalho. Apesar disso, por causa do excesso de atividades e da falta de tempo, muitos professores não conseguem deixar suas aulas totalmente inclusivas para esse público. Slides, apostilas e PDFs continuam chegando aos alunos cegos como arquivos visuais, dependentes de leitores de tela genéricos que ignoram imagens, gráficos e tabelas — justamente onde costuma estar a informação mais densa do material.
>
> O Audio.Doc surge como um parceiro nesse cenário. Com apenas um clique, é possível transformar um documento — PDF, DOCX, PPTX ou TXT — em um áudio MP3 completo do conteúdo, contemplando:
>
> - Leitura fiel dos textos, com voz natural em português brasileiro;
> - Descrição automática das imagens, gráficos e tabelas presentes no documento, gerada por inteligência artificial e narrada de forma contínua, sem jargão técnico;
> - Navegação parágrafo a parágrafo, com marcadores que indicam ao ouvinte em que parte do material o áudio se encontra (slide atual, início e fim de cada descrição de imagem, etc.);
> - Preservação da ordem original do documento, garantindo que texto e elementos visuais sejam narrados no mesmo fluxo em que aparecem.
>
> O objetivo é dar autonomia ao aluno com deficiência visual para consumir o material da disciplina no mesmo nível de profundidade que os colegas videntes, sem depender da disponibilidade do professor ou de monitores para descrever cada imagem.

### 2.2. O diferencial da solução está claro? O que torna a ideia de vocês única?

> *Descrição:*
> Leitores de tela tradicionais (NVDA, JAWS, TalkBack) leem apenas o texto cru de um documento — quando encontram uma imagem, no melhor caso anunciam "imagem" e seguem em frente, deixando o aluno sem acesso a gráficos, tabelas, esquemas e fotos que muitas vezes carregam o conteúdo principal da aula. Conversores de texto-para-voz online comuns (NaturalReader, Speechify, Murf) também ignoram esse problema e ainda exigem que o usuário copie e cole o texto manualmente.
>
> O diferencial do Audio.Doc está em três pontos:
>
> 1. **Descrição inteligente de imagens, gráficos e tabelas.** Usando IA generativa (Gemini), o sistema gera narrações em linguagem natural, sem markdown nem jargão técnico, com instruções específicas para descrever tabelas e gráficos como um locutor faria — em prosa contínua, pronta pra ser ouvida.
> 2. **Pipeline um clique → MP3 pronto.** O usuário não precisa pré-processar o documento, separar texto e imagens, ou usar ferramentas diferentes. Sobe o arquivo, escolhe a voz, baixa o áudio.
> 3. **Preservação da ordem e da navegação.** O áudio segue a ordem natural do documento (parágrafo → imagem → parágrafo seguinte) e inclui marcadores faladados ("Slide 3 de 12", "Descrição da imagem 2", "Fim da descrição"), facilitando a localização dentro do conteúdo — algo que players de áudio comuns não oferecem.
>
> Em resumo: as alternativas existentes resolvem ou só o "ler texto em voz alta", ou só o "descrever uma imagem isolada". O Audio.Doc une as duas coisas em um único fluxo, voltado especificamente para material acadêmico.

---

## ⚙️ 3. A Solução na Prática (Como Funciona)

### 3.1. Como a solução funciona para o usuário final?

> *Descrição:*
> O fluxo do usuário foi pensado para ser o mais curto possível, principalmente porque o público-alvo inclui pessoas com deficiência visual usando leitores de tela:
>
> 1. **Acessa o site** do Audio.Doc pelo navegador (hospedado no Render).
> 2. **Faz upload do documento** (PDF, DOCX, PPTX ou TXT) por meio de um campo de arquivo simples e bem rotulado.
> 3. **Escolhe a voz** que prefere ouvir (Francisca, Antônio, Thalita ou Macério — vozes em português brasileiro).
> 4. **Clica em "Converter"** e acompanha o progresso em tempo real (barra de progresso com mensagens faladas: "Extraindo conteúdo", "Descrevendo imagem 3 de 7", "Gerando áudio", "Concluído").
> 5. **Baixa o MP3** ao final e ouve em qualquer player.
>
> Por baixo dos panos, o sistema:
> - Identifica o tipo do arquivo e usa o extrator adequado;
> - Separa o documento em blocos ordenados de texto e imagem;
> - Envia cada imagem para o Gemini, que gera uma descrição narrável;
> - Monta um roteiro único intercalando texto original e descrições;
> - Quebra o roteiro em pedaços e gera o MP3 final usando edge-tts (síntese de voz neural da Microsoft).

### 3.2. Quais são as principais tecnologias, linguagens ou ferramentas que decidiram usar?

> *Descrição:*
>
> **Backend (Python 3):**
> - **Flask** — framework web que expõe a API REST e serve o frontend
> - **Gunicorn + Gevent** — servidor de produção com suporte a streaming (SSE) para o progresso em tempo real
> - **PyMuPDF (fitz)** — extração de texto e imagens de PDFs
> - **python-docx** — extração de texto, tabelas e imagens de arquivos DOCX
> - **python-pptx** — extração de slides, formas, tabelas, imagens e notas do apresentador de PPTX
> - **edge-tts** — síntese de voz neural em português brasileiro (gratuita)
> - **Google GenAI SDK (Gemini 2.5 Flash Lite)** — descrição automática de imagens, gráficos e tabelas
> - **Pillow** — manipulação das imagens antes do envio à IA
>
> **Frontend:**
> - **HTML5, CSS3 e JavaScript puro** — sem framework, mantendo a página leve e acessível por leitores de tela
> - **Server-Sent Events (SSE)** — para atualizar a barra de progresso em tempo real durante a conversão
>
> **Infraestrutura:**
> - **GitHub** — controle de versão e integração contínua com a hospedagem
> - **Render.com** — hospedagem do site (free tier), com deploy automático a cada push
> - **Variáveis de ambiente** para guardar a chave da API do Gemini com segurança

---

## 👥 4. Gestão e Divisão de Trabalho

### 4.1. Quem está fazendo o quê na equipe?

- *Guilherme:* Desenvolvimento do código em python, hospedagem do site e organização do grupo
- *Allan:* Desenvolvimento de mecânicas do front, hospedagem do site, fusão entre back-front e revisor
- *Lucas:* Revisor, apresentador, geração de roteiros, criação do front
- *Caio:* Criação do front, revisor, teste de usabilidade

---

## 🛠️ 5. Status Atual do Desenvolvimento (O MVP)

### 5.1. Vocês já começaram o protótipo visual ou o código do MVP? Qual o percentual de conclusão estimado?

- *Status:* ( ) Não começamos | ( ) Apenas rascunho visual | ( ) Código inicial iniciado | (X) Mais da metade pronto

### 5.2. O projeto já funciona em alguma parte? O que já está codificado e operacional?

> *Descrição:*
> O projeto já está funcional de ponta a ponta em ambiente local e em fase final de deploy no Render. Está operacional:
>
> - **Pipeline completo de extração** para os quatro formatos suportados: PDF, DOCX, PPTX e TXT. Cada extrator preserva a ordem original do documento e separa texto e imagens em blocos.
> - **Descrição automática de imagens via Gemini**, com prompt especializado para gerar narrações sem markdown, com tratamento específico para tabelas, gráficos, fotos e texto dentro de imagens.
> - **Sistema de retry e controle de cota** na chamada à IA — em caso de rate limit, o sistema espera e tenta de novo; em caso de cota diária esgotada, substitui a descrição por uma mensagem amigável em vez de travar.
> - **Geração de MP3 com edge-tts**, com quebra automática do roteiro em pedaços (respeitando o fim de frase) e concatenação dos áudios — permitindo converter documentos longos sem cortar no meio de uma palavra.
> - **API Flask completa** com endpoints para conversão, acompanhamento de progresso em tempo real (SSE), download do MP3 e listagem de arquivos gerados.
> - **Interface web** (`index.html`) com formulário de upload, seleção de voz, barra de progresso e botão de download.
> - **CLI funcional** (`audiodoc.py`) que permite usar o sistema pelo terminal sem precisar do site.

### 5.3. O que foi ou será "Mockado" (dados fictícios/estáticos)?

> *Descrição:*
> Quase nada precisa ser mockado, porque o pipeline já funciona com arquivos reais. Para a apresentação, podem ser usados como "mock":
>
> - **Documentos pré-selecionados** de exemplo (um PDF, um PPTX e um DOCX já testados) para garantir que a demonstração ao vivo não dependa de subir um arquivo do zero diante da banca — economiza tempo de upload e processamento.
> - **MP3s já gerados previamente** dos mesmos documentos, como plano B caso a conexão com a API do Gemini fique instável ou a cota gratuita esgote no dia da apresentação.
> - **Mensagens de progresso** continuam reais, vindas do servidor — não são fingidas.

### 5.4. O que ainda falta finalizar obrigatoriamente para a entrega?

> *Descrição:*
>
> 1. **Concluir o deploy no Render** com a variável de ambiente da chave do Gemini configurada e o ajuste do `Procfile`/Start Command para usar Gunicorn + Gevent.
> 2. **Testar o fluxo completo em produção** com documentos de cada formato (PDF, DOCX, PPTX, TXT) para garantir que o disco efêmero do Render não está causando perda de arquivos durante a conversão.
> 3. **Ajustar acessibilidade do `index.html`** — garantir labels ARIA corretos nos campos de upload e voz, foco visível em todos os elementos interativos e mensagens de status anunciadas por leitores de tela (`aria-live`).
> 4. **Definir limite de tamanho de arquivo na interface** para evitar que um upload muito grande consuma toda a cota diária da API do Gemini de uma só vez.
> 5. **Revisar o README do repositório** com instruções claras de uso (link do site, formatos suportados, como rodar local) e créditos da equipe.
> 6. **Preparar os documentos e MP3s de demonstração** para a apresentação.

---

## 🚧 6. Obstáculos e Pedidos de Ajuda

### 6.1. Qual maior dificuldade da equipe?

> *Descrição:*
> A maior dificuldade tem sido a **hospedagem do projeto em produção**. O backend é em Python (Flask) e processa arquivos relativamente pesados, então hospedagens estáticas como GitHub Pages e Netlify não atendem. Tivemos que pesquisar alternativas com free tier real e migrar para o Render, o que envolveu ajustar o `Procfile`, configurar Gunicorn com worker Gevent (porque o SSE da barra de progresso não funciona com worker padrão), tratar o sistema de arquivos efêmero da plataforma e lidar com o sleep do free tier (15 minutos sem uso e o site dorme).
>
> Em segundo lugar, o **gerenciamento da cota da API do Gemini** preocupa: a cota gratuita é compartilhada por chave, então se o site for público e várias pessoas usarem ao mesmo tempo, a cota acaba rápido. Estamos pensando em limitar o tamanho dos arquivos e o número de imagens por conversão.
>
> Em terceiro, garantir **boa acessibilidade real** (não apenas legalmente compliant) na interface — testar com leitor de tela de verdade e ajustar contraste, ordem de tabulação e anúncios dinâmicos exige tempo que estamos correndo para encaixar antes da entrega.

---

## 🎤 7. Preparação para o Show (O Pitch)

### 7.1. Como será a estratégia de apresentação de vocês na segunda-feira?

> *Descrição:*
> A apresentação será dividida em três blocos curtos, conduzidos principalmente pelo **Lucas** (apresentador), com **Guilherme** e **Allan** dando suporte técnico na demonstração ao vivo e **Caio** acompanhando o teste de usabilidade em tempo real.
>
> **Bloco 1 — O problema (≈1 min):** Lucas abre contextualizando a realidade dos alunos com deficiência visual nas universidades e explicando por que leitores de tela comuns não bastam quando o material tem imagens, gráficos e tabelas.
>
> **Bloco 2 — A solução ao vivo (≈3 min):** Demonstração no próprio site hospedado. Allan faz o upload de um PDF de exemplo (já preparado), escolhe uma voz e mostra a barra de progresso em tempo real. Enquanto o áudio é gerado, Guilherme explica brevemente o que está acontecendo por baixo dos panos (extração, descrição via IA, geração do MP3). Ao final, **tocamos um trecho do MP3 gerado** para a banca ouvir — é o momento mais impactante, porque mostra a descrição de uma imagem real sendo narrada.
>
> **Bloco 3 — Tecnologias e próximos passos (≈1 min):** Lucas fecha resumindo o stack usado (Python, Flask, Gemini, edge-tts, Render) e o que pretendemos evoluir (suporte a mais formatos, geração de capítulos no MP3, modo "trazer sua própria chave do Gemini" para uso ilimitado).
>
> **Plano B:** Se a demonstração ao vivo travar (cota da API, internet do local, sleep do Render), temos um vídeo gravado de 2 minutos mostrando o fluxo completo do início ao fim, mais os MP3s já gerados previamente para tocar diretamente.
