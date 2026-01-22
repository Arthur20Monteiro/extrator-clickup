import os
import io
import requests
from flask import Flask, request, render_template, send_file
from PIL import Image
import pytesseract

app = Flask(__name__)

# Caminho do Tesseract (se necessário para uso local)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

TXT_FILE = 'registros.txt'
HEADER = 'DataNascimento,Livro,Folhas,Termo,NomePai,NomeMae,NomeRegistrado,DataRegistro\n'

# Cria o arquivo TXT se ele não existir (evita erro FileNotFound)
if not os.path.exists(TXT_FILE):
    with open(TXT_FILE, 'w', encoding='utf-8') as f:
        f.write(HEADER)

# Informações do ClickUp
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN') or 'COLE_SEU_TOKEN_AQUI'
DOC_ID = 'doc:2ky5fut1-833'  # Substitua pelo seu documento ClickUp

HEADERS = {
    'Authorization': CLICKUP_API_TOKEN,
    'Content-Type': 'application/json'
}

# =============================
# Atualiza documento no ClickUp
# =============================
def atualizar_documento_clickup(linhas):
    url = f'https://api.clickup.com/api/v2/doc/{DOC_ID}'

    try:
        r = requests.get(url, headers=HEADERS)
        conteudo_atual = ''
        if r.status_code == 200:
            conteudo_atual = r.json()['doc']['content']
        else:
            print('⚠️ Erro ao ler documento:', r.text)

        conteudo_novo = conteudo_atual + '\n' + ''.join(linhas)

        payload = {"content": conteudo_novo}
        r = requests.put(url, headers=HEADERS, json=payload)

        if r.status_code == 200:
            print('✅ Documento atualizado com sucesso no ClickUp!')
        else:
            print('❌ Erro ao atualizar documento:', r.text)
    except Exception as e:
        print('❌ Erro de conexão com ClickUp:', e)

# =============================
# Função para extrair informações
# =============================
def extrair_campo(texto, chave):
    for linha in texto.split('\n'):
        if chave.lower() in linha.lower():
            return linha.split(':')[-1].strip()
    return ''

# =============================
# Rotas do Flask
# =============================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    imagens = request.files.getlist('imagens')

    if not imagens:
        return 'Nenhuma imagem enviada.'

    linhas_geradas = []

    for img_file in imagens:
        image_bytes = img_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        texto = pytesseract.image_to_string(image, lang='por')

        linha = {
            'DataNascimento': extrair_campo(texto, 'nascimento'),
            'Livro': extrair_campo(texto, 'livro'),
            'Folhas': extrair_campo(texto, 'folhas'),
            'Termo': extrair_campo(texto, 'termo'),
            'NomePai': extrair_campo(texto, 'pai'),
            'NomeMae': extrair_campo(texto, 'mae'),
            'NomeRegistrado': extrair_campo(texto, 'nome'),
            'DataRegistro': extrair_campo(texto, 'registro')
        }

        csv_line = ','.join(linha.values()) + '\n'
        linhas_geradas.append(csv_line)

    with open(TXT_FILE, 'a', encoding='utf-8') as f:
        f.writelines(linhas_geradas)

    atualizar_documento_clickup(linhas_geradas)

    return f"{len(linhas_geradas)} imagem(ns) processada(s) e enviadas para o ClickUp com sucesso! <a href='/download'>Baixar TXT</a>"

@app.route('/download')
def download():
    return send_file(TXT_FILE, as_attachment=True)

# =============================
# Execução da aplicação
# =============================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)