# Jupyter для ноутбуков курса: Python, драйвер PostgreSQL и pandas для вывода таблиц.
FROM python:3.12-slim
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
# В /work монтируется папка репозитория: ноутбуки сохраняются на вашем компьютере.
WORKDIR /work
# Токен и пароль отключены: Jupyter доступен только с этого компьютера (см. ports в compose).
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", \
     "--IdentityProvider.token=", "--ServerApp.password="]
