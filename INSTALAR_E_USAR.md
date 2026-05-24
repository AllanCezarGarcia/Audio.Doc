# 🎧 AudioDoc — Documentos em Áudio Acessível

Sistema para converter documentos (PDF, DOCX, PPTX, TXT) em áudio MP3 com interface web moderna.

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🚀 Como Usar

### 1. Instalar Dependências

**Windows (GUI):**
- Clique duas vezes em `instalar_dependencias.bat`

**Linha de comando:**
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Servidor

**Windows (GUI):**
- Clique duas vezes em `rodar_servidor.bat`

**Linha de comando:**
```bash
python server.py
```

Você verá:
```
============================================================
🎧 AudioDoc API — Iniciando servidor...
============================================================
📍 Acesse: http://localhost:5000
============================================================
```

### 3. Abrir no Navegador

Acesse **http://localhost:5000** no seu navegador.

---

## 💡 Funcionalidades

✅ **Upload de Documentos** — Arraste ou selecione PDF, DOCX, PPTX ou TXT  
✅ **Seleção de Voz** — Escolha entre Francisca, Antonio, Thalita ou Macerio  
✅ **Conversão para Áudio** — Converte automaticamente em MP3  
✅ **Biblioteca** — Gerencia e reproduz seus arquivos de áudio  
✅ **Download** — Baixe os arquivos MP3 gerados  

---

## 📁 Estrutura do Projeto

```
Audiodoc/
├── server.py                    # API Flask (backend)
├── index.html                   # Interface web (frontend)
├── audiodoc.py                  # Script CLI principal
├── extrair.py                   # Router de extração
├── extrair_pdf.py               # Extrator de PDF
├── extrair_docx.py              # Extrator de DOCX
├── extrair_pptx.py              # Extrator de PPTX
├── extrair_txt.py               # Extrator de TXT
├── gerar_audio.py               # Gerador de áudio MP3
├── descrever_imagem.py          # Descrição de imagens com IA
├── requirements.txt             # Dependências Python
├── rodar_servidor.bat           # Script para iniciar servidor (Windows)
└── instalar_dependencias.bat    # Script para instalar dependências (Windows)
```

---

## 🔑 Configuração de API Keys

O projeto usa a API Google Gemini para descrever imagens. Configure a chave no arquivo `.env`:

```env
GEMINI_API_KEY=sua_chave_aqui
```

Ou defina como variável de ambiente:
```bash
set GEMINI_API_KEY=sua_chave_aqui
```

---

## 🎯 Endpoints da API

### `GET /`
Serve a página HTML principal.

### `GET /api/info`
Retorna informações sobre formatos suportados e vozes disponíveis.

```json
{
  "app": "AudioDoc",
  "formatos_suportados": [".pdf", ".docx", ".txt", ".pptx"],
  "vozes": {
    "francisca": "pt-BR-FranciscaNeural",
    "antonio": "pt-BR-AntonioNeural",
    "thalita": "pt-BR-ThalitaMultilingualNeural",
    "macerio": "pt-BR-MacerioMultilingualNeural"
  }
}
```

### `POST /api/converter`
Converte um documento em áudio.

**Parâmetros:**
- `file` (multipart/form-data) — Arquivo a converter
- `voz` (form field, opcional) — Voz desejada (padrão: francisca)
- `nome_saida` (form field, opcional) — Nome customizado para o MP3

**Resposta de sucesso:**
```json
{
  "sucesso": true,
  "mensagem": "Áudio gerado com sucesso!",
  "arquivo_saida": "documento_audio.mp3",
  "download_url": "/api/download/documento_audio.mp3",
  "blocos": 42,
  "voz": "pt-BR-FranciscaNeural"
}
```

### `GET /api/download/<nome_arquivo>`
Baixa um arquivo MP3 gerado.

### `GET /api/arquivos`
Lista todos os arquivos MP3 disponíveis.

```json
{
  "arquivos": [
    {
      "nome": "documento_audio.mp3",
      "tamanho": "5.23 MB",
      "url": "/api/download/documento_audio.mp3"
    }
  ]
}
```

---

## 🛠️ Desenvolvimento

### Usar a CLI (Linha de Comando)

```bash
# Converter um arquivo
python audiodoc.py documento.pdf -o saida.mp3 --voz francisca

# Formatos suportados
python audiodoc.py --help
```

### Modificar o Backend

O servidor Flask está em `server.py`. Você pode:
- Adicionar novos endpoints
- Personalizar tratamento de erros
- Integrar outras APIs

### Modificar o Frontend

A interface web está em `index.html`. Para editar:
- Estilos CSS: Seção `<style>`
- Comportamento: Função JavaScript ao final

---

## ⚙️ Requisitos Instalados

- **Flask** — Framework web Python
- **PyMuPDF** — Extração de PDF
- **python-docx** — Extração de DOCX
- **python-pptx** — Extração de PPTX
- **google-genai** — Descrição de imagens
- **Pillow** — Processamento de imagens
- **edge-tts** — Síntese de fala (Text-to-Speech)
- **python-dotenv** — Carregamento de variáveis de ambiente

---

## 📝 Licença

Desenvolvido para Hackathon 2026 UGB.

---

## 🤝 Suporte

Em caso de dúvidas ou problemas:
1. Verifique se Flask está instalado: `pip list | findstr Flask`
2. Verifique se a porta 5000 está disponível
3. Consulte os logs da API para erros específicos

**Bom uso! 🎧**
