"""
AudioDoc — Converte documentos (PDF, DOCX, PPTX, TXT) em áudio acessível.

Uso:
    python audiodoc.py arquivo.pdf
    python audiodoc.py arquivo.pdf -o livro.mp3
    python audiodoc.py arquivo.pptx --voz Antonio
    python audiodoc.py arquivo.docx -o aula.mp3 --voz Francisca
"""
import argparse
import os
import sys

from extrair import extrair_conteudo, FORMATOS_SUPORTADOS
from gerar_audio import gerar_audio_de_blocos


# Atalhos amigáveis para nomes de voz
VOZES = {
    "francisca": "pt-BR-FranciscaNeural",
    "antonio":   "pt-BR-AntonioNeural",
    "thalita":   "pt-BR-ThalitaMultilingualNeural",
    "macerio":   "pt-BR-MacerioMultilingualNeural",
}


def parse_voz(nome: str) -> str:
    """Aceita um apelido (Francisca) ou o nome completo (pt-BR-FranciscaNeural)."""
    nome_limpo = nome.lower().strip()
    if nome_limpo in VOZES:
        return VOZES[nome_limpo]
    # Se o usuário passou o nome completo, deixa passar
    return nome


def main():
    parser = argparse.ArgumentParser(
        description="Converte documentos em áudio acessível para pessoas cegas.",
        epilog="Formatos suportados: " + ", ".join(FORMATOS_SUPORTADOS),
    )
    parser.add_argument(
        "arquivo",
        help="Caminho para o arquivo de entrada (PDF, DOCX, PPTX ou TXT)."
    )
    parser.add_argument(
        "-o", "--saida",
        default=None,
        help="Nome do arquivo MP3 de saída. Padrão: <nome_do_arquivo>.mp3"
    )
    parser.add_argument(
        "--voz",
        default="francisca",
        help="Voz: francisca, antonio, thalita, macerio (padrão: francisca)"
    )

    args = parser.parse_args()

    # Validações
    if not os.path.exists(args.arquivo):
        print(f"❌ Arquivo não encontrado: {args.arquivo}")
        sys.exit(1)

    extensao = os.path.splitext(args.arquivo)[1].lower()
    if extensao not in FORMATOS_SUPORTADOS:
        print(f"❌ Formato '{extensao}' não suportado.")
        print(f"   Use um destes: {', '.join(FORMATOS_SUPORTADOS)}")
        sys.exit(1)

    # Define o nome do MP3 de saída
    if args.saida:
        caminho_saida = args.saida
        if not caminho_saida.lower().endswith(".mp3"):
            caminho_saida += ".mp3"
    else:
        nome_base = os.path.splitext(os.path.basename(args.arquivo))[0]
        caminho_saida = f"{nome_base}.mp3"

    voz = parse_voz(args.voz)

    # Mostra resumo
    print("=" * 60)
    print("🎧 AudioDoc — Documentos em áudio acessível")
    print("=" * 60)
    print(f"📂 Entrada: {args.arquivo}")
    print(f"💾 Saída:   {caminho_saida}")
    print(f"🎙️ Voz:     {voz}")
    print("=" * 60 + "\n")

    # Pipeline
    print(f"📂 Lendo '{args.arquivo}'...")
    blocos = extrair_conteudo(args.arquivo)
    print(f"   {len(blocos)} blocos encontrados.\n")

    gerar_audio_de_blocos(blocos, caminho_saida=caminho_saida, voz=voz)

    print("\n🎉 Pronto! Abra o arquivo MP3 e ouça.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Cancelado pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)