FROM apify/actor-python:3.13
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends tesseract-ocr \
    tesseract-ocr-eng tesseract-ocr-heb tesseract-ocr-ara tesseract-ocr-rus tesseract-ocr-deu \
    tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-ita tesseract-ocr-por tesseract-ocr-nld \
    tesseract-ocr-pol tesseract-ocr-tur tesseract-ocr-ukr \
 && rm -rf /var/lib/apt/lists/*
USER myuser
COPY --chown=myuser:myuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=myuser:myuser . ./
RUN python -m compileall -q src/
CMD ["python3", "-m", "src"]
