# 🤖 Dropee Bot Standalone

Este é um bot autônomo para o jogo Dropee que funciona **independentemente** do MasterCryptoFarm. 

## 📋 Características

- ✅ **100% Autônomo** - Não precisa do framework MasterCryptoFarm
- 🔄 **Auto Farming** - Inicia e coleta farming automaticamente
- 🎁 **Recompensa Diária** - Coleta recompensas diárias automaticamente
- 🎯 **Auto Tarefas** - Completa tarefas automaticamente
- 🎰 **Roda da Fortuna** - Gira roda automaticamente
- 🔐 **Gerenciamento de Tokens** - Salva e renova tokens automaticamente
- 🌐 **Suporte a Proxy** - Configure proxy para cada conta
- 📝 **Logs Detalhados** - Sistema de logging completo
- ⚙️ **Configurável** - Configurações personalizáveis via JSON
- 📊 **Estatísticas** - Rastreamento detalhado de ganhos
- 🔄 **Modo Contínuo** - Execução automática em intervalos
- 🎮 **Duas Versões** - Bot simples e avançado

## 🚀 Instalação Rápida

### Instalação Automática (Recomendado)
```bash
python install.py
```

### Instalação Manual

#### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 2. Configurar Contas
Na primeira execução, será criado um arquivo `accounts_example.json`. Copie para `accounts.json` e configure suas contas:

```json
{
    "conta_principal": {
        "telegram_data": "query_id=AAAA...&user=%7B%22id%22%3A...",
        "proxy": null,
        "enabled": true,
        "notes": "Conta principal sem proxy"
    },
    "conta_com_proxy": {
        "telegram_data": "query_id=BBBB...&user=%7B%22id%22%3A...",
        "proxy": "http://usuario:senha@proxy:porta",
        "enabled": true,
        "notes": "Conta com proxy"
    }
}
```

### 3. Obter dados do Telegram

Para obter o `telegram_data`:

1. Abra o Telegram Web/Desktop
2. Acesse o bot @DropeeBot
3. Abra as ferramentas de desenvolvedor (F12)
4. Vá para a aba Network/Rede
5. Clique em "Play" no jogo
6. Procure por uma requisição que contenha `query_id=`
7. Copie toda a string de dados

## ⚡ Formas de Execução

### 🎮 Menu Interativo (Recomendado)
```bash
python run_bot.py
```

### 🚀 Execução Direta

#### Bot Simples
```bash
python standalone_bot.py
```

#### Bot Avançado (Recomendado)
```bash
python advanced_standalone_bot.py
```

### 🔄 Modo Contínuo
```bash
# Bot avançado a cada hora
python run_bot.py continuous --interval 3600

# Bot simples a cada 30 minutos
python run_bot.py continuous --interval 1800 --bot-type simple
```

### 📊 Ver Estatísticas
```bash
python run_bot.py stats
```

## ⚙️ Configurações

O arquivo `config.json` é criado automaticamente com as seguintes opções:

```json
{
    "check_interval": 3600,
    "auto_claim_daily_reward": true,
    "auto_farming": true,
    "auto_tasks": true,
    "delay_min": 5,
    "delay_max": 15
}
```

### Explicação das Configurações:

- `check_interval`: Intervalo entre execuções (em segundos)
- `auto_claim_daily_reward`: Coletar recompensa diária automaticamente
- `auto_farming`: Gerenciar farming automaticamente
- `auto_tasks`: Executar tarefas automaticamente (futuro)
- `delay_min/max`: Delay aleatório entre contas (em segundos)

## 📁 Estrutura de Arquivos

```
MCF_Dropee/
├── 📄 BOTS
│   ├── standalone_bot.py            # Bot simples
│   ├── advanced_standalone_bot.py   # Bot avançado (recomendado)
│   └── run_bot.py                   # Script de execução com menu
├── 🔧 CONFIGURAÇÃO
│   ├── install.py                   # Instalação automática
│   ├── requirements.txt             # Dependências Python
│   ├── accounts.json               # Suas contas (criar)
│   ├── accounts_example.json       # Exemplo de contas
│   └── config.json                 # Configurações do bot
├── 📊 DADOS
│   ├── tokens.json                 # Tokens salvos (automático)
│   └── stats.json                  # Estatísticas (automático)
├── 🚀 SCRIPTS INÍCIO
│   ├── start_bot.sh/.bat           # Scripts de inicialização
└── 📖 DOCUMENTAÇÃO
    └── README_STANDALONE.md         # Este arquivo
```

## 🔧 Funcionalidades

### ✅ Bot Simples (standalone_bot.py):
- ✅ Autenticação via Telegram
- ✅ Renovação automática de tokens
- ✅ Coleta de recompensa diária
- ✅ Farming automático (iniciar/coletar)
- ✅ Verificação de saldo
- ✅ Suporte a múltiplas contas
- ✅ Suporte a proxy por conta

