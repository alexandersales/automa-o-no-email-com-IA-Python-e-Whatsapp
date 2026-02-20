# 🤖 Assistente Pessoal de E-mail com IA e WhatsApp

Bem-vindo ao projeto do Assistente Pessoal de E-mail! Este script automatiza a leitura da sua caixa de entrada do Gmail, utiliza a Inteligência Artificial do Google (Gemini) para ler e resumir os e-mails mais recentes e envia um "Boletim Executivo" diretamente para o seu WhatsApp através da Twilio. 

E o melhor: tudo isto roda de forma **100% gratuita e automática** na nuvem usando o GitHub Actions!

---

## 🛠️ Tecnologias Utilizadas
* **Python 3.10+** (Linguagem base)
* **BeautifulSoup4** (Para limpar e extrair texto de e-mails HTML)
* **Google Generative AI (Gemini 2.5 Flash)** (Para gerar os resumos inteligentes)
* **Twilio API** (Para o envio automático de mensagens via WhatsApp)
* **GitHub Actions** (Para agendar e rodar o script na nuvem diariamente)

---

## 📋 Pré-requisitos (O que você vai precisar)

Antes de rodar o código, você precisará criar contas e gerar algumas chaves gratuitas:

1. **Gmail:** Uma Senha de Aplicativo (App Password) gerada nas configurações de segurança da sua conta Google (não use a sua senha normal!).
2. **Google AI Studio:** Uma API Key gratuita para acessar o modelo Gemini.
3. **Twilio:** Uma conta gratuita e um ambiente Sandbox do WhatsApp ativado (você precisará do seu `Account SID` e `Auth Token`).
4. **GitHub:** Uma conta para hospedar o código e rodar a automação.

---

## 🚀 Passo a Passo da Instalação

### Passo 1: Preparar os Ficheiros
Crie um repositório **Privado** no seu GitHub e adicione dois ficheiros: `requirements.txt` e `assistente_email.py`.

**Conteúdo do `requirements.txt`:**
```text
beautifulsoup4
google-generativeai
twilio
```
Conteúdo do assistente_email.py:
Copie o código abaixo. Atenção: Você só precisa alterar os números de telefone na seção 3 do código. As senhas serão configuradas no painel do GitHub por segurança.

    import os
    import imaplib
    import email
    from bs4 import BeautifulSoup
    import google.generativeai as genai
    from twilio.rest import Client

print("Iniciando o Assistente de E-mail... 🚀")


# 1. CARREGAR SEGREDOS (Variáveis de Ambiente do GitHub)
# NUNCA escreva as suas senhas diretamente no código!

    meu_email = os.environ.get("GMAIL_EMAIL")
    minha_senha = os.environ.get("GMAIL_SENHA")
    chave_ia = os.environ.get("GEMINI_API_KEY")
    twilio_sid = os.environ.get("TWILIO_SID")
    twilio_token = os.environ.get("TWILIO_TOKEN")


# 2. CONECTAR AO GMAIL E LER OS E-MAILS

    print("Conectando ao Gmail...")
    try:
        conexao = imaplib.IMAP4_SSL("imap.gmail.com")
        conexao.login(meu_email, minha_senha)
        conexao.select("inbox")
        
        # Busca todos os e-mails
        status, mensagens = conexao.search(None, "ALL")
        ids_emails = mensagens[0].split()
        
        # Pega os 10 e-mails mais recentes
        ultimos_ids = ids_emails[-10:]
        pacote_de_emails = ""
        
        for num_id in ultimos_ids:
            status, dados_email = conexao.fetch(num_id, '(RFC822)')
            mensagem_bruta = dados_email[0][1]
            mensagem = email.message_from_bytes(mensagem_bruta)
            
            remetente = mensagem.get("From")
            assunto = mensagem.get("Subject")
            corpo_texto = ""
            
            if mensagem.is_multipart():
                for parte in mensagem.walk():
                    if parte.get_content_type() == "text/html":
                        html_bruto = parte.get_payload(decode=True).decode("utf-8", errors="ignore")
                        sopa = BeautifulSoup(html_bruto, "html.parser")
                        corpo_texto = sopa.get_text(separator=" ", strip=True)
                        break
            else:
                corpo_texto = mensagem.get_payload(decode=True).decode("utf-8", errors="ignore")
            
            # Limita o texto de cada e-mail para não sobrecarregar a IA
            pacote_de_emails += f"\nDe: {remetente}\nAssunto: {assunto}\nConteúdo: {corpo_texto[:400]}\n---\n"
            
    except Exception as erro:
        print(f"Erro ao conectar no Gmail: {erro}")
        exit()


