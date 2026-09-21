#!/bin/sh
set -e

# Executa migrações do banco de dados ao iniciar o container
python manage.py migrate --noinput

exec "$@"
