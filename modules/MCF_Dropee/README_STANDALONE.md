# 🤖 Dropee Bot Standalone

Este é um bot autônomo para o jogo Dropee que funciona **independentemente** do MasterCryptoFarm. 

## 📋 Características

- ✅ **100% Autônomo** - Não precisa do framework MasterCryptoFarm
- 🔄 **Auto Farming** - Inicia e coleta farming automaticamente
- 🎁 **Recompensa Diária** - Coleta recompensas diárias automaticamente
- 🔐 **Gerenciamento de Tokens** - Salva e renova tokens automaticamente
- 🌐 **Suporte a Proxy** - Configure proxy para cada conta
- 📝 **Logs Detalhados** - Sistema de logging completo
- ⚙️ **Configurável** - Configurações personalizáveis via JSON

## 🚀 Instalação

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Contas
Na primeira execução, será criado um arquivo `accounts_example.json`. Renomeie para `accounts.json` e configure suas contas:

```json
{
    "conta1": {
        "telegram_data": "query_id=AAAA...&user=%7B%22id%22%3A...",
        "proxy": null
    },
    "conta2": {
        "telegram_data": "query_id=BBBB...&user=%7B%22id%22%3A...",
        "proxy": "http://usuario:senha@proxy:porta"
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

## ⚡ Execução

```bash
python standalone_bot.py
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
├── standalone_bot.py      # Bot principal
├── requirements.txt       # Dependências
├── accounts.json         # Suas contas (criar manualmente)
├── config.json          # Configurações (criado automaticamente)
├── tokens.json          # Tokens salvos (criado automaticamente)
└── README_STANDALONE.md  # Este arquivo
```

## 🔧 Funcionalidades

### ✅ Implementadas:
- Autenticação via Telegram
- Renovação automática de tokens
- Coleta de recompensa diária
- Farming automático (iniciar/coletar)
- Verificação de saldo
- Suporte a múltiplas contas
- Suporte a proxy por conta

### 🚧 Em Desenvolvimento:
- Execução de tarefas/quests
- Sistema de tribe/aliança
- Interface web básica
- Modo daemon (execução contínua)

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

Para executar o bot continuamente, você pode usar um loop:

```bash
# Linux/Mac
while true; do python standalone_bot.py; sleep 3600; done

# Windows (PowerShell)
while ($true) { python standalone_bot.py; Start-Sleep 3600 }
```

Ou usar ferramentas como `cron` (Linux) ou Task Scheduler (Windows).