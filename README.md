# 🛒 Plataforma de E-commerce

Projeto desenvolvido para a disciplina de **Laboratório de Engenharia de Software**.

O sistema consiste em uma plataforma de e-commerce, permitindo que clientes realizem compras online de forma segura, enquanto administradores gerenciam produtos, categorias, pedidos e demais recursos do sistema. O objetivo é desenvolver o backend utilizando uma arquitetura em camadas, aplicando conceitos de Engenharia de Software, Banco de Dados e desenvolvimento de APIs REST. Além da implementação das funcionalidades principais, o projeto busca aplicar boas práticas de organização de código, versionamento e testes automatizados.

## Funcionalidades

* Cadastro de usuários
* Login e autenticação
* Cadastro e gerenciamento de produtos
* Carrinho de compras
* Aplicação de cupons
* Criação de pedidos
* Processamento de pagamentos
* Controle de estoque

##  Requisitos

<a id="requisitos"></a>

- Python 3.12
- PostgreSQL (configurável via `.env` — veja `.env.example`)
- uv como gerenciador de dependências
<br>
<a id="tecnologias"></a>

<div align="center">

![Python](https://img.shields.io/badge/Python-0D6EFD?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0D6EFD?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-0D6EFD?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-0D6EFD?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-0D6EFD?style=for-the-badge&logo=alembic&logoColor=white)
![Git](https://img.shields.io/badge/Git-0D6EFD?style=for-the-badge&logo=git&logoColor=white)

</div>


## Estrutura do Projeto

```
ecommerce-es/
├── src/
│   ├── main.py                  # instancia o FastAPI e registra os routers
│   ├── core/
│   │   └── security.py          # hashing de senha (bcrypt)
│   ├── database/
│   │   ├── base.py              # Base declarativa do SQLAlchemy
│   │   ├── idmixin.py           # mixin do id: UUID (PK) compartilhado
│   │   └── session.py           # engine async + get_db (transação por request)
│   └── modules/
│       ├── users/               # usuários
│       ├── auth/                # autenticação (JWT)
│       ├── categories/          # categorias de produto
│       ├── products/            # produtos
│       ├── inventories/         # estoque 
│       ├── coupons/             # cupons de desconto
│       ├── addresses/           # endereços do usuário
│       ├── carts/               # carrinho + checkout
│       ├── cart_items/          # itens do carrinho
│       ├── orders/              # pedidos 
│       ├── order_items/         # itens do pedido (snapshot de preço)
│       └── payments/            # pagamentos + gateway + webhook
├── alembic/
│   ├── env.py                   
│   └── versions/                # migrations (cadeia linear)
├── tests/
│   ├── conftest.py              # fixtures (banco temporário, repositories)
│   └── <módulo>/{unit,api,integration}/
├── docs/                        # diagramas (DER, casos de uso) 
├── .github/workflows/ci-pipeline.yaml
├── pyproject.toml
└── .env.example
```

## Arquitetura em Camadas

O sistema segue uma **arquitetura em camadas** com separação
clara entre domínio e persistência.

```
┌──────────────────────────────────────────────────────┐
│  Cliente (Swagger / frontend / outro serviço)        │
└───────────────────────────┬──────────────────────────┘
                            │ HTTP (JSON)
┌───────────────────────────▼─────────────────────────┐
│  ROUTER         → endpoints, injeção de dependência │
│  SCHEMAS (DTO)   → validação de entrada/saída       │
├─────────────────────────────────────────────────────┤
│  SERVICE          → regras de negócio               │
│  ENTITY           → objeto de domínio               │
├─────────────────────────────────────────────────────┤
│  REPOSITORY        → acesso a dados                 │
│  MAPPER            → entity ↔ model ↔ schema        │
│  MODEL             → tabela (SQLAlchemy)            │
└───────────────────────────┬─────────────────────────┘
                            │ SQL
┌───────────────────────────▼──────────────────────────┐
│  PostgreSQL                                          │
└──────────────────────────────────────────────────────┘
```
## Diagrama Entidade-Relacionamento

<p align="center">
<img src="docs/DER ecommerce.drawio.png" width="950">
</p> 

## Regras de Negócio

* Apenas usuários autenticados podem realizar compras.
* Cupons somente podem ser utilizados enquanto estiverem ativos e dentro da validade.
* O sistema impede que dois usuários adquiram simultaneamente a última unidade disponível de um produto.
* Após a confirmação do pagamento, o pedido não poderá mais ser alterado.


## Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/ecommerce-es.git
```

### 2. Entrar na pasta

```bash
cd ecommerce-es
```

### 3. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 4. Ativar o ambiente virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

### 5. Instalar as dependências
```bash
pip install -e .
pip install uv      # ou: uv sync
```

### 6. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Configure as credenciais do banco PostgreSQL antes de iniciar a aplicação.

### 7. Executar as migrações

```bash
alembic upgrade head
```

### 8. Iniciar a aplicação

```bash
uvicorn src.main:app --reload
```

API disponível: **http://127.0.0.1:8000/docs**

##  Testes

Para executar os testes automatizados:

```bash
pytest
```

| Pasta | Marcador | Testa |
|-------|----------|-------|
| `tests/<m>/unit/` | `unit` | services e schemas com `AsyncMock` | 
| `tests/<m>/api/` | `api` | routers via `TestClient` (service mockado) | 
| `tests/<m>/integration/` | `integration` | repositories contra Postgres real |

## Integrantes

<div align="center">

| Nome         | GitHub                                                                                                                                  |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Luana Souza  | [![GitHub](https://img.shields.io/badge/GitHub-111217?style=flat-square\&logo=github\&logoColor=white)](https://github.com/luanaapms)   |
| Ygor Pereira | [![GitHub](https://img.shields.io/badge/GitHub-111217?style=flat-square\&logo=github\&logoColor=white)](https://github.com/YgorPereira) |

</div>
