# comand.io - Sistema de Comanda Digital

## Introdução

**comand.io** é um sistema inovador de comanda digital desenvolvido para restaurantes e bares modernos. Ele permite que os clientes façam pedidos através de uma interface intuitiva baseada em QR codes, eliminando a necessidade de comandas físicas.

O sistema oferece:
- 📱 Interface web responsiva para fazer pedidos
- 🍽️ Gerenciamento de mesas e pedidos
- 🧾 Sistema de comanda digital
- 🔄 Sincronização em tempo real
- 👨‍🍳 Painel da cozinha para controlar pedidos
- 📊 Gerenciamento de produtos e menus

---

## Pré-requisitos

### Opção 1: Execução Local (Recomendado para Desenvolvimento)

- **Python 3.12+**
- **pip** (gerenciador de pacotes Python)
- **MySQL 8.0+**
- **Git** (opcional)

### Opção 2: Com Docker (Recomendado para Produção/Deployment)

- **Docker Desktop** (ou Docker Engine)
- **Docker Compose**

#### Instalando Docker

##### Windows

1. Baixe o instalador em: https://www.docker.com/products/docker-desktop
2. Execute o instalador e siga as instruções
3. Reinicie o computador
4. Abra o Docker Desktop (pode levar alguns minutos na primeira inicialização)
5. Verifique a instalação no PowerShell/CMD:
   ```powershell
   docker --version
   docker-compose --version
   ```

##### macOS

1. Baixe o Docker Desktop para Mac: https://www.docker.com/products/docker-desktop
2. Abra o arquivo `.dmg` e arraste o Docker para a pasta Applications
3. Abra o Docker a partir de Applications
4. Verifique a instalação no Terminal:
   ```bash
   docker --version
   docker-compose --version
   ```

##### Linux (Ubuntu/Debian)

1. Instale o Docker:
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   ```

2. Adicione seu usuário ao grupo docker:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. Verifique a instalação:
   ```bash
   docker --version
   docker-compose --version
   ```

---

## 🚀 Iniciando o Serviço

### Opção 1: Com Docker Compose (Recomendado)

#### No Windows (PowerShell ou CMD):

1. **Navegue até o diretório do projeto:**
   ```powershell
   cd "caminho\para\comand_io"
   ```

2. **Inicie os serviços:**
   ```powershell
   docker-compose up -d --build
   ```
   - O flag `-d` executa em segundo plano (detached mode)
   - O flag `--build` reconstrói as imagens Docker

3. **Verifique se os serviços estão rodando:**
   ```powershell
   docker-compose ps
   ```

4. **Acesse a aplicação:**
   - Interface Web: http://localhost:5000
   - MySQL: localhost:3306

5. **Para visualizar os logs:**
   ```powershell
   docker-compose logs -f web
   ```

6. **Para parar os serviços:**
   ```powershell
   docker-compose down
   ```

#### No macOS e Linux (Terminal):

1. **Navegue até o diretório do projeto:**
   ```bash
   cd /caminho/para/comand_io
   ```

2. **Inicie os serviços:**
   ```bash
   docker-compose up -d --build
   ```
   - O flag `-d` executa em segundo plano (detached mode)
   - O flag `--build` reconstrói as imagens Docker

3. **Verifique se os serviços estão rodando:**
   ```bash
   docker-compose ps
   ```

4. **Acesse a aplicação:**
   - Interface Web: http://localhost:5000
   - MySQL: localhost:3306

5. **Para visualizar os logs:**
   ```bash
   docker-compose logs -f web
   ```

6. **Para parar os serviços:**
   ```bash
   docker-compose down
   ```

---

### Opção 2: Ambiente Virtual Local (Desenvolvimento)

#### No Windows (PowerShell):

1. **Navegue até o diretório do projeto:**
   ```powershell
   cd "caminho\para\comand_io"
   ```

2. **Crie um ambiente virtual:**
   ```powershell
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   > Se aparecer erro de política de execução, execute:
   > ```powershell
   > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   > ```

