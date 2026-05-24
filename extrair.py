"""
Fase 4c: Roteador — decide qual extrator usar baseado na extensão do arquivo.
"""
import os
from extrair_pdf import extrair_conteudo_pdf
from extrair_docx import extrair_conteudo_docx
from extrair_txt import extrair_conteudo_txt
from extrair_pptx import extrair_conteudo_pptx


FORMATOS_SUPORTADOS = (".pdf", ".docx", ".txt", ".pptx")


def extrair_conteudo(caminho_arquivo: str):
    """
    Detecta o tipo do arquivo pela extensão e chama o extrator certo.
    Devolve uma lista padronizada de blocos.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    if extensao == ".pdf":
        return extrair_conteudo_pdf(caminho_arquivo)
    elif extensao == ".docx":
        return extrair_conteudo_docx(caminho_arquivo)
    elif extensao == ".txt":
        return extrair_conteudo_txt(caminho_arquivo)
    elif extensao == ".pptx":
        return extrair_conteudo_pptx(caminho_arquivo)
    else:
        raise ValueError(
            f"Formato '{extensao}' não suportado. "
            f"Use um destes: {', '.join(FORMATOS_SUPORTADOS)}"
        )


# --- Teste rápido ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python extrair.py <caminho_do_arquivo>")
        print("Exemplo: python extrair.py teste.pptx")
        sys.exit(1)

    caminho = sys.argv[1]
    blocos = extrair_conteudo(caminho)
    print(f"\n✅ {len(blocos)} blocos extraídos de '{caminho}'\n")

    for i, bloco in enumerate(blocos, start=1):
        if bloco["tipo"] == "texto":
            preview = bloco["conteudo"][:80].replace("\n", " ")
            print(f"[{i}] TEXTO : {preview}...")
        else:
            print(f"[{i}] IMAGEM: {bloco['caminho']}")