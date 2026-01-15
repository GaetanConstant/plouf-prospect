FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /plouf-prospect

# Installer les dépendances à partir du fichier requirements.txt
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers nécessaires de l'application
COPY dev.py app.py
COPY config.yaml config.yaml
COPY crm_scopa.csv crm_scopa.csv
COPY .streamlit/config.toml .streamlit/config.toml

# Exposer le port utilisé par Streamlit
EXPOSE 4202

# Healthcheck pour vérifier si l'application est active
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl --fail http://localhost:4202/_stcore/health || exit 1

# Lancer l'application
CMD ["streamlit", "run", "app.py", "--server.port=4202", "--server.address=0.0.0.0"]
