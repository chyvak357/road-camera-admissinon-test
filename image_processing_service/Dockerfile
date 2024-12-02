FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN python -m venv venv && . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", ". venv/bin/activate && python main.py"]