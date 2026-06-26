# 🛒 Plataforma de E-commerce

Projeto desenvolvido para a disciplina de **Laboratório de Engenharia de Software**.

O sistema consiste em uma **API REST** para uma plataforma de e-commerce, permitindo que clientes realizem compras online de forma segura, enquanto administradores gerenciam produtos, categorias, pedidos e demais recursos do sistema.

---

# 📖 Sobre o Projeto

O objetivo deste projeto é desenvolver o backend de uma plataforma de e-commerce utilizando uma arquitetura em camadas, aplicando conceitos de Engenharia de Software, Banco de Dados e desenvolvimento de APIs REST. Além da implementação das funcionalidades principais, o projeto busca aplicar boas práticas de organização de código, versionamento e testes automatizados.
---

# 🚀 Tecnologias Utilizadas

* Python 3.12
* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* Pytest

---

# 📂 Estrutura do Projeto

```text
ecommerce-es/
│
├── alembic/
├── docs/
│   ├── DER ecommerce.drawio.png
│   └── Caso de Uso.drawio.png
│
├── src/
│   ├── database/
│   ├── routes/
│   ├── schemas/
│   └── utils/
│
├── tests/
│
├── .env.example
├── alembic.ini
├── pyproject.toml
└── README.md
```

---

# 🏛 Arquitetura

O projeto segue uma arquitetura em camadas, separando responsabilidades para facilitar manutenção, escalabilidade e testes.

```text
Cliente

↓

Routes / Controllers

↓

Services

↓

Repositories

↓

Banco de Dados
```
---

# 📌 Funcionalidades

* Cadastro de usuários
* Login e autenticação
* Cadastro e gerenciamento de produtos
* Carrinho de compras
* Aplicação de cupons
* Criação de pedidos
* Processamento de pagamentos
* Controle de estoque

---

# 📋 Regras de Negócio

* Apenas usuários autenticados podem realizar compras.
* Cupons somente podem ser utilizados enquanto estiverem ativos e dentro da validade.
* O sistema impede que dois usuários adquiram simultaneamente a última unidade disponível de um produto.
* Após a confirmação do pagamento, o pedido não poderá mais ser alterado.

---

# 📐 Diagramas

## Diagrama Entidade-Relacionamento (DER)

<p align="center">
<img src="docs/DER ecommerce.drawio.png" width="900">
</p>

---

## Diagrama de Casos de Uso

<p align="center">
<img src="docs/Caso de Uso.drawio.png" width="900">
</p>

---

# ▶ Como Executar o Projeto

## 1. Clonar o repositório

```bash
git clone https://github.com/ecommerce-es.git
```

## 2. Entrar na pasta

```bash
cd ecommerce-es
```

## 3. Criar o ambiente virtual

```bash
python -m venv .venv
```

## 4. Ativar o ambiente virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

## 5. Instalar as dependências

Caso utilize **uv**:

```bash
uv sync
```

Ou utilizando **pip**:

```bash
pip install -e .
```

## 6. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Configure as credenciais do banco PostgreSQL antes de iniciar a aplicação.

## 7. Executar as migrações

```bash
alembic upgrade head
```

## 8. Iniciar a aplicação

```bash
uvicorn src.main:app --reload
```

A API estará disponível em:

```
http://localhost:8000
```

---

# 🧪 Testes

Para executar os testes automatizados:

```bash
pytest
```

---

# 👥 Integrantes

<div align="center">

| Nome         | GitHub                                                                                                                                  |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Luana Souza  | [![GitHub](https://img.shields.io/badge/GitHub-111217?style=flat-square\&logo=github\&logoColor=white)](https://github.com/luanaapms)   |
| Ygor Pereira | [![GitHub](https://img.shields.io/badge/GitHub-111217?style=flat-square\&logo=github\&logoColor=white)](https://github.com/YgorPereira) |

</div>

---
