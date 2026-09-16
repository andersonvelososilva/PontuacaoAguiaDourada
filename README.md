# 🏆 Sistema Web de Pontuação do Clube de Desbravadores

Aplicação web responsiva, simples e eficiente desenvolvida em **Python** e **Django** para consulta pública de pontuação dos desbravadores e gestão administrativa do clube.

---

## 📌 1. O que é o Projeto?

O **Sistema Web de Pontuação do Clube de Desbravadores** permite que os desbravadores acompanhem em tempo real a sua pontuação acumulada e o seu extrato de pontos pelo celular ou computador.

### Principais Recursos:
- **Consulta Pública Instantânea**: Busca rápida por nome ou filtro por unidade.
- **Extrato Detalhado de Pontos**: Transparência de onde veio cada ponto (+ para presenças/especialidades, - para atrasos/indiscipilina).
- **Cálculo de Pontuação 100% Derivado**: O total é calculado no backend através do histórico (`Sum('pontos')`), sem edições manuais arriscadas.
- **Preservação de Dados**: Desbravadores inativos deixam de aparecer na consulta pública sem apagar o histórico acumulado.
- **Painel Administrativo Completo**: Gerenciamento facilitado através do Django Admin nativo.
- **PWA (Progressive Web App)**: Suporte para instalação na tela inicial de celulares Android e iOS.

---

## 🛠️ 2. Tecnologias Utilizadas

- **Linguagem**: Python 3.10+
- **Framework Web**: Django 5.x
- **Banco de Dados**: SQLite (Desenvolvimento local) e PostgreSQL (Produção)
- **Servidor de Arquivos Estáticos**: WhiteNoise
- **Servidor WSGI**: Gunicorn
- **Interface**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript Vanilla leve (PWA & Filtro)
- **Gestão de Configurações**: Python Decouple & DJ-Database-URL

---

## 🚀 3. Como Executar o Projeto Localmente

Siga o passo a passo abaixo para rodar a aplicação em seu computador.

### Passo 1: Instalar o Python
Baixe e instale o Python (versão 3.10 ou superior) através do site oficial: [python.org](https://www.python.org/).  
Certifique-se de marcar a opção **"Add Python to PATH"** durante a instalação.

### Passo 2: Clonar ou Baixar o Repositório
```bash
git clone https://github.com/seu-usuario/pontuacao-desbravadores.git
cd pontuacao-desbravadores
```

### Passo 3: Criar e Ativar o Ambiente Virtual (`venv`)
No terminal (Windows):
```bash
python -m venv venv
.\venv\Scripts\activate
```

No Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 4: Instalar as Dependências
Com o ambiente virtual ativado, execute:
```bash
pip install -r requirements.txt
```

### Passo 5: Configurar as Variáveis de Ambiente (`.env`)
Copie o arquivo de exemplo `.env.example` para `.env`:

No Windows (CMD/PowerShell):
```powershell
copy .env.example .env
```
No Linux/macOS:
```bash
cp .env.example .env
```

O arquivo `.env` conterá:
```env
SECRET_KEY=django-insecure-chave-de-desenvolvimento-local-123
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
NOME_DO_CLUBE=Clube de Desbravadores Águias
EXIBIR_HISTORICO_PUBLICO=True
```

### Passo 6: Executar as Migrations do Banco de Dados
```bash
python manage.py migrate
```

### Passo 7: Popular Dados de Teste e Criar Usuário Admin
Para popular o banco com unidades, desbravadores de exemplo e criar um superusuário automático:
```bash
python manage.py popular_dados
```
> 🔑 **Credenciais do Usuário Administrativo Criado:**
> - **Usuário:** `admin`
> - **Senha:** `admin123`

*(Caso queira criar outro superusuário manualmente, use `python manage.py createsuperuser`)*

### Passo 8: Iniciar o Servidor de Desenvolvimento
```bash
python manage.py runserver
```

Acesse no seu navegador:
- **Página Pública de Consulta:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Ranking Geral:** [http://127.0.0.1:8000/ranking/](http://127.0.0.1:8000/ranking/)
- **Painel Administrativo:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## ⚙️ 4. Guia de Uso da Área Administrativa (`/admin/`)

1. Acesse `http://127.0.0.1:8000/admin/` e faça login com a conta de administrador.
2. **Cadastrar Unidades**:
   - Vá em **Unidades** → **Adicionar Unidade**.
   - Digite o nome da unidade (ex: *Águias*, *Falcões*) e clique em **Salvar**.
3. **Cadastrar Desbravadores**:
   - Vá em **Desbravadores** → **Adicionar Desbravador**.
   - Digite o nome completo, selecione a unidade e clique em **Salvar**.
4. **Registrar Pontuações**:
   - **Opção A (Direto no Desbravador)**: Ao editar um desbravador, utilize a seção de formulário inline no final da página para adicionar pontos.
   - **Opção B (Menu Pontuações)**: Vá em **Pontuações** → **Adicionar Pontuação**. Selecione o desbravador, informe a quantidade de pontos (ex: `10` para ganho ou `-5` para perda) e o motivo.
   - O campo "Registrado por" será preenchido automaticamente com seu usuário.

---

## ☁️ 5. Como Fazer Deploy Gratuito em Produção

O projeto está preparado para hospedagens gratuitas modernas (como **Render.com**, **Neon.tech**, **Railway** ou **Koyeb**).

### Opção Recomendada: Render.com + Neon.tech (PostgreSQL)

1. **Criar Banco PostgreSQL Gratuito no Neon.tech**:
   - Acesse [neon.tech](https://neon.tech/) e crie uma conta gratuita.
   - Crie um novo projeto e copie a `DATABASE_URL` fornecida.

2. **Hospedar a Aplicação no Render.com**:
   - Envie o código para o seu repositório no **GitHub**.
   - Acesse [render.com](https://render.com/) e crie um **New Web Service**.
   - Conecte ao seu repositório do GitHub.
   - Configure o ambiente:
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
     - **Start Command**: `gunicorn config.wsgi:application`
   - Adicione as **Variables of Environment**:
     - `SECRET_KEY`: uma chave forte aleatória.
     - `DEBUG`: `False`
     - `ALLOWED_HOSTS`: `seu-app.onrender.com`
     - `DATABASE_URL`: a URL do PostgreSQL copiada do Neon.tech.
     - `NOME_DO_CLUBE`: O nome do seu clube de desbravadores.
     - `EXIBIR_HISTORICO_PUBLICO`: `True` ou `False`

3. **Pronto!** O sistema estará no ar com HTTPS gratuito e PostgreSQL em nuvem.

---

## 🧪 6. Suíte de Testes Automatizados

Para rodar os testes unitários da aplicação e verificar a integridade do código:
```bash
python manage.py test
```

Os testes cobrem:
- Cadastro de unidades e desbravadores.
- Lançamento de pontuações positivas e negativas.
- Cálculo acumulado correto do total de pontos.
- Ocultação automática de desbravadores inativos na pesquisa.
- Proteção da rota do Django Admin.
- Funcionamento dos filtros de busca.

---

## 📝 Licença

Este projeto é desenvolvido para uso em **Clubes de Desbravadores**. Livre para uso, modificação e distribuição sem fins lucrativos.
