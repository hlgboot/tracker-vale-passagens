# 🚆 Tracker Vale Passagens

Bot do Telegram desenvolvido em **Python** para monitorar automaticamente a disponibilidade de passagens dos trens de passageiros da **Vale**, notificando os usuários quando são encontradas passagens para uma rota e data específicas.

O projeto automatiza a consulta de disponibilidade, permitindo cadastrar, gerenciar e reativar monitoramentos diretamente pelo Telegram.

## 📌 Sobre o projeto

A disponibilidade de passagens ferroviárias pode variar ao longo do tempo, exigindo consultas frequentes ao sistema de vendas.

O **Tracker Vale Passagens** foi desenvolvido para automatizar esse processo, realizando verificações periódicas no sistema de passagens da Vale e enviando notificações pelo Telegram quando encontra passagens disponíveis.

O sistema permite que diferentes usuários monitorem uma mesma rota sem a necessidade de criar consultas duplicadas.

## ⚙️ Funcionalidades

- **Monitoramento automático:** consultas periódicas de disponibilidade a cada 5 minutos.
- **Notificações pelo Telegram:** envio de alertas contendo origem, destino, data, horário de partida e valor da passagem.
- **Cadastro de viagens:** seleção das estações de origem e destino e da data desejada.
- **Gerenciamento de alertas:** visualização e remoção dos monitoramentos ativos.
- **Reativação de buscas:** possibilidade de reativar um monitoramento após o recebimento de uma notificação.
- **Suporte a múltiplos usuários:** compartilhamento de monitoramentos para rotas e datas idênticas.
- **Persistência de dados:** armazenamento dos monitoramentos em arquivos JSON.
- **Gerenciamento de sessões HTTP:** utilização de cookies e renovação de sessão para realizar consultas ao sistema da Vale.

## 🛠️ Tecnologias utilizadas

- **Python:** linguagem principal do projeto.
- **python-telegram-bot:** integração com a API do Telegram e gerenciamento dos comandos.
- **requests:** realização de requisições HTTP ao sistema de passagens.
- **JSON:** armazenamento de estações e monitoramentos.
- **python-dotenv:** carregamento de variáveis de ambiente.
- **truststore:** integração com o armazenamento de certificados do sistema.
- **JobQueue:** agendamento das verificações periódicas.

## 📂 Estrutura do projeto

```text
tracker-vale-passagens/
├── bot.py
├── monitor.py
├── vale.py
├── locais.py
├── data/
│   ├── locais.json
│   └── monitoramentos.json
├── requirements.txt
├── .gitignore
└── README.md
```

### Descrição dos arquivos

- **bot.py:** implementação do bot do Telegram, comandos, interações e agendamento das verificações.
- **monitor.py:** criação, armazenamento, consulta e remoção dos monitoramentos.
- **vale.py:** comunicação HTTP com o sistema de passagens da Vale e processamento das respostas.
- **locais.py:** carregamento e consulta das estações disponíveis.
- **data/locais.json:** catálogo de estações ferroviárias e seus respectivos códigos.
- **data/monitoramentos.json:** armazenamento dos monitoramentos cadastrados.
- **requirements.txt:** dependências necessárias para executar o projeto.

## 🚀 Instalação e execução

### Pré-requisitos

- Python 3.9 ou superior.
- Conta no Telegram.
- Token de um bot criado através do [BotFather](https://t.me/BotFather).
- Conexão com a internet.

### 1. Clonar o repositório

```bash
git clone https://github.com/hlgboot/tracker-vale-passagens.git
cd tracker-vale-passagens
```

### 2. Criar um ambiente virtual

```bash
python -m venv .venv
```

Ativar o ambiente virtual:

**Linux/macOS:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
TOKEN=SEU_TOKEN_DO_TELEGRAM
```

Substitua `SEU_TOKEN_DO_TELEGRAM` pelo token fornecido pelo BotFather.

**Importante:** não compartilhe o token nem envie o arquivo `.env` para o GitHub.

### 5. Executar o bot

```bash
python bot.py
```

Após a inicialização, o bot começará a receber comandos pelo Telegram e executará verificações periódicas dos monitoramentos cadastrados.

## 🤖 Comandos disponíveis

| Comando | Descrição |
|---|---|
| `/start` | Exibe a mensagem inicial e os comandos disponíveis. |
| `/monitorar` | Inicia o cadastro de um novo monitoramento. |
| `/alertas` | Lista os monitoramentos ativos do usuário. |
| `/cancelar` | Cancela o processo de cadastro atual. |

### Exemplo de utilização

**1. Iniciar o monitoramento**

Envie o comando:

```text
/monitorar
```

**2. Informar a origem**

O bot apresenta a lista de estações disponíveis. Informe o código desejado:

```text
7185
```

**3. Informar o destino**

Selecione o código da estação de destino:

```text
7173
```

**4. Informar a data**

```text
25/12/2026
```

O bot registrará o monitoramento e iniciará as verificações automáticas.

### Exemplo de notificação

Quando uma passagem é encontrada, o usuário recebe uma mensagem semelhante a:

```text
🚨 PASSAGEM ENCONTRADA!

Trem: Belo Horizonte → Governador Valadares
Data: 25/12/2026
Hora de Partida: [horário retornado]
Valor: R$ [valor retornado]

Acesse o site da Vale para comprar!

[🔄 Reativar busca]
```

Após encontrar passagens e enviar os alertas, o monitoramento é removido automaticamente. O usuário pode reativá-lo pelo botão presente na notificação.

## 🔄 Funcionamento do sistema

O processo de monitoramento segue as seguintes etapas:

1. O usuário cadastra uma rota e uma data pelo Telegram.
2. O sistema verifica se já existe um monitoramento para a mesma viagem.
3. Caso exista, o usuário é associado ao monitoramento existente.
4. Os dados são armazenados em `data/monitoramentos.json`.
5. A cada 5 minutos, o sistema consulta as rotas monitoradas.
6. Quando encontra passagens, envia notificações aos usuários cadastrados.
7. O monitoramento é removido após o envio dos alertas, podendo ser reativado pelo usuário.

### Comunicação com a Vale

As consultas são realizadas por meio de requisições HTTP ao sistema de venda de passagens da Vale.

O módulo `vale.py` é responsável por:

- Inicializar e manter uma sessão HTTP.
- Gerenciar cookies de sessão.
- Construir os dados necessários para a consulta.
- Realizar requisições de disponibilidade.
- Processar as passagens retornadas.
- Renovar a sessão quando necessário.

## ⚠️ Observações importantes

- O bot **não realiza compras nem reservas** de passagens. Ele apenas consulta a disponibilidade e envia notificações.
- A disponibilidade pode mudar entre a verificação e o acesso ao site de vendas.
- O funcionamento depende da disponibilidade e da estrutura do sistema de consultas da Vale.
- O processo Python precisa permanecer em execução para que os monitoramentos continuem sendo verificados.
- Os monitoramentos são armazenados localmente em JSON, sem necessidade de um banco de dados externo.
- Este é um projeto independente, sem vínculo oficial com a Vale.

## 👨‍💻 Autor

Desenvolvido por [@hlgboot](https://github.com/hlgboot).

---

Projeto desenvolvido para automatizar consultas de disponibilidade de passagens ferroviárias e explorar integração com APIs, bots de mensagens e tarefas agendadas em Python.
