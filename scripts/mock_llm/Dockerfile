FROM python:3.11-slim
WORKDIR /srv
RUN pip install --no-cache-dir flask gunicorn
COPY scripts/mock_llm/app.py /srv/app.py
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]