#!/bin/sh
set -e

# Garante que os arquivos estáticos (logos, css, js) estão coletados na pasta staticfiles
python manage.py collectstatic --noinput

# Executa migrações do banco de dados ao iniciar o container
python manage.py migrate --noinput

# Configura/atualiza automaticamente as contas de diretoria e restaura desbravadores se vazio
python manage.py setup_diretoria

# Sincroniza fotos locais com o Cloudinary se configurado
python manage.py upload_to_cloudinary || true

exec "$@"
