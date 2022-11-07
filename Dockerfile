FROM python:3.10
RUN python -m venv /opt/venv
COPY ./application /opt/application
COPY pyproject.toml /opt
WORKDIR /opt
RUN /opt/venv/bin/pip install -U pip poetry
RUN /opt/venv/bin/poetry install
RUN /opt/venv/bin/pip install aiosqlite
RUN /opt/venv/bin/pip install -e .