# Usa uma imagem oficial do Python que inclui o pip3
FROM python:3.13-slim

# Instala dependência do sistema para o Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-por && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask
EXPOSE 5000

# Comando pra rodar o app
CMD ["python3", "app.py"]