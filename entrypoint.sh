#!/bin/sh
set -e

# Executa migrações do banco de dados ao iniciar o container
python manage.py migrate --noinput

# Configura/atualiza automaticamente as contas de diretoria e restaura desbravadores se vazio
python manage.py setup_diretoria

# Sincroniza fotos locais com o Cloudinary se configurado
python manage.py upload_to_cloudinary || true

exec "$@"
