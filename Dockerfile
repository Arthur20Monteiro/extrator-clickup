# Usa uma imagem oficial do Python que inclui o pip3
FROM python:3.13-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Instala as dependências do requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta 5000 (padrão Flask)
EXPOSE 5000

# Comando para rodar o app
CMD ["python3", "app.py"]