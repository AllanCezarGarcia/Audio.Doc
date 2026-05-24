"""
Fase 2: Descreve imagens usando o Gemini (SDK novo, gratuito).
Com retry automático, controle de rate limit e tratamento de erros amigável.
"""
import os
import re
import time
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from PIL import Image

# Carrega a chave do arquivo .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "❌ GEMINI_API_KEY não encontrada. "
        "Verifique se o arquivo .env existe e contém a chave."
    )

client = genai.Client(api_key=api_key)

# Modelo gratuito com cota diária mais generosa (~250/dia vs 20/dia do flash)
# Pode trocar para "gemini-2.5-flash" se quiser qualidade ligeiramente superior.
MODELO = "gemini-2.5-flash-lite"

# Pausa mínima entre chamadas, pra respeitar limite por minuto
PAUSA_ENTRE_CHAMADAS = 4.0  # segundos

# Máximo de tentativas em caso de erro transitório
MAX_TENTATIVAS = 3

# Marcador interno que sinaliza erro (será tratado pelo gerar_audio)
PREFIXO_ERRO = "__ERRO_DESCRICAO__"

# Controle de tempo entre chamadas (variável global pra rastrear última chamada)
_ultima_chamada = 0.0


PROMPT_DESCRICAO = """
Você descreve imagens para pessoas cegas que ouvirão o resultado em áudio.
Sua descrição será lida por um sintetizador de voz, então deve soar como uma narração natural.

REGRAS CRÍTICAS — siga TODAS:

1. PROIBIDO usar qualquer formatação: nada de asteriscos, hashtags, traços iniciais, marcadores de lista, negrito, itálico, ou caracteres como * # - _ ` ~.

2. PROIBIDO usar listas com marcadores. Em vez disso, use frases corridas separadas por ponto final.

3. Se for uma TABELA, narre como um locutor faria, em prosa contínua. Exemplo de tom:
   "Tabela com o título tal. Possui três colunas: coluna um, coluna dois, coluna três.
    Primeira linha: na coluna tipo de camada, valor entrada. Na coluna descrição, valor 32 por 32 por 3.
    Segunda linha: na coluna tipo de camada, valor CONV..."

4. Se for um GRÁFICO, descreva o tipo (barras, linhas, pizza), os eixos e as principais tendências, em prosa.

5. Se for uma FOTO ou ILUSTRAÇÃO, descreva o que aparece, cores relevantes e contexto, em prosa.

6. Se houver TEXTO na imagem, transcreva o texto fielmente integrado à narração.

7. Use português brasileiro natural e fluido. Pontuação correta (vírgulas e pontos), pois ela controla as pausas do áudio.

8. NÃO comece com "A imagem mostra". Varie a abertura.

Comece a descrição agora, em texto corrido, sem nenhuma formatação.
""".strip()


def limpar_markdown(texto: str) -> str:
    """Remove markdown que tenha escapado do prompt."""
    texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto)
    texto = re.sub(r"__(.+?)__", r"\1", texto)
    texto = re.sub(r"\*(.+?)\*", r"\1", texto)
    texto = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", texto)
    texto = re.sub(r"`(.+?)`", r"\1", texto)
    texto = re.sub(r"^#{1,6}\s*", "", texto, flags=re.MULTILINE)
    texto = re.sub(r"^\s*[\*\-\+]\s+", "", texto, flags=re.MULTILINE)
    texto = re.sub(r"^\s*\d+[\.\)]\s+", "", texto, flags=re.MULTILINE)
    texto = texto.replace("*", "").replace("`", "")
    texto = re.sub(r"\n{2,}", "\n", texto)
    texto = re.sub(r" {2,}", " ", texto)
    return texto.strip()


def _esperar_se_necessario():
    """Garante a pausa mínima entre chamadas pra respeitar rate limit por minuto."""
    global _ultima_chamada
    agora = time.time()
    tempo_passado = agora - _ultima_chamada
    if tempo_passado < PAUSA_ENTRE_CHAMADAS:
        time.sleep(PAUSA_ENTRE_CHAMADAS - tempo_passado)
    _ultima_chamada = time.time()


def descrever_imagem(caminho_imagem: str) -> str:
    """
    Recebe o caminho de uma imagem e devolve uma descrição em português,
    pronta pra ser lida em voz alta.

    Em caso de erro, devolve uma string que COMEÇA com PREFIXO_ERRO.
    Isso permite que o chamador (gerar_audio.py) detecte e use uma mensagem
    amigável em vez de colocar o erro técnico no áudio.
    """
    try:
        imagem = Image.open(caminho_imagem)
    except Exception as e:
        return f"{PREFIXO_ERRO}arquivo_invalido|{e}"

    ultima_excecao = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        _esperar_se_necessario()
        try:
            resposta = client.models.generate_content(
                model=MODELO,
                contents=[PROMPT_DESCRICAO, imagem],
            )
            texto = resposta.text
            if texto:
                return limpar_markdown(texto)
            return f"{PREFIXO_ERRO}resposta_vazia|"

        except genai_errors.APIError as e:
            ultima_excecao = e
            mensagem = str(e).lower()

            # Cota diária esgotada — não adianta tentar de novo
            if "429" in str(e) and "perday" in mensagem.replace(" ", ""):
                return f"{PREFIXO_ERRO}cota_diaria|"

            # Rate limit por minuto — espera mais e tenta de novo
            if "429" in str(e):
                espera = 35 if tentativa == 1 else 60
                print(f"   ⏳ Rate limit atingido. Aguardando {espera}s e tentando novamente ({tentativa}/{MAX_TENTATIVAS})...")
                time.sleep(espera)
                continue

            # Outros erros — espera curta e tenta de novo
            print(f"   ⚠️  Erro temporário (tentativa {tentativa}/{MAX_TENTATIVAS}): {e}")
            time.sleep(2 * tentativa)

        except Exception as e:
            ultima_excecao = e
            print(f"   ⚠️  Erro inesperado (tentativa {tentativa}/{MAX_TENTATIVAS}): {e}")
            time.sleep(2 * tentativa)

    return f"{PREFIXO_ERRO}falhou_todas_tentativas|{ultima_excecao}"


# --- Teste rápido ---
if __name__ == "__main__":
    caminho_teste = "saida_imagens/img_1.png"

    if not os.path.exists(caminho_teste):
        print(f"❌ Imagem '{caminho_teste}' não encontrada.")
    else:
        print(f"🔍 Descrevendo '{caminho_teste}' com modelo '{MODELO}'...\n")
        descricao = descrever_imagem(caminho_teste)
        print("=" * 60)
        if descricao.startswith(PREFIXO_ERRO):
            tipo = descricao.replace(PREFIXO_ERRO, "").split("|")[0]
            print(f"❌ Erro: {tipo}")
        else:
            print(descricao)
        print("=" * 60)