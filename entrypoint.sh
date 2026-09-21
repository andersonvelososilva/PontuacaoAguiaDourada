#!/bin/sh
set -e

# Executa migrações do banco de dados ao iniciar o container
python manage.py migrate --noinput

# Carrega os dados iniciais dos desbravadores se o banco for novo
python manage.py loaddata initial_data.json || true

exec "$@"