# 3. GERAR O RESUMO COM A IA (GEMINI)

    print("Conectando ao Gemini para gerar o resumo... 🧠")
    try:
        genai.configure(api_key=chave_ia)
        modelo = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Você é meu assistente executivo. Abaixo estão os dados dos últimos e-mails que recebi.
        Por favor, faça um resumo diário em formato de tópicos para o WhatsApp.
        Destaque os remetentes importantes, o assunto principal e ignore propagandas inúteis.
        Seja direto e organizado.
    
        Aqui estão os e-mails:
        {pacote_de_emails}
        """
        
        resposta_ia = modelo.generate_content(prompt)
        resumo_final = resposta_ia.text
    except Exception as erro:
        print(f"Erro ao processar a IA: {erro}")
        exit()


# 4. ENVIAR PARA O WHATSAPP (TWILIO)

print("Enviando resumo para o WhatsApp... 📱")

# 👉 ATENÇÃO: SUBSTITUA OS NÚMEROS ABAIXO PELOS SEUS 
        remetente_twilio = "whatsapp:+14155238886" # Confirme o número do seu Sandbox Twilio
        meu_numero = "whatsapp:+55SEUNUMEROAQUI" # Coloque o seu código de país + DDD + Número
        
        try:
            cliente_twilio = Client(twilio_sid, twilio_token)
            mensagem_whatsapp = f"🤖 *Seu Boletim Diário de E-mails*\n\n{resumo_final}"
        
        mensagem = cliente_twilio.messages.create(
            from_=remetente_twilio,
            body=mensagem_whatsapp,
            to=meu_numero
        )
        print("✅ Sucesso! Mensagem enviada para o seu WhatsApp.")
    except Exception as erro:
        print(f"Erro ao enviar o WhatsApp: {erro}")

Passo 2: Configurar os Segredos (Secrets) no GitHub

Para o código funcionar com segurança, você precisa guardar as suas chaves no "Cofre" do GitHub.

No seu repositório, vá na aba Settings > Security > Secrets and variables > Actions.

Clique em New repository secret e adicione os 5 segredos exatamente com estes nomes (sem aspas e sem espaços vazios):

    GMAIL_EMAIL: (Ex: seuemail@gmail.com)

    GMAIL_SENHA: (A senha de aplicativo de 16 dígitos)

    GEMINI_API_KEY: (Sua chave do Google AI Studio)
    
    TWILIO_SID: (O seu Account SID da Twilio que começa com AC)
    
    TWILIO_TOKEN: (O seu Auth Token da Twilio)

Passo 3: Criar a Automação (GitHub Actions)

No seu repositório, vá na aba Actions.

Clique em "set up a workflow yourself".

Cole o código YAML abaixo e salve (Commit). Este código diz para a nuvem rodar o script todos os dias às 07:00 da manhã (horário do Brasil).
```
name: Assistente de Email Diario

on:
  schedule:
    # 10:00 UTC equivale a 07:00 no Horário de Brasília
    - cron: '0 10 * * *'
  workflow_dispatch:

jobs:
  resumir_emails:
    runs-on: ubuntu-latest

    steps:
    - name: Baixar arquivos do repositório
      uses: actions/checkout@v3

    - name: Configurar o Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Instalar bibliotecas
      run: pip install -r requirements.txt

    - name: Executar o Assistente
      env:
        GMAIL_EMAIL: ${{ secrets.GMAIL_EMAIL }}
        GMAIL_SENHA: ${{ secrets.GMAIL_SENHA }}
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        TWILIO_SID: ${{ secrets.TWILIO_SID }}
        TWILIO_TOKEN: ${{ secrets.TWILIO_TOKEN }}
      run: python assistente_email.py
```

🎉 Pronto! O seu assistente pessoal está configurado e rodando na nuvem!

"O progresso não é feito pelos que se levantam cedo. É feito pelos homens preguiçosos tentando encontrar maneiras mais fáceis de fazer algo."
    --Robert A. Heinlein
