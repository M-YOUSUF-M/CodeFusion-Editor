# Linux Build

FROM python:3.12.2 AS linux

WORKDIR /app

ADD ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt && \
    pip install pyinstaller

ADD . /app

RUN pyinstaller \
    --onefile \
    --name codefusion-linux \
    --add-data ".env:." \
    --add-data "icon.ico:." \
    --add-data "styles/*:styles/" \
    --add-data ".prompt_train/*:.prompt_train/" \
    editor.py

# Windows Build

FROM batonogov/pyinstaller-windows AS windows

WORKDIR /app

ADD ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt && \
    pip install pyinstaller

ADD . /app

RUN pip install -r requirements.txt
RUN pyinstaller \
    --onefile \
    --name codefusion-windows \
    --add-data ".env:." \
    --add-data "icon.ico:." \
    --add-data "styles/*:styles/" \
    --add-data ".prompt_train/*:.prompt_train/" \
    editor.py

# Copy artifacts of all builds

FROM alpine AS final
COPY --from=linux /app/dist/* /output/
COPY --from=windows /app/dist/* /output/

CMD ["sh", "-c", "cp /output/* /dist/"]
