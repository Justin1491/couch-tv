FROM node:24-bookworm-slim AS remote
WORKDIR /src/remote
COPY remote/package.json remote/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY remote/ ./
RUN npm run build

FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    COUCH_CONFIG=/config/config.json COUCH_DATA=/data \
    HOME=/tmp PORT=5400 ADB_KEY=/data/adbkey
WORKDIR /app
COPY bridge/requirements.txt ./bridge/requirements.txt
RUN pip install --no-cache-dir -r bridge/requirements.txt \
    && groupadd --gid 10001 couch \
    && useradd --uid 10001 --gid couch --no-create-home couch \
    && mkdir /config /data && chown couch:couch /config /data
COPY bridge/ ./bridge/
COPY tv-home/web/ ./tv-home/web/
COPY config.example.json ./config.example.json
COPY --from=remote /src/remote/dist ./remote/dist/
USER 10001:10001
EXPOSE 5400
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://'+os.getenv('BIND_HOST','127.0.0.1')+':'+os.getenv('PORT','5400')+'/api/health',timeout=3).close()" || exit 1
CMD ["python", "bridge/container_start.py"]
