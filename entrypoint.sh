#!/bin/sh
set -e

# Executa migrações do banco de dados ao iniciar o container
python manage.py migrate --noinput

# Configura/atualiza automaticamente as contas de diretoria
python manage.py setup_diretoria

exec "$@"
