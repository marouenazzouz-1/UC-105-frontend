FROM python:3.11-slim
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
EXPOSE 8501
 
# Azure App Service sets PORT env var; Streamlit uses --server.port
CMD ["sh", "-c", "streamlit run frontend.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false"]