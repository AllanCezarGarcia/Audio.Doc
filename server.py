"""
API Flask para AudioDoc — expõe os scripts Python como serviços REST.
Permite upload de documentos e conversão para áudio via interface web.
Com suporte a streaming de progresso em tempo real.
"""
import os
import tempfile
import threading
import json
from flask_cors import CORS
from queue import Queue
from flask import Flask, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from extrair import extrair_conteudo, FORMATOS_SUPORTADOS
from gerar_audio import gerar_audio_de_blocos

app = Flask(__name__, static_folder='.')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

PASTA_TEMP = tempfile.gettempdir()
PASTA_UPLOADS = os.path.join(os.getcwd(), 'uploads')
os.makedirs(PASTA_UPLOADS, exist_ok=True)

# Dicionário global para rastrear progresso de conversões
conversoes_em_progresso = {}
conversoes_lock = threading.Lock()


def is_allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [
        ext.lstrip('.') for ext in FORMATOS_SUPORTADOS
    ]


def callback_progresso(id_conversao, etapa, progresso, mensagem=""):
    """Callback para atualizar progresso de conversão em tempo real."""
    with conversoes_lock:
        if id_conversao not in conversoes_em_progresso:
            conversoes_em_progresso[id_conversao] = {}
        
        conversoes_em_progresso[id_conversao] = {
            'etapa': etapa,
            'progresso': progresso,
            'mensagem': mensagem,
            'status': 'processando'
        }


def processar_conversao(id_conversao, caminho_entrada, caminho_saida, voz, nome_saida):
    """Processa conversão em thread separada com feedback de progresso."""
    try:
        # Etapa 1: Extrair conteúdo
        callback_progresso(id_conversao, 'Extraindo conteúdo', 5, 'Lendo arquivo...')
        blocos = extrair_conteudo(caminho_entrada)
        print(f"✓ {len(blocos)} blocos extraídos")
        
        # Etapa 2: Gerar áudio
        callback_progresso(id_conversao, 'Gerando áudio', 15, f'Processando {len(blocos)} blocos...')
        gerar_audio_de_blocos(
            blocos, 
            caminho_saida=caminho_saida, 
            voz=voz,
            callback=lambda p, m: callback_progresso(id_conversao, 'Gerando áudio', 15 + (p * 0.8), m)
        )
        
        # Etapa 3: Finalizado
        callback_progresso(id_conversao, 'Concluído', 100, f'Áudio salvo: {nome_saida}')
        
        # Limpa arquivo de entrada
        if os.path.exists(caminho_entrada):
            os.remove(caminho_entrada)
        
        with conversoes_lock:
            conversoes_em_progresso[id_conversao]['status'] = 'concluido'
        
        print(f"✅ Conversão {id_conversao} concluída")
    
    except Exception as e:
        print(f"❌ Erro na conversão {id_conversao}: {e}")
        with conversoes_lock:
            conversoes_em_progresso[id_conversao].update({
                'status': 'erro',
                'mensagem': str(e)
            })


@app.route('/')
def index():
    """Serve a página HTML principal."""
    return send_file('index.html', mimetype='text/html')


@app.route('/api/info', methods=['GET'])
def info():
    """Retorna informações sobre formatos suportados e vozes disponíveis."""
    return jsonify({
        'app': 'AudioDoc',
        'formatos_suportados': list(FORMATOS_SUPORTADOS),
        'vozes': {
            'francisca': 'pt-BR-FranciscaNeural',
            'antonio': 'pt-BR-AntonioNeural',
            'thalita': 'pt-BR-ThalitaMultilingualNeural',
            'macerio': 'pt-BR-MacerioMultilingualNeural',
        }
    })


@app.route('/api/progresso/<id_conversao>', methods=['GET'])
def progresso(id_conversao):
    """
    SSE: Streaming de eventos de progresso.
    Mantém a conexão aberta e envia atualizações em tempo real.
    """
    def gerar_eventos():
        ultimo_progresso = -1
        while True:
            with conversoes_lock:
                info = conversoes_em_progresso.get(id_conversao)
            
            if not info:
                yield f"data: {json.dumps({'status': 'nao_encontrado'})}\n\n"
                break
            
            # Só envia se houver mudança de progresso
            if info.get('progresso', -1) != ultimo_progresso:
                ultimo_progresso = info.get('progresso', -1)
                evento = {
                    'progresso': info.get('progresso', 0),
                    'etapa': info.get('etapa', ''),
                    'mensagem': info.get('mensagem', ''),
                    'status': info.get('status', 'processando')
                }
                yield f"data: {json.dumps(evento)}\n\n"
            
            # Se terminou, sai do loop
            if info.get('status') in ['concluido', 'erro']:
                break
            
            # Aguarda um pouco antes de verificar novamente
            import time
            time.sleep(0.5)
    
    return Response(gerar_eventos(), mimetype='text/event-stream')