### 🚀 Bot Avançado (advanced_standalone_bot.py):
- ✅ Todas as funcionalidades do bot simples
- ✅ **Execução automática de tarefas/quests**
- ✅ **Roda da fortuna automática**
- ✅ **Sistema completo de estatísticas**
- ✅ **Gerenciamento avançado de tokens**
- ✅ **Logs detalhados com níveis**
- ✅ **Retry automático em falhas**
- ✅ **Rate limiting inteligente**
- ✅ **Delays aleatórios para segurança**
- ✅ **Contas habilitadas/desabilitadas**
- ✅ **Relatório de ganhos por sessão**

### 🎮 Sistema de Execução (run_bot.py):
- ✅ **Menu interativo**
- ✅ **Modo contínuo/daemon**
- ✅ **Múltiplas opções de execução**
- ✅ **Visualização de estatísticas**
- ✅ **Gerenciamento de configurações**

### 🚧 Funcionalidades Futuras:
- Sistema de tribe/aliança
- Interface web básica
- Integração com Discord/Telegram notifications
- Sistema de backup automático

## 🛠️ Solução de Problemas

### Erro de Autenticação
- Verifique se o `telegram_data` está correto e atualizado
- Os dados do Telegram expiram após algumas horas
- Obtenha novos dados seguindo o guia acima

### Erro de Dependências
```bash
pip install --upgrade cloudscraper requests
```

### Bot não executa
- Verifique se o Python 3.7+ está instalado
- Certifique-se de que o arquivo `accounts.json` existe e está configurado
- Verifique os logs para erros específicos

## 📞 Suporte

Este bot é baseado no trabalho original do MasterkinG32. Para suporte:

- GitHub: https://github.com/masterking32
- Telegram: https://t.me/MasterCryptoFarmBot

## ⚖️ Aviso Legal

- Use por sua própria conta e risco
- Respeite os termos de serviço do jogo
- Este bot é apenas para fins educacionais
- O uso de bots pode violar os termos do jogo

## 🔄 Execução Contínua (Opcional)

### Usando o Sistema Integrado (Recomendado)
```bash
# Modo contínuo com menu
python run_bot.py continuous

# Direto pela linha de comando
python run_bot.py continuous --interval 3600 --bot-type advanced
```

### Usando Loops Manuais
```bash
# Linux/Mac
while true; do python advanced_standalone_bot.py; sleep 3600; done

# Windows (PowerShell)
while ($true) { python advanced_standalone_bot.py; Start-Sleep 3600 }
```

### Usando Agendadores do Sistema
```bash
# Linux cron (a cada hora)
0 * * * * cd /caminho/para/MCF_Dropee && python3 advanced_standalone_bot.py

# Windows Task Scheduler
# Use o GUI ou schtasks para agendar start_bot.bat
```

## 💡 Exemplos de Uso

### 🚀 Início Rápido
```bash
# 1. Instalar tudo automaticamente
python install.py

# 2. Configurar contas (editar accounts.json)
cp accounts_example.json accounts.json
# ... editar com seus dados ...

# 3. Executar com menu
python run_bot.py

# 4. Escolher opção 2 (Bot Avançado)
```

### 📊 Monitoramento de Ganhos
```bash
# Ver estatísticas detalhadas
python run_bot.py stats

# Ou usando o bot avançado
python advanced_standalone_bot.py --stats
```

### 🔧 Configuração Personalizada
```json
// config.json - Exemplo de configuração otimizada
{
    "check_interval": 1800,           // 30 minutos
    "auto_claim_daily_reward": true,  
    "auto_farming": true,             
    "auto_tasks": true,               // Completar tarefas
    "auto_wheel": true,               // Girar roda da fortuna
    "delay_min": 3,                   // Delay mínimo entre ações
    "delay_max": 8,                   // Delay máximo entre ações
    "max_retries": 5,                 // Tentativas em caso de erro
    "use_random_delays": true,        // Delays aleatórios para segurança
    "log_level": "INFO"               // Nível de logs (DEBUG, INFO, WARNING, ERROR)
}
```

### 🌐 Uso com Proxies
```json
// accounts.json - Exemplo com múltiplas contas e proxies
{
    "conta_principal": {
        "telegram_data": "query_id=...",
        "proxy": null,                    // Sem proxy
        "enabled": true,
        "notes": "Conta principal"
    },
    "conta_proxy_1": {
        "telegram_data": "query_id=...",
        "proxy": "http://user:pass@proxy1:8080",
        "enabled": true,
        "notes": "Conta com proxy HTTP"
    },
    "conta_proxy_2": {
        "telegram_data": "query_id=...",
        "proxy": "socks5://user:pass@proxy2:1080",
        "enabled": true,
        "notes": "Conta com proxy SOCKS5"
    },
    "conta_desativada": {
        "telegram_data": "query_id=...",
        "proxy": null,
        "enabled": false,                 // Temporariamente desabilitada
        "notes": "Conta em manutenção"
    }
}
```