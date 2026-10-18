FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN rm -f /etc/apt/sources.list.d/yarn.list

COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /usr/local/bin/
