# Projetos Fullstack

Laboratórios de desenvolvimento web em diferentes estágios. O objetivo é estudar APIs, interfaces, persistência e controles de acesso.

| Projeto | Implementado no repositório | Próximos passos |
|---|---|---|
| [TechShop](techshop-ecommerce) | API Flask para usuários, catálogo, avaliações, carrinho e pedidos simulados; código de frontend React/Vite | Validar interface completa, ampliar testes e revisar regras de negócio |
| [DevConnect](devconnect-social) | API Flask de cadastro, consulta, alteração e exclusão de usuários | Autenticação individual, posts, feed e frontend próprio |
| [TaskFlow](taskflow-productivity) | API Flask de usuários | Modelos e rotas de tarefas, projetos, colaboração e frontend próprio |

DevConnect e TaskFlow são protótipos de API; seus nomes representam o domínio planejado. Não possuem os frontends React descritos em versões anteriores deste README.

## Executar um backend

Requer Python 3.11+. Exemplo para TechShop, partindo da raiz:

```bash
git clone https://github.com/ThaisESGomes/projetos-fullstack.git
cd projetos-fullstack/techshop-ecommerce/techshop-backend
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python src/main.py
```

No PowerShell, configure a variável com `$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"`.

A API local usa `http://127.0.0.1:5000/api`. O banco SQLite é criado quando necessário. `DATABASE_URL` permite usar um banco descartável, por exemplo `sqlite:///:memory:` para testes. Não use os bancos versionados com dados reais.

Para DevConnect ou TaskFlow, entre na pasta correspondente do backend e repita a instalação. Configure também `ADMIN_API_TOKEN` com pelo menos 32 caracteres e envie `Authorization: Bearer <token>` nas chamadas `/api/`. Esse token compartilhado protege o laboratório; autenticação individual ainda precisa ser implementada.

## Frontend TechShop

```bash
cd techshop-ecommerce/techshop-frontend
pnpm install
pnpm run dev
```

Execute a partir da raiz do repositório em outro terminal. O backend permite por padrão a origem `http://localhost:5173`; ajuste `CORS_ORIGINS` para a origem usada. Ainda é necessário validar todos os fluxos da interface.

## Controles e limites de segurança

- Chave de assinatura configurada pelo ambiente, sem chave fixa no código.
- Rotas de administração de usuários no TechShop exigem JWT válido e perfil administrador.
- Contas desativadas não acessam rotas protegidas.
- Criação administrativa de usuário exige senha explícita.
- Quantidades de carrinho devem ser inteiros positivos.
- Debug desligado por padrão e servidor local em `127.0.0.1`.

Não há garantia de uso em produção: faltam rate limiting, revisão completa de validações, tratamento uniforme de erros, auditoria de dependências e testes completos da interface. Pedidos são simulações sem processamento real de pagamento.

## Testes

Na pasta de cada backend:

```bash
python -m unittest discover -s tests -v
```

Consulte também [o estudo de caso](docs/security-improvements.md) sobre as correções e suas limitações.
