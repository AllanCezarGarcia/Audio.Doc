"""
Fase 5: Monta o roteiro completo e gera o áudio MP3.
Suporta textos longos quebrando em pedaços e concatenando os MP3s.
"""
import asyncio
import os
import re
import tempfile
import edge_tts
from descrever_imagem import descrever_imagem


VOZ_PADRAO = "pt-BR-FranciscaNeural"

# Tamanho máximo de cada pedaço enviado ao edge-tts (caracteres).
# Textos muito longos cortam silenciosamente, então quebramos em blocos.
TAMANHO_MAX_PEDACO = 3500


def montar_roteiro(blocos: list) -> str:
    """
    Converte a lista de blocos num roteiro de texto único,a
    substituindo cada imagem pela sua descrição.
    Erros viram mensagens amigáveis em vez de jargão técnico.
    """
    from descrever_imagem import PREFIXO_ERRO

    partes = []
    total_imagens = sum(1 for b in blocos if b["tipo"] == "imagem")
    img_atual = 0
    cota_esgotada = False

    for bloco in blocos:
        if bloco["tipo"] == "texto":
            partes.append(bloco["conteudo"])

        elif bloco["tipo"] == "imagem":
            img_atual += 1

            # Se já sabemos que a cota acabou, nem chama a API de novo
            if cota_esgotada:
                descricao = "Esta imagem não pôde ser descrita."
            else:
                print(f"🖼️  Descrevendo imagem {img_atual}/{total_imagens}...")
                resultado = descrever_imagem(bloco["caminho"])

                # Detecta erro pelo prefixo interno
                if resultado.startswith(PREFIXO_ERRO):
                    tipo_erro = resultado.replace(PREFIXO_ERRO, "").split("|")[0]

                    if tipo_erro == "cota_diaria":
                        print("   ❌ Cota diária do Gemini esgotada. Imagens seguintes não serão descritas.")
                        cota_esgotada = True
                        descricao = (
                            "Esta imagem não pôde ser descrita porque a cota diária "
                            "do serviço de descrição foi atingida. Tente novamente amanhã."
                        )
                    elif tipo_erro == "arquivo_invalido":
                        descricao = "Esta imagem não pôde ser aberta."
                    elif tipo_erro == "resposta_vazia":
                        descricao = "Esta imagem não pôde ser descrita."
                    else:
                        descricao = "Esta imagem não pôde ser descrita devido a um erro temporário."
                    print(f"   ⚠️  Imagem {img_atual}: {descricao}")
                else:
                    descricao = resultado

            marcador_inicio = f"Descrição da imagem {img_atual}."
            marcador_fim = f"Fim da descrição da imagem {img_atual}."
            partes.append(f"{marcador_inicio} {descricao} {marcador_fim}")

    return "\n\n".join(partes)


def quebrar_texto(texto: str, tamanho_max: int = TAMANHO_MAX_PEDACO) -> list:
    """
    Quebra o texto em pedaços de no máximo `tamanho_max` caracteres,
    sempre respeitando o fim de uma frase (ponto, exclamação, interrogação,
    quebra de linha). Nunca corta no meio de uma palavra.
    """
    texto = texto.strip()
    if len(texto) <= tamanho_max:
        return [texto]

    # Quebra em "sentenças" usando . ! ? ou quebra de linha como delimitador
    # O regex mantém o pontuador junto com a frase
    sentencas = re.split(r"(?<=[\.\!\?\n])\s+", texto)

    pedacos = []
    pedaco_atual = ""

    for sentenca in sentencas:
        # Se a sentença sozinha já é maior que o limite, quebra ela por palavras
        if len(sentenca) > tamanho_max:
            if pedaco_atual:
                pedacos.append(pedaco_atual.strip())
                pedaco_atual = ""

            palavras = sentenca.split(" ")
            sub_pedaco = ""
            for palavra in palavras:
                if len(sub_pedaco) + len(palavra) + 1 > tamanho_max:
                    pedacos.append(sub_pedaco.strip())
                    sub_pedaco = palavra
                else:
                    sub_pedaco = (sub_pedaco + " " + palavra).strip()
            if sub_pedaco:
                pedaco_atual = sub_pedaco
            continue

        # Caso normal: tenta adicionar a sentença no pedaço atual
        if len(pedaco_atual) + len(sentenca) + 1 > tamanho_max:
            pedacos.append(pedaco_atual.strip())
            pedaco_atual = sentenca
        else:
            pedaco_atual = (pedaco_atual + " " + sentenca).strip()

    if pedaco_atual:
        pedacos.append(pedaco_atual.strip())

    return pedacos


