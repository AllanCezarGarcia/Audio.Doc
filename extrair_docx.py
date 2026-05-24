"""
Fase 4a: Extrai texto e imagens de um DOCX mantendo a ordem.
"""
import os
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def extrair_conteudo_docx(caminho_docx: str, pasta_saida: str = "saida_imagens"):
    """
    Lê um DOCX e devolve uma lista de blocos na ordem em que aparecem.
    """
    Path(pasta_saida).mkdir(exist_ok=True)

    doc = Document(caminho_docx)
    blocos = []
    contador_imagens = 0

    # Mapa: id da imagem -> bytes
    imagens_doc = {}
    for rel_id, rel in doc.part.rels.items():
        if "image" in rel.target_ref:
            imagens_doc[rel_id] = rel.target_part

    # Percorre o corpo do documento (parágrafos e tabelas) NA ORDEM
    for elemento in doc.element.body.iter():
        tag = elemento.tag.split("}")[-1]  # remove namespace

        # 1) Parágrafos
        if tag == "p":
            # Texto do parágrafo
            textos = []
            for run in elemento.iter(qn("w:t")):
                if run.text:
                    textos.append(run.text)
            texto = "".join(textos).strip()

            if texto:
                blocos.append({
                    "tipo": "texto",
                    "conteudo": texto
                })

            # Imagens dentro do parágrafo
            for blip in elemento.iter(qn("a:blip")):
                rel_id = blip.get(qn("r:embed"))
                if rel_id and rel_id in imagens_doc:
                    image_part = imagens_doc[rel_id]
                    ext = image_part.content_type.split("/")[-1]
                    if ext == "jpeg":
                        ext = "jpg"

                    contador_imagens += 1
                    nome_arquivo = f"img_{contador_imagens}.{ext}"
                    caminho_imagem = os.path.join(pasta_saida, nome_arquivo)

                    with open(caminho_imagem, "wb") as f:
                        f.write(image_part.blob)

                    blocos.append({
                        "tipo": "imagem",
                        "caminho": caminho_imagem
                    })

        # 2) Tabelas (extrai texto célula por célula)
        elif tag == "tbl":
            linhas = []
            for linha in elemento.iter(qn("w:tr")):
                celulas = []
                for celula in linha.iter(qn("w:tc")):
                    textos_celula = []
                    for t in celula.iter(qn("w:t")):
                        if t.text:
                            textos_celula.append(t.text)
                    celulas.append("".join(textos_celula).strip())
                if any(celulas):
                    linhas.append(" | ".join(celulas))

            if linhas:
                texto_tabela = "Tabela: " + ". ".join(linhas)
                blocos.append({
                    "tipo": "texto",
                    "conteudo": texto_tabela
                })

    return blocos


# --- Teste rápido ---
if __name__ == "__main__":
    caminho = "teste.docx"

    if not os.path.exists(caminho):
        print(f"❌ Arquivo '{caminho}' não encontrado.")
        print("   Coloque um DOCX chamado 'teste.docx' na pasta do projeto.")
    else:
        blocos = extrair_conteudo_docx(caminho)
        print(f"\n✅ Extração concluída! {len(blocos)} blocos encontrados.\n")

        for i, bloco in enumerate(blocos, start=1):
            if bloco["tipo"] == "texto":
                preview = bloco["conteudo"][:80].replace("\n", " ")
                print(f"[{i}] TEXTO : {preview}...")
            else:
                print(f"[{i}] IMAGEM: {bloco['caminho']}")