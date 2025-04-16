FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Agrega Rust y herramientas necesarias
RUN apt-get update && apt-get install -y curl build-essential && curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "vista:app", "--host", "0.0.0.0", "--port", "8000"]
