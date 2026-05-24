@echo off
cd /d c:\Audiodoc
echo.
echo ============================================================
echo  AudioDoc - Instalando Dependencias
echo ============================================================
echo.
echo  Instalando pacotes do requirements.txt...
echo.
python -m pip install -r requirements.txt
echo.
echo ============================================================
echo  Dependencias instaladas com sucesso!
echo ============================================================
echo.
echo  Proximo passo: Clique duplo em "rodar_servidor.bat"
echo.
pause
