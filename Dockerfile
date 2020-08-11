FROM python:3.8.5-slim
WORKDIR /project
ADD chess_engine.py main.py requirements.txt stockfish_20011801_x64 /project/
RUN pip install -r requirements.txt
CMD gunicorn -b :$PORT main:app