"""
Fase 1: Extrai texto e imagens de um PDF mantendo a ordem.
"""
import fitz  # PyMuPDF
import os
from pathlib import Path


def extrair_conteudo_pdf(caminho_pdf: str, pasta_saida: str = "saida_imagens"):
    """
    Lê um PDF e devolve uma lista de blocos na ordem em que aparecem.
    Cada bloco é um dicionário:
      {"tipo": "texto", "conteudo": "..."}
      {"tipo": "imagem", "caminho": "saida_imagens/img_1.png"}
    """
    # Cria a pasta onde as imagens serão salvas
    Path(pasta_saida).mkdir(exist_ok=True)

    doc = fitz.open(caminho_pdf)
    blocos = []
    contador_imagens = 0

    for num_pagina, pagina in enumerate(doc, start=1):
        print(f"Processando página {num_pagina}/{len(doc)}...")

        # 1) Extrai o texto da página
        texto = pagina.get_text().strip()
        if texto:
            blocos.append({
                "tipo": "texto",
                "pagina": num_pagina,
                "conteudo": texto
            })

        # 2) Extrai as imagens da página
        imagens = pagina.get_images(full=True)
        for img_info in imagens:
            xref = img_info[0]  # referência interna da imagem no PDF
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]  # ex: "png", "jpeg"

            contador_imagens += 1
            nome_arquivo = f"img_{contador_imagens}.{ext}"
            caminho_imagem = os.path.join(pasta_saida, nome_arquivo)

            with open(caminho_imagem, "wb") as f:
                f.write(image_bytes)

            blocos.append({
                "tipo": "imagem",
                "pagina": num_pagina,
                "caminho": caminho_imagem
            })

    doc.close()
    return blocos


# --- Teste rápido ---
if __name__ == "__main__":
    # Coloque um PDF de teste na mesma pasta e troque o nome abaixo
    caminho = "teste.pdf"

    if not os.path.exists(caminho):
        print(f"❌ Arquivo '{caminho}' não encontrado.")
        print("   Coloque um PDF chamado 'teste.pdf' na pasta do projeto.")
    else:
        blocos = extrair_conteudo_pdf(caminho)
        print(f"\n✅ Extração concluída! {len(blocos)} blocos encontrados.\n")

        for i, bloco in enumerate(blocos, start=1):
            if bloco["tipo"] == "texto":
                preview = bloco["conteudo"][:80].replace("\n", " ")
                print(f"[{i}] TEXTO  (pág {bloco['pagina']}): {preview}...")
            else:
                print(f"[{i}] IMAGEM (pág {bloco['pagina']}): {bloco['caminho']}")