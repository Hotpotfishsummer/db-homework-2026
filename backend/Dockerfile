FROM mambaorg/micromamba:1.5.10

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY --chown=$MAMBA_USER:$MAMBA_USER backend/environment.yml /tmp/environment.yml
RUN micromamba env create -f /tmp/environment.yml \
    && micromamba clean --all --yes

COPY --chown=$MAMBA_USER:$MAMBA_USER backend /app/backend
COPY --chown=$MAMBA_USER:$MAMBA_USER db /app/db
RUN sed -i 's/\r$//' /app/backend/entrypoint.sh || true

ENTRYPOINT ["micromamba", "run", "-n", "l-wardrobe", "/bin/bash", "/app/backend/entrypoint.sh"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "backend/main.py", "--host", "0.0.0.0", "--port", "8000"]
