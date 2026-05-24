"""
Script de validação: Verifica se todos os componentes estão prontos para usar.
Executa: python validar_instalacao.py
"""
import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("🔍 VALIDAÇÃO DA INSTALAÇÃO - AudioDoc")
print("="*70 + "\n")

# Cores para output
OK = "✅"
ERRO = "❌"
AVISO = "⚠️"

erros = []
avisos = []

# 1. Verificar Python
print(f"{OK} Python {sys.version.split()[0]} detectado")

# 2. Verificar estrutura de diretórios
print("\n📁 Verificando diretórios...")
diretorios = [
    ".",
    "saida_imagens",
    "uploads"
]
for dir_nome in diretorios:
    if os.path.exists(dir_nome):
        print(f"  {OK} {dir_nome}")
    else:
        os.makedirs(dir_nome, exist_ok=True)
        print(f"  {OK} {dir_nome} (criado)")

# 3. Verificar arquivos essenciais
print("\n📄 Verificando arquivos essenciais...")
arquivos_essenciais = [
    "server.py",
    "index.html",
    "audiodoc.py",
    "extrair.py",
    "gerar_audio.py",
    "requirements.txt"
]
for arquivo in arquivos_essenciais:
    if os.path.exists(arquivo):
        tamanho = os.path.getsize(arquivo)
        print(f"  {OK} {arquivo} ({tamanho} bytes)")
    else:
        erros.append(f"Arquivo não encontrado: {arquivo}")
        print(f"  {ERRO} {arquivo}")

# 4. Verificar módulos Python
print("\n📦 Verificando módulos Python...")
modulos_verificar = [
    ("extrair", "Extrator de documentos"),
    ("gerar_audio", "Gerador de áudio"),
    ("descrever_imagem", "Descritor de imagens"),
]

for modulo, descricao in modulos_verificar:
    try:
        __import__(modulo)
        print(f"  {OK} {modulo} ({descricao})")
    except ImportError as e:
        avisos.append(f"Módulo {modulo} não pode ser importado: {e}")
        print(f"  {AVISO} {modulo} - Será necessário ao usar")

# 5. Verificar Flask
print("\n🌐 Verificando Flask...")
try:
    import flask
    print(f"  {OK} Flask {flask.__version__} detectado")
except ImportError:
    avisos.append("Flask não instalado. Execute: pip install Flask")
    print(f"  {ERRO} Flask não instalado")

# 6. Verificar dependências críticas
print("\n⚙️  Verificando dependências críticas...")
dependencias_criticas = [
    ("pymupdf", "Leitura de PDFs"),
    ("docx", "Leitura de DOCX"),
    ("pptx", "Leitura de PPTX"),
    ("PIL", "Processamento de imagens"),
    ("edge_tts", "Síntese de fala"),
]

for modulo, descricao in dependencias_criticas:
    try:
        __import__(modulo)
        print(f"  {OK} {modulo} ({descricao})")
    except ImportError:
        avisos.append(f"{modulo} não instalado: pip install {modulo}")
        print(f"  {AVISO} {modulo} não instalado")

# 7. Verificar arquivo .env
print("\n🔑 Verificando configuração...")
if os.path.exists(".env"):
    print(f"  {OK} Arquivo .env encontrado")
else:
    avisos.append(".env não encontrado. Configure GEMINI_API_KEY se necessário")
    print(f"  {AVISO} Arquivo .env não encontrado")

# 8. Verificar porta 5000
print("\n🔌 Verificando porta 5000...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    resultado = sock.connect_ex(('localhost', 5000))
    sock.close()
    if resultado == 0:
        avisos.append("Porta 5000 já está em uso. Feche o servidor anterior.")
        print(f"  {AVISO} Porta 5000 em uso")
    else:
        print(f"  {OK} Porta 5000 disponível")
except Exception as e:
    print(f"  {AVISO} Não foi possível verificar porta: {e}")

# ============================================================================
# RESUMO
# ============================================================================

print("\n" + "="*70)
if not erros and not avisos:
    print("✅ TUDO ESTÁ PRONTO!")
    print("\nVocê pode começar agora:")
    print("  1. python server.py")
    print("  2. Abra http://localhost:5000 no navegador")
    print("="*70 + "\n")
    sys.exit(0)

elif not erros:
    print("⚠️  AVISOS ENCONTRADOS")
    print("\nO sistema deve funcionar, mas há alguns itens para verificar:")
    for i, aviso in enumerate(avisos, 1):
        print(f"  {i}. {aviso}")
    print("\nVocê pode tentar usar mesmo assim.")
    print("="*70 + "\n")
    sys.exit(1)

else:
    print("❌ ERROS CRÍTICOS ENCONTRADOS")
    print("\nErros que impedem o funcionamento:")
    for i, erro in enumerate(erros, 1):
        print(f"  {i}. {erro}")
    if avisos:
        print("\nAvisos adicionais:")
        for i, aviso in enumerate(avisos, 1):
            print(f"  {i}. {aviso}")
    print("\n" + "="*70)
    print("Resolva os erros acima antes de prosseguir.")
    print("="*70 + "\n")
    sys.exit(2)
