FROM registry.access.redhat.com/ubi8/python-39 as builder
WORKDIR /app

USER root

RUN pip install --upgrade setuptools pip

RUN python -mvenv venv && ./venv/bin/pip install --no-cache-dir --upgrade pip
RUN ./venv/bin/pip install --upgrade setuptools pip

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN ./venv/bin/pip install torch --extra-index-url https://download.pytorch.org/whl/cpu

RUN ./venv/bin/pip install "argostranslate @ git+https://github.com/TommiNieminen/argos-translate.git@master"
RUN ./venv/bin/pip install "argos-translate-files @ git+https://github.com/TommiNieminen/argos-translate-files.git@main"

COPY . .

# unzip models, the zip is included in the repo as LFS objects
RUN unzip ./models.zip -d models

# Install package from source code, compile translations
RUN ./venv/bin/pip install Babel==2.12.1 && ./venv/bin/python scripts/compile_locales.py && ./venv/bin/pip install .

FROM registry.access.redhat.com/ubi8/python-39

RUN pip install --upgrade setuptools pip

ARG with_models=false
ARG models=""

#RUN addgroup --system --gid 1032 libretranslate && adduser --system --uid 1032 libretranslate && mkdir -p /home/libretranslate/.local && chown -R libretranslate:libretranslate /home/libretranslate/.local
USER root
#RUN adduser --system --uid 1032 libretranslate && mkdir -p /home/libretranslate/.local && chown -R 1032:0 /home/libretranslate/.local

RUN mkdir -p /opt/app-root/src/.local && chown -R 1032:0 /opt/app-root/src/.local

RUN chgrp -R 0 /opt/app-root/src/.local && \
    chmod -R g=u /opt/app-root/src/.local


COPY --from=builder --chown=1032:0 /app /app
RUN chgrp -R 0 /app && \
    chmod -R g=u /app

WORKDIR /app

RUN if [ "$with_models" = "true" ]; then  \
  # initialize the language models
  if [ ! -z "$models" ]; then \
  ./venv/bin/python scripts/install_models.py --load_only_lang_codes "$models";   \
  else \
  ./venv/bin/python scripts/install_models.py;  \
  fi \
  fi

EXPOSE 5000
ENTRYPOINT [ "./venv/bin/libretranslate", "--host", "0.0.0.0", "--char-limit=10000" ]