async def _gerar_pedaco_mp3(texto: str, caminho_saida: str, voz: str):
    """Gera um único MP3 a partir de um pedaço de texto."""
    comunicador = edge_tts.Communicate(texto, voz)
    await comunicador.save(caminho_saida)


def _concatenar_mp3s(caminhos_mp3: list, caminho_final: str):
    """
    Concatena vários MP3s em um único arquivo.
    Como todos foram gerados com a mesma voz e mesmo bitrate, dá pra
    simplesmente concatenar os bytes — não precisa de ffmpeg.
    """
    with open(caminho_final, "wb") as final:
        for caminho in caminhos_mp3:
            with open(caminho, "rb") as parte:
                final.write(parte.read())


async def _gerar_audio_longo(texto: str, caminho_saida: str, voz: str, callback=None):
    """
    Gera o áudio quebrando o texto em pedaços, salvando cada um num MP3
    temporário, e concatenando tudo no final.
    
    callback: função(progresso_pct, mensagem) para relatar progresso
    """
    pedacos = quebrar_texto(texto)
    total = len(pedacos)
    print(f"📦 Texto dividido em {total} pedaço(s) para o TTS.")
    
    if callback:
        callback(10, f"Iniciando síntese de {total} pedaços...")

    # Cria pasta temporária pros MP3s intermediários
    with tempfile.TemporaryDirectory() as tmp_dir:
        caminhos_pedacos = []

        for i, pedaco in enumerate(pedacos, start=1):
            print(f"🎙️  Gerando pedaço {i}/{total} ({len(pedaco)} caracteres)...")
            caminho_pedaco = os.path.join(tmp_dir, f"pedaco_{i:04d}.mp3")
            
            # Calcula progresso (distribuído entre 10% e 90%)
            progresso = 10 + (i / total) * 80
            if callback:
                callback(progresso, f"Gerando pedaço {i}/{total}...")
            
            try:
                await _gerar_pedaco_mp3(pedaco, caminho_pedaco, voz)
                caminhos_pedacos.append(caminho_pedaco)
            except Exception as e:
                print(f"   ⚠️  Falhou o pedaço {i}: {e}. Pulando.")

        if not caminhos_pedacos:
            raise RuntimeError("Nenhum pedaço de áudio foi gerado com sucesso.")

        print(f"🔗 Juntando {len(caminhos_pedacos)} pedaço(s) em um único MP3...")
        if callback:
            callback(92, "Finalizando áudio...")
        
        _concatenar_mp3s(caminhos_pedacos, caminho_saida)
        
        if callback:
            callback(98, "Salvando arquivo...")


def gerar_audio_de_blocos(blocos: list, caminho_saida: str, voz: str = VOZ_PADRAO, callback=None):
    """
    Função principal: recebe blocos, monta roteiro, gera áudio.
    
    callback: função(progresso_pct, mensagem) para relatar progresso
    """
    if not blocos:
        raise ValueError("Lista de blocos está vazia.")

    print("📝 Montando roteiro...")
    if callback:
        callback(2, "Montando roteiro...")
    
    roteiro = montar_roteiro(blocos)

    # Salva o roteiro em texto pra revisão/debug
    caminho_roteiro = os.path.splitext(caminho_saida)[0] + "_roteiro.txt"
    with open(caminho_roteiro, "w", encoding="utf-8") as f:
        f.write(roteiro)
    print(f"📄 Roteiro salvo em '{caminho_roteiro}' (pra você conferir)")

    print(f"📏 Tamanho do roteiro: {len(roteiro)} caracteres")

    asyncio.run(_gerar_audio_longo(roteiro, caminho_saida, voz, callback))
    print(f"✅ Áudio salvo em '{caminho_saida}'")


# --- Teste rápido ---
if __name__ == "__main__":
    from extrair import extrair_conteudo

    caminho_entrada = "teste.pdf"  # troque conforme o arquivo

    if not os.path.exists(caminho_entrada):
        print(f"❌ Arquivo '{caminho_entrada}' não encontrado.")
    else:
        print(f"📂 Lendo '{caminho_entrada}'...")
        blocos = extrair_conteudo(caminho_entrada)
        print(f"   {len(blocos)} blocos encontrados.\n")

        gerar_audio_de_blocos(blocos, caminho_saida="teste.mp3")
        print("\n🎉 Pronto! Abra 'teste.mp3' pra ouvir.")