4. **Instale as dependências:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   MYSQL_ROOT_PASSWORD=comand_io_dev
   RESEND_API_KEY=sua_chave_api
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:comand_io_dev@localhost:3306/restaurante
   ```

6. **Inicie o servidor MySQL** (certifique-se que está rodando):
   
   Windows Service:
   ```powershell
   net start MySQL80
   ```
   
   Ou via Docker:
   ```powershell
   docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=comand_io_dev -e MYSQL_DATABASE=restaurante -v mysql_data:/var/lib/mysql mysql:8.0
   ```

7. **Execute a aplicação:**
   ```powershell
   python run.py
   ```

   A aplicação estará disponível em: **http://localhost:5000**

8. **Desative o ambiente virtual quando terminar:**
   ```powershell
   deactivate
   ```

#### No macOS e Linux (Terminal):

1. **Navegue até o diretório do projeto:**
   ```bash
   cd /caminho/para/comand_io
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python3 -m venv venv
   ```

3. **Ative o ambiente virtual:**
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```bash
   cat > .env << EOF
   MYSQL_ROOT_PASSWORD=comand_io_dev
   RESEND_API_KEY=sua_chave_api
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:comand_io_dev@localhost:3306/restaurante
   EOF
   ```

6. **Inicie o servidor MySQL** (certifique-se que está rodando):
   
   macOS (via Homebrew):
   ```bash
   brew services start mysql
   ```
   
   Linux (Ubuntu/Debian):
   ```bash
   sudo systemctl start mysql
   ```
   
   Ou via Docker:
   ```bash
   docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=comand_io_dev -e MYSQL_DATABASE=restaurante -v mysql_data:/var/lib/mysql mysql:8.0
   ```

7. **Execute a aplicação:**
   ```bash
   python run.py
   ```

   A aplicação estará disponível em: **http://localhost:5000**

8. **Desative o ambiente virtual quando terminar:**
   ```bash
   deactivate
   ```

---

## 📁 Estrutura do Projeto

```
comand_io/
├── app/                          # Código principal da aplicação Flask
│   ├── __init__.py               # Factory pattern da aplicação
│   ├── extensions.py             # Extensões (SQLAlchemy, CORS)
│   ├── email_service.py          # Serviço de envio de emails
│   ├── gerar_qr.py               # Gerador de QR codes
│   ├── frontend/                 # Rotas do frontend
│   ├── mesa/                     # Rotas de mesas
│   ├── pedido/                   # Rotas de pedidos
│   ├── produto/                  # Rotas de produtos
│   └── models/                   # Modelos de dados
├── frontend/                     # Arquivos estáticos (HTML, CSS, JS)
├── docker/                       # Configuração Docker
│   └── mysql/
│       └── init/
│           └── restaurante.sql   # Schema inicial do banco
├── qrcodes/                      # QR codes gerados
├── docker-compose.yml            # Orquestração de containers
├── Dockerfile                    # Imagem Docker da aplicação
├── requirements.txt              # Dependências Python
├── run.py                        # Ponto de entrada da aplicação
└── README.md                     # Este arquivo
```

---

## Testes automatizados: dublês Fake e Mock

Os testes do serviço de e-mail usam dois dublês para não chamar a API Resend:

- **Fake (`FakeEmailApiResponse`)**: simula uma resposta HTTP com `status_code` e `text`.
- **Mock (`unittest.mock`)**: substitui `requests.post`, fornece a resposta Fake e permite verificar se a chamada foi realizada.

No PowerShell, execute na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O teste valida os caminhos de sucesso e erro da API. A saída detalhada do comando pode ser capturada para comprovar a execução da atividade.

---

## Painel de relatórios

Acesse **http://localhost:5000/relatorios** (também disponível pelo link no admin) e informe o período desejado. As APIs `GET /relatorios/faturamento`, `GET /relatorios/produtos-mais-vendidos`, `GET /relatorios/ticket-medio` e `GET /relatorios/ocupacao-mesas` aceitam `inicio` e `fim` no formato `AAAA-MM-DD`; sem parâmetros, usam o mês atual até hoje.

- O faturamento soma pagamentos com status `pago`, agrupados pela data de confirmação.
- Ranking de produtos e ticket médio usam os itens dos pedidos fechados no período, pela data de criação do pedido.
- A ocupação por mesa mede o tempo entre a criação e o último pagamento confirmado, limitado ao período selecionado. Pedidos ainda ativos contam até o fim do período ou o momento atual, o que ocorrer primeiro; pedidos fechados sem pagamento registrado não têm duração calculável e não são contabilizados. A taxa geral é a média das taxas das mesas.

O painel apresenta cartões de métricas, filtros de data, gráficos de faturamento diário e produtos mais vendidos, além das tabelas de ranking e ocupação.

---

## Programa de fidelidade

Acesse **http://localhost:5000/fidelidade** pelo link no painel administrativo para cadastrar e ativar benefícios de desconto. Na tela de pagamento, o cliente informa nome e e-mail para participar do programa.

- Cada pedido totalmente pago gera **1 ponto por real** sobre o total após eventual desconto.
- Os benefícios são descontos fixos, resgatáveis antes do primeiro pagamento do pedido.
- Todo crédito e resgate fica registrado no histórico do cliente.
- Quando `RESEND_API_KEY` estiver configurada, o cliente recebe e-mails de crédito e resgate de pontos.

---

## Reservas de mesas e lista de espera

Tela da recepção: **http://localhost:5000/recepcao** (também tem link no `/admin` e no `/mesas`).

**Reserva**: cliente, contato, data, horário, quantidade de pessoas, mesa, observação e status.
Os status são `confirmada`, `aguardando` (o cliente chegou e está na lista de espera), `em_atendimento`, `cancelada`, `nao_compareceu` e `finalizada` (o pedido da mesa foi encerrado ou pago).

Regras:
- A mesa precisa comportar a quantidade de pessoas.
- Cada reserva ocupa a mesa por **2 horas**, e duas reservas da mesma mesa com menos de 2h de diferença entram em conflito.
- Não dá para reservar no passado. O check-in só vale no dia da reserva.
- **Check-in**: abre o pedido da mesa (a comanda funciona normalmente em `/mesa/N`) e marca a mesa como ocupada. Se a mesa estiver ocupada, o sistema sugere outra livre. Se não houver nenhuma, o cliente vai para a lista de espera.
- **Lista de espera**: guarda nome, contato, pessoas e horário de entrada, e mostra a ordem de chegada. Uma mesa liberada pode ser atribuída a qualquer cliente da fila (a tela já sugere as mesas que comportam o grupo).
- A disponibilidade é calculada na hora, então ela se atualiza sozinha depois de cancelamento, check-in, "não compareceu" e encerramento do pedido (fechar ou pagar).

Principais rotas da API:

| Método | Rota | Descrição |
|---|---|---|
| GET | `/reservas?data=&mesa=&status=&busca=` | Consulta com filtros (status aceita vários, separados por vírgula) |
| POST | `/reservas` | Nova reserva |
| PUT | `/reservas/<id>` | Editar |
| POST | `/reservas/<id>/cancelar` | Cancelar |
| POST | `/reservas/<id>/check-in` | Check-in (body opcional: `{"mesa_numero": N}`) |
| POST | `/reservas/<id>/nao-compareceu` | Marcar não comparecimento |
| POST | `/reservas/<id>/lista-espera` | Cliente com reserva vai para a fila |
| GET | `/reservas/agenda?data=` | Agenda diária por mesa |
| GET | `/reservas/mesas-disponiveis?data=&horario=&pessoas=` | Mesas disponíveis |
| GET/POST | `/lista-espera` | Fila em ordem / entrar na fila |
| POST | `/lista-espera/<id>/atribuir` | Atribuir mesa (`{"mesa_numero": N}`) |
| POST | `/lista-espera/<id>/desistir` | Remover da fila |

**Dados de exemplo**: são criados automaticamente na primeira execução (reservas de hoje e de amanhã, além de 3 clientes na fila). Para recriá-los com a data de hoje (por exemplo, no dia da prova):

```bash
flask --app run.py dados-exemplo-reservas --recriar
```

Roteiro de demonstração:
1. Cadastrar uma reserva na mesa 3 às 20:00. O sistema avisa do conflito com a reserva da Carla às 19:00.
2. Cadastrar a mesma reserva para 6 pessoas na mesa 1. O sistema avisa que a capacidade foi excedida.
3. Clicar em "Ver mesas disponíveis" e salvar a reserva.
4. Abrir a mesa 1 pelo painel `/mesas` e fazer o check-in do João (mesa 1). O sistema sugere outra mesa ou a lista de espera.
5. Fazer o check-in da Carla, abrir a comanda e adicionar itens.
6. Fechar ou pagar um pedido e atribuir a mesa liberada ao 1º da fila.

Testes: `python -m unittest tests.test_reservas -v`

---

## 🔨 Variáveis de Ambiente

Configure as seguintes variáveis conforme necessário:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MYSQL_ROOT_PASSWORD` | `comand_io_dev` | Senha do MySQL |
| `RESEND_API_KEY` | (vazio) | Chave de API para envio de emails |
| `SQLALCHEMY_DATABASE_URI` | (configurado no docker-compose) | String de conexão do banco |

