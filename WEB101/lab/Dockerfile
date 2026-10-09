FROM python:3.12-slim
WORKDIR /app
COPY app.py index.html ./
ENV HOST=0.0.0.0 PORT=8080 PYTHONUNBUFFERED=1
USER nobody
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/robots.txt')"
CMD ["python", "app.py"]
