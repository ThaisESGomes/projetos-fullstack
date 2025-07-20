# Projetos Fullstack

Este repositório contém três projetos fullstack elaborados, cada um demonstrando diferentes tecnologias e funcionalidades:

## 🛒 TechShop - E-commerce de Tecnologia

Uma plataforma completa de e-commerce especializada em produtos de tecnologia.

### Funcionalidades
- **Autenticação completa**: Registro, login, logout com JWT
- **Catálogo de produtos**: Listagem com filtros por categoria, preço e busca
- **Carrinho de compras**: Adicionar/remover produtos, atualizar quantidades
- **Sistema de avaliações**: Usuários podem avaliar produtos (1-5 estrelas)
- **Processo de checkout**: Simulação completa de compra
- **Painel administrativo**: Gerenciamento de produtos e pedidos

### Tecnologias
- **Backend**: Python Flask, SQLAlchemy, JWT, Flask-CORS
- **Frontend**: React 18, Tailwind CSS, shadcn/ui, React Router
- **Banco de dados**: SQLite
- **Autenticação**: JWT (JSON Web Tokens)

### Como executar
```bash
# Backend
cd techshop-ecommerce/techshop-backend
source venv/bin/activate
python src/main.py

# Frontend
cd techshop-ecommerce/techshop-frontend
pnpm install
pnpm run dev
```

---

## 🌐 DevConnect - Rede Social para Desenvolvedores

Uma rede social simplificada focada na comunidade de desenvolvedores.

### Funcionalidades
- **Perfis personalizados**: Informações profissionais, habilidades, links
- **Publicações**: Posts de texto e blocos de código com syntax highlighting
- **Interações sociais**: Curtir, comentar, seguir outros usuários
- **Feed personalizado**: Visualização de posts de usuários seguidos
- **Sistema de tags**: Organização de conteúdo por tecnologias

### Tecnologias
- **Backend**: Python Flask, SQLAlchemy
- **Frontend**: React, Context API para estado global
- **Banco de dados**: SQLite
- **Autenticação**: JWT

### Como executar
```bash
# Backend
cd devconnect-social/devconnect-backend
source venv/bin/activate
python src/main.py

# Frontend
cd devconnect-social/devconnect-frontend
pnpm install
pnpm run dev
```

---

## ✅ TaskFlow - Gerenciador de Produtividade

Uma aplicação completa para gerenciamento de tarefas e projetos.

### Funcionalidades
- **Gerenciamento de tarefas**: Criar, editar, excluir, marcar como concluída
- **Organização avançada**: Categorias, tags, prioridades, datas de vencimento
- **Colaboração**: Compartilhar listas de tarefas com outros usuários
- **Notificações**: Lembretes de tarefas próximas ao vencimento
- **Dashboard**: Visão geral do progresso e estatísticas
- **Filtros inteligentes**: Por status, prioridade, data, categoria

### Tecnologias
- **Backend**: Python Flask, SQLAlchemy
- **Frontend**: React, Material-UI inspired design
- **Banco de dados**: SQLite
- **Notificações**: Sistema de lembretes integrado

### Como executar
```bash
# Backend
cd taskflow-productivity/taskflow-backend
source venv/bin/activate
python src/main.py

# Frontend
cd taskflow-productivity/taskflow-frontend
pnpm install
pnpm run dev
```

---

## 🚀 Características Gerais dos Projetos

### Arquitetura
- **Separação clara**: Frontend e backend independentes
- **API RESTful**: Comunicação via JSON
- **CORS configurado**: Permite integração frontend-backend
- **Autenticação segura**: JWT com expiração
- **Validação de dados**: Tanto no frontend quanto no backend

### Qualidade do Código
- **Estrutura organizada**: Separação de responsabilidades
- **Tratamento de erros**: Feedback adequado ao usuário
- **Responsividade**: Interfaces adaptáveis a diferentes dispositivos
- **Componentes reutilizáveis**: Código modular e maintível

### Segurança
- **Senhas criptografadas**: Hash seguro com Werkzeug
- **Tokens JWT**: Autenticação stateless
- **Validação de entrada**: Prevenção de ataques básicos
- **CORS configurado**: Controle de acesso de origem

---

## 📋 Requisitos do Sistema

### Backend
- Python 3.8+
- Flask 3.0+
- SQLAlchemy
- Werkzeug (para hash de senhas)
- PyJWT (para autenticação)
- Flask-CORS

### Frontend
- Node.js 18+
- React 18+
- Vite (bundler)
- Tailwind CSS
- shadcn/ui components
- React Router DOM

---

## 🛠️ Instalação Geral

1. **Clone o repositório**
```bash
git clone https://github.com/ThaisESGomes/projetos-fullstack.git
cd projetos-fullstack
```

2. **Escolha um projeto e siga as instruções específicas acima**

3. **Configuração do ambiente**
   - Certifique-se de ter Python 3.8+ e Node.js 18+ instalados
   - Cada projeto tem seu próprio ambiente virtual Python
   - Os frontends usam pnpm como gerenciador de pacotes

---

## 📝 Notas de Desenvolvimento

- **Banco de dados**: Todos os projetos usam SQLite para simplicidade, mas podem ser facilmente migrados para PostgreSQL ou MySQL
- **Deploy**: Os projetos estão preparados para deploy em plataformas como Heroku, Vercel, ou servidores VPS
- **Escalabilidade**: A arquitetura permite fácil escalabilidade horizontal
- **Manutenibilidade**: Código bem documentado e estruturado para facilitar manutenção

---

## 🎯 Objetivos dos Projetos

Estes projetos foram desenvolvidos para demonstrar:

1. **Competência fullstack**: Domínio tanto de frontend quanto backend
2. **Diferentes domínios**: E-commerce, redes sociais, produtividade
3. **Tecnologias modernas**: React, Flask, JWT, Tailwind CSS
4. **Boas práticas**: Arquitetura limpa, segurança, UX/UI
5. **Funcionalidades completas**: Desde autenticação até features avançadas

Cada projeto é funcional e pode ser usado como base para aplicações reais em produção.

---

**Desenvolvido por Thaís Gomes** | [GitHub](https://github.com/ThaisESGomes)

