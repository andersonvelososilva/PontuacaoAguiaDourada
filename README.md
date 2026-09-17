# 🏆 Sistema Web de Pontuação do Clube de Desbravadores

Aplicação web responsiva, simples e extremamente segura desenvolvida em **Python** e **Django** para gestão administrativa da Diretoria e consulta de pontuação individual dos Desbravadores.

---

## 📌 1. O que é o Projeto?

O **Sistema Web de Pontuação do Clube de Desbravadores** permite que a diretoria gerencie a pontuação e os membros do clube, enquanto os desbravadores consultam de forma privativa e segura apenas o seu próprio extrato e perfil.

### Principais Recursos:
- **Perfil Privado do Desbravador (`/perfil/`)**: Acesso restrito via login ao próprio perfil com foto, unidade, pontuação total acumulada e extrato detalhado de lançamentos.
- **Segurança e Autorização no Backend**: Proteção no servidor impedindo que desbravadores acessem perfis alheios ou a área administrativa (`/admin/`).
- **Controle de Exibição Pública pela Diretoria**:
  - **Top 3**: Pode ser **Ativo** ou **Inativo**, com 4 Modos (*Nome+Foto+Pontos*, *Nome+Foto sem Pontos*, *Identidade Oculta com Pontos 🔒*, *Nome+Pontos sem Foto*).
  - **Ranking Geral**: Pode ser **Ativo** ou **Inativo**.
  - **Mensagem de Orientação**: Quando ambos estão desativados, a página pública omite dados no HTML e exibe o botão **[ENTRAR]**.
- **Cálculo Derivado Confiável**: Total acumulado via backend (`Sum('pontos')`).
- **Preservação do Histórico**: Desbravadores inativos deixam de figurar no Top 3/Ranking público, mantendo seu histórico salvo.
- **PWA (Progressive Web App)**: Suporte para instalação na tela inicial de celulares.

---

## 🛠️ 2. Tecnologias Utilizadas

- **Linguagem**: Python 3.10+
- **Framework Web**: Django 5.x
- **Banco de Dados**: SQLite (Desenvolvimento local) e PostgreSQL (Produção)
- **Imagens & Mídia**: Pillow
- **Servidor de Arquivos Estáticos**: WhiteNoise
- **Servidor WSGI**: Gunicorn
- **Interface**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript Vanilla
- **Gestão de Configurações**: Python Decouple & DJ-Database-URL

---

## 🚀 3. Como Executar o Projeto Localmente

### Passo 1: Ativar o Ambiente Virtual (`venv`)
No Windows:
```powershell
.\venv\Scripts\activate
```

### Passo 2: Executar as Migrations
```bash
python manage.py migrate
```

### Passo 3: Popular Dados de Teste
```bash
python manage.py popular_dados
```

> 🔑 **Contas de Teste Criadas Automaticamente:**
> - **Diretoria (Admin):** Usuário: `admin` | Senha: `admin123`
> - **Desbravador 1:** Usuário: `joao` | Senha: `senha123`
> - **Desbravador 2:** Usuário: `beatriz` | Senha: `senha123`

### Passo 4: Iniciar o Servidor
```bash
python manage.py runserver
```

Acesse no navegador:
- **Página Inicial Pública:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Login:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- **Meu Perfil Privado:** [http://127.0.0.1:8000/perfil/](http://127.0.0.1:8000/perfil/)
- **Painel Administrativo:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## ⚙️ 4. Guia de Gestão pela Diretoria (`/admin/`)

1. Acesse `http://127.0.0.1:8000/admin/` e faça login com a conta da diretoria.
2. **Controlar Top 3 e Ranking Público**:
   - Acesse **Configurações do Sistema**.
   - Alterne as opções **Exibir Ranking Publicamente**, **Exibir Top 3 Publicamente** e selecione o **Modo de Exibição do Top 3**.
3. **Cadastrar Desbravador com Conta de Acesso**:
   - Em **Usuários**, crie uma conta para o desbravador (ex: `marcos` / `senha123`).
   - Em **Desbravadores**, cadastre o membro, selecione a unidade, faça upload da foto (opcional) e vincule à conta de usuário criada.
4. **Lançar Pontos (+ ou -)**:
   - Acesse **Pontuações** ou utilize o formulário inline na própria página do desbravador. Informe os pontos (ex: `15` para presença/especialidade, `-5` para atraso) e a justificativa.

---

## 🧪 5. Suíte de Testes Automatizados

Para rodar a suíte completa de testes de autorização, permissões e modos de exibição:
```bash
python manage.py test
```

---

## ☁️ 6. Deploy Gratuito em Nuvem (Render.com + Neon.tech)

1. Suba o projeto para o seu repositório no **GitHub**.
2. No **Render.com**, crie um **Web Service** conectado ao repositório:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn config.wsgi:application`
3. Configure as variáveis de ambiente (`DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`).