---

## 🐛 Troubleshooting

### Docker Desktop

**Problema (Windows):** "Docker daemon is not running"
- Solução: Abra o Docker Desktop a partir do menu iniciar

**Problema (Windows):** "Cannot connect to the Docker daemon"
- Solução: Habilite o WSL 2 (Windows Subsystem for Linux 2):
  ```powershell
  wsl --install
  ```
  Reinicie o computador e tente novamente

**Problema (macOS):** "Cannot connect to the Docker daemon"
- Solução: Certifique-se de que o Docker Desktop está aberto. Se persistir:
  ```bash
  rm -rf ~/.docker/config.json
  ```
  E reinicie o Docker Desktop

**Problema (Linux):** "permission denied while trying to connect to the Docker daemon"
- Solução: Adicione seu usuário ao grupo docker:
  ```bash
  sudo usermod -aG docker $USER
  ```
  Faça logout e login novamente

### Ambiente Virtual

**Problema (Windows):** "comando python não encontrado"
- Solução: Instale Python em https://www.python.org/ (marque "Add Python to PATH" durante instalação)

**Problema (macOS/Linux):** "python: command not found"
- Solução: Use `python3` em vez de `python`:
  ```bash
  python3 -m venv venv
  python3 run.py
  ```

**Problema (Windows):** "Permission denied" ao executar scripts
- Solução: Execute no PowerShell como administrador ou altere a política de execução conforme descrito acima

**Problema (macOS/Linux):** "Permission denied: ./venv/bin/activate"
- Solução: Defina as permissões corretas:
  ```bash
  chmod +x venv/bin/activate
  ```

### Conexão com MySQL

**Problema:** "Connection refused" porta 3306
- Solução: Verifique se o MySQL está rodando
  - Com Docker: `docker ps` (procure pelo container mysql)
  - Windows: Verifique MySQL Services na janela Services
  - macOS: `brew services list`
  - Linux: `sudo systemctl status mysql`

---

## 📝 Próximas Etapas

Após iniciar o serviço:

1. Acesse http://localhost:5000
2. Configure suas mesas e produtos no admin
3. Teste a geração de QR codes
4. Acesse o painel da cozinha

---

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação do projeto ou entre em contato com a equipe de desenvolvimento.

---

**Última atualização:** Abril 2026  
**Versão:** 1.0
