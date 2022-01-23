FROM python:3

COPY . /app
WORKDIR /app

EXPOSE 8000

RUN pip install 'hypercorn'

RUN pip install -r /app/serwer/requirements.txt

HEALTHCHECK --interval=5s --timeout=5s --start-period=5s --retries=3 CMD curl --fail http://localhost:8000/healthcheck || exit 1

CMD ["hypercorn", "serwer.app:app", "--bind", "0.0.0.0:8000"]