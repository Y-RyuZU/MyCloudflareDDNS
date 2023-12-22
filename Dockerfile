FROM python:latest
LABEL authors="ryuzu"

RUN pip install requests

# アプリケーションのコピー
COPY . /app

# 実行コマンドの指定
CMD ["python", "/app/ddns.py"]