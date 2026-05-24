"""
Fase 4b: Extrai texto de um arquivo TXT.
"""
import os


def extrair_conteudo_txt(caminho_txt: str):
    """
    Lê um TXT e devolve a estrutura padrão de blocos.
    """
    # Tenta UTF-8 primeiro, cai pra latin-1 se falhar
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(caminho_txt, "r", encoding=encoding) as f:
                texto = f.read().strip()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"Não foi possível ler o arquivo '{caminho_txt}'.")

    if not texto:
        return []

    return [{"tipo": "texto", "conteudo": texto}]


# --- Teste rápido ---
if __name__ == "__main__":
    caminho = "teste.txt"

    if not os.path.exists(caminho):
        print(f"❌ Arquivo '{caminho}' não encontrado.")
        print("   Crie um TXT chamado 'teste.txt' na pasta do projeto.")
    else:
        blocos = extrair_conteudo_txt(caminho)
        print(f"\n✅ Extração concluída! {len(blocos)} blocos.\n")
        for i, bloco in enumerate(blocos, start=1):
            preview = bloco["conteudo"][:200].replace("\n", " ")
            print(f"[{i}] TEXTO: {preview}...")