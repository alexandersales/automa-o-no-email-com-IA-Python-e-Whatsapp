import os
import imaplib
import email
from bs4 import BeautifulSoup
import google.generativeai as genai
from twilio.rest import Client

print("Iniciando o Assistente de E-mail... 🚀")

# ==============================================================================
# 1. CARREGAR SEGREDOS (Variáveis de Ambiente)
# NUNCA escreva as suas senhas diretamente no código se for subir para o GitHub!
# Estes valores devem ser configurados nos "Secrets" do GitHub Actions.
# ==============================================================================
meu_email = os.environ.get("GMAIL_EMAIL")
minha_senha = os.environ.get("GMAIL_SENHA")
chave_ia = os.environ.get("GEMINI_API_KEY")
twilio_sid = os.environ.get("TWILIO_SID")
twilio_token = os.environ.get("TWILIO_TOKEN")

# ==============================================================================
# 2. CONECTAR AO GMAIL E LER OS E-MAILS
# ==============================================================================
print("Conectando ao Gmail...")
try:
    conexao = imaplib.IMAP4_SSL("imap.gmail.com")
    conexao.login(meu_email, minha_senha)
    conexao.select("inbox")
    
    # Busca todos os e-mails da caixa de entrada
    status, mensagens = conexao.search(None, "ALL")
    ids_emails = mensagens[0].split()
    
    # Pega os 10 e-mails mais recentes (ajuste o número se desejar ler mais)
    ultimos_ids = ids_emails[-10:]
    pacote_de_emails = ""
    
    for num_id in ultimos_ids:
        status, dados_email = conexao.fetch(num_id, '(RFC822)')
        mensagem_bruta = dados_email[0][1]
        mensagem = email.message_from_bytes(mensagem_bruta)
        
        remetente = mensagem.get("From")
        assunto = mensagem.get("Subject")
        corpo_texto = ""
        
        # Extrai o texto limpo, ignorando formatações HTML invisíveis
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

# ==============================================================================
# 3. GERAR O RESUMO COM A IA (GEMINI)
# ==============================================================================
print("Conectando ao Gemini para gerar o resumo... 🧠")
try:
    genai.configure(api_key=chave_ia)
    # Utilizamos o modelo rápido e eficiente do Google
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

# ==============================================================================
# 4. ENVIAR PARA O WHATSAPP (TWILIO)
# ==============================================================================
print("Enviando resumo para o WhatsApp... 📱")

# 👉 ATENÇÃO: SUBSTITUA OS NÚMEROS ABAIXO PELOS SEUS DADOS DA TWILIO 👈
remetente_twilio = "whatsapp:+1XXXXXXXXXX" # <-- COLOQUE AQUI O NÚMERO DO SEU SANDBOX TWILIO
meu_numero = "whatsapp:+55DDNNNNNNNNN" # <-- COLOQUE AQUI O SEU NÚMERO (Ex: +5511999999999)

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
