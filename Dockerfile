# Imagem base leve com Python
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements primeiro (aproveita cache de camadas do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código-fonte
COPY app.py .

# Expõe a porta usada pela aplicação Flask
EXPOSE 5000

# Variáveis de ambiente básicas
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Comando padrão de inicialização
CMD ["python", "app.py"]
