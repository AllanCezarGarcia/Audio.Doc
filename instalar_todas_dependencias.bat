@echo off
echo.
echo ============================================================
echo  AudioDoc - Instalacao Manual via Prompt
echo ============================================================
echo.
echo  Vai instalar todas as dependencias agora...
echo.
cd /d c:\Audiodoc

echo Instalando pymupdf (para PDFs)...
python -m pip install pymupdf

echo Instalando python-docx (para DOCX)...
python -m pip install python-docx

echo Instalando python-pptx (para PPTX)...
python -m pip install python-pptx

echo Instalando google-genai (para descrever imagens)...
python -m pip install google-genai

echo Instalando Pillow (para processamento de imagens)...
python -m pip install Pillow

echo Instalando edge-tts (para sintese de fala)...
python -m pip install edge-tts

echo Instalando python-dotenv (para variaveis de ambiente)...
python -m pip install python-dotenv

echo Instalando Flask (para API web)...
python -m pip install Flask

echo.
echo ============================================================
echo  Todas as dependencias instaladas com sucesso!
echo ============================================================
echo.
pause
