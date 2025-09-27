FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer puerto del servidor
EXPOSE 8080

# Comando por defecto (puede ser sobreescrito)
CMD ["python", "servidor.py"]