@app.route('/api/converter', methods=['POST'])
def converter():
    """
    Endpoint para converter documento em áudio com feedback de progresso.
    
    Params:
        - file: arquivo (PDF, DOCX, PPTX ou TXT)
        - voz: escolha de voz (francisca, antonio, thalita, macerio)
        - nome_saida: nome personalizado para o MP3 (opcional)
    """
    try:
        # Validações
        if 'file' not in request.files:
            return jsonify({'erro': 'Arquivo não fornecido'}), 400
        
        arquivo = request.files['file']
        if arquivo.filename == '':
            return jsonify({'erro': 'Arquivo vazio'}), 400
        
        if not is_allowed_file(arquivo.filename):
            formatos = ', '.join(FORMATOS_SUPORTADOS)
            return jsonify({'erro': f'Formato não suportado. Use: {formatos}'}), 400
        
        # Parâmetros opcionais
        voz = request.form.get('voz', 'francisca').lower()
        vozes_mapeadas = {
            'francisca': 'pt-BR-FranciscaNeural',
            'antonio': 'pt-BR-AntonioNeural',
            'thalita': 'pt-BR-ThalitaMultilingualNeural',
            'macerio': 'pt-BR-MacerioMultilingualNeural',
        }
        voz = vozes_mapeadas.get(voz, 'pt-BR-FranciscaNeural')
        
        # Salva arquivo temporário
        filename = secure_filename(arquivo.filename)
        caminho_entrada = os.path.join(PASTA_UPLOADS, filename)
        arquivo.save(caminho_entrada)
        
        # Nome do MP3 de saída
        nome_base = os.path.splitext(filename)[0]
        nome_saida = request.form.get('nome_saida', nome_base)
        if not nome_saida.lower().endswith('.mp3'):
            nome_saida += '.mp3'
        
        caminho_saida = os.path.join(PASTA_UPLOADS, nome_saida)
        
        # Gera ID único para esta conversão
        import uuid
        id_conversao = str(uuid.uuid4())[:8]
        
        # Inicia processamento em thread separada
        with conversoes_lock:
            conversoes_em_progresso[id_conversao] = {
                'etapa': 'Iniciando',
                'progresso': 0,
                'mensagem': 'Preparando conversão...',
                'status': 'processando'
            }
        
        thread = threading.Thread(
            target=processar_conversao,
            args=(id_conversao, caminho_entrada, caminho_saida, voz, nome_saida),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'sucesso': True,
            'id_conversao': id_conversao,
            'mensagem': 'Conversão iniciada! Acompanhe o progresso.',
            'arquivo_saida': nome_saida,
            'url_progresso': f'/api/progresso/{id_conversao}',
            'download_url': f'/api/download/{nome_saida}'
        })
    
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        return jsonify({'erro': str(e)}), 500


@app.route('/api/download/<nome_arquivo>', methods=['GET'])
def download(nome_arquivo):
    """Permite download do arquivo MP3 gerado."""
    try:
        # Validação de segurança: não permite .. ou /
        if '..' in nome_arquivo or '/' in nome_arquivo or '\\' in nome_arquivo:
            return jsonify({'erro': 'Caminho inválido'}), 400
        
        caminho = os.path.join(PASTA_UPLOADS, secure_filename(nome_arquivo))
        
        if not os.path.exists(caminho):
            return jsonify({'erro': 'Arquivo não encontrado'}), 404
        
        return send_file(
            caminho,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=nome_arquivo
        )
    
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return jsonify({'erro': str(e)}), 500


@app.route('/api/arquivos', methods=['GET'])
def listar_arquivos():
    """Lista os arquivos MP3 gerados."""
    try:
        arquivos = []
        if os.path.exists(PASTA_UPLOADS):
            for arquivo in os.listdir(PASTA_UPLOADS):
                if arquivo.endswith('.mp3'):
                    caminho = os.path.join(PASTA_UPLOADS, arquivo)
                    tamanho = os.path.getsize(caminho)
                    arquivos.append({
                        'nome': arquivo,
                        'tamanho': f'{tamanho / (1024*1024):.2f} MB',
                        'url': f'/api/download/{arquivo}'
                    })
        
        return jsonify({'arquivos': arquivos})
    
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        return jsonify({'erro': str(e)}), 500


@app.errorhandler(413)
def arquivo_grande(e):
    """Erro quando arquivo excede tamanho máximo."""
    return jsonify({'erro': 'Arquivo muito grande (máximo 100MB)'}), 413


if __name__ == '__main__':
    print("=" * 60)
    print("🎧 AudioDoc API — Iniciando servidor...")
    print("=" * 60)
    print("📍 Acesse: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
