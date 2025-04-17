import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timezone, timedelta
import base64
import os
import logging
import urllib3
from dotenv import load_dotenv

# Desabilitar avisos de SSL não verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def criar_sessao():
    try:
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry, pool_maxsize=10)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {e}")
        return None

session = criar_sessao()

def fazer_requisicao(url, json, headers):
    try:
        if not session:
            logger.error("Sessão não inicializada")
            return None
            
        response = session.post(url, json=json, headers=headers, timeout=60, verify=False)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        logger.error(f"Timeout na requisição para {url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Erro de conexão ao acessar {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
    return None

def alterar_campo_card(card_id, field_id, novo_valor):
    try:
        url = "https://api.pipefy.com/graphql"
        load_dotenv()
        headers = {
            "Authorization": f"Bearer {os.getenv('PIPEFY_TOKEN')}",
            "Content-Type": "application/json"
        }
        query = f"""
        mutation {{
            updateCardField(input: {{
                card_id: {card_id},
                field_id: "{field_id}",
                new_value: "{novo_valor}"
            }}) {{
                success
            }}
        }}
        """
        response = fazer_requisicao(url, json={"query": query}, headers=headers)
        return response.json() if response else {"error": "No response received"}
    except Exception as e:
        logger.error(f"Erro ao alterar campo do card: {e}")
        return {"error": str(e)}

def buscar_email(nome_da_empresa):
    try:
        url = "https://api.pipefy.com/graphql"
        load_dotenv()
        headers = {
            "Authorization": f"Bearer {os.getenv('PIPEFY_TOKEN')}",
            "Content-Type": "application/json"
        }
        query = f"""
        {{
            findRecords(tableId: "zaSzaB-T", search: {{
                fieldId: "nome_da_empresa",
                fieldValue: "{nome_da_empresa}"
            }}) {{
                edges {{
                    node {{
                        fields {{
                            field {{ id }}
                            value
                        }}
                    }}
                }}
            }}
        }}
        """
        response = fazer_requisicao(url, json={'query': query}, headers=headers)
        if not response:
            return []
        
        data = response.json()
        return [
            field["value"]
            for edge in data.get("data", {}).get("findRecords", {}).get("edges", [])
            for field in edge["node"].get("fields", [])
            if field["field"]["id"] == "email_do_contato"
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar email: {e}")
        return []

def processar_anexos(file_urls):
    anexos = {}
    tipos_arquivo = {
        "pdf": "application/pdf",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "zip": "application/zip"
    }
    
    try:
        for idx, url in enumerate(filter(None, file_urls)):
            try:
                extensao = url.split('.')[-1].split('?')[0].lower()
                response = requests.get(url, timeout=30, verify=False)
                response.raise_for_status()
                content = base64.b64encode(response.content).decode('utf-8')
                
                anexos[f"file{idx + 1}"] = {
                    "name": f"anexo{idx + 1}.{extensao}",
                    "type": tipos_arquivo.get(extensao, "application/octet-stream"),
                    "content": content
                }
            except Exception as e:
                logger.error(f"Erro ao processar anexo {url}: {e}")
                continue
        return anexos
    except Exception as e:
        logger.error(f"Erro ao processar anexos: {e}")
        return {}

def gerar_links_anexos(urls):
    if not urls:
        return ""
    try:
        links = "".join([
            f"<br><a href='{url}' style='text-decoration: none; color: #007bff;'>{os.path.basename(url.split('?')[0])}</a>"
            for url in urls if url
        ])
        return f"<div style='border: 1px solid #ccc; padding: 10px; margin-top: 10px;'><h3>Clique aqui para baixar os Anexos:</h3>{links}</div>"
    except Exception as e:
        logger.error(f"Erro ao gerar links dos anexos: {e}")
        return ""

def definir_destinatarios(departamento, emails):
    try:
        departamentos = {
            "FISCAL": ("fiscal@odoscontabilidade.com.br", ["samuel@odoscontabilidade.com.br"]),
            "CONTÁBIL": ("contabil@odoscontabilidade.com.br", ["nathalialeal@odoscontabilidade.com.br"]),
            "LEGAL": ("centraldesolucoes@odoscontabilidade.com.br", ["barbara@odoscontabilidade.com.br"]),
            "SUCESSO": ("sucesso@odoscontabilidade.com.br", [])
        }
        email_reply, emails_adicionais = departamentos.get(departamento, ("", []))
        if isinstance(emails, list):
            emails.extend(emails_adicionais)
            emails.append("integracao.odos@gmail.com")
            # Remover duplicatas e valores vazios
            emails = list(filter(None, set(emails)))
        return email_reply, emails
    except Exception as e:
        logger.error(f"Erro ao definir destinatários: {e}")
        return "", []

def main(input):
    try:
        if not isinstance(input, dict):
            raise ValueError("Input inválido")

        file_urls = input.get("anexos", "").split(", ")
        if not any(file_urls):
            raise Exception("Nenhum arquivo encontrado.")
        
        anexos = processar_anexos(file_urls)
        if not anexos:
            logger.warning("Nenhum anexo foi processado.")
            raise Exception("Nenhum anexo processado.")
        
        corpo_email = f"{input.get('corpo_do_email', '')} {gerar_links_anexos(file_urls)}"
        
        emails = buscar_email(input.get("nome_da_empresa"))
        email_reply, emails = definir_destinatarios(input.get("departamento"), emails)
        
        if not emails:
            raise Exception("Nenhum destinatário encontrado.")
        
        data = {
            "host_smtp": "cloud66.mailgrid.net.br",
            "usuario_smtp": "smtp@mkt.odoscontabilidade.com.br",
            "senha_smtp": "y6lORKQXNd",
            "emailRemetente": "smtp@mkt.odoscontabilidade.com.br",
            "nomeRemetente": "Odos",
            "emailReply": email_reply,
            "emailDestino": emails,
            "assunto": input.get("assunto", ""),
            "mensagem": f"""
            <html>
            <body>
                <div class='frame'>
                    <table>
                        <tr><td><h1 style='color: black;'>oDos</h1></td></tr>
                        <tr><td class='content'><p class='large-text'>{input.get("tipo_de_solicitacao", "")} está concluída!</p></td></tr>
                        <tr><td class='content'><p class='merge-text'>{corpo_email}</p>
                        <p>Obrigado,<br>ODOS ACELERADORA<br><a href='mailto:{email_reply}'>{email_reply}</a><br>(98) 3022-7277</p></td></tr>
                        <tr><td class='footer'><p>© 2024 ODOS Contabilidade. Todos os direitos reservados.</p></td></tr>
                    </table>
                </div>
            </body>
            </html>
            """,
            "mensagemTipo": "html",
            "mensagemEncoding": "quoted-printable",
            "mensagemAlt": corpo_email,
            "mensagemAnexos": anexos
        }
        
        resp = fazer_requisicao("https://api.mailgrid.net.br/send/", json=data, headers={
            "Authorization": "Content-Type: application/json",
            "Content-Type": "application/json"
        })
        
        if not resp:
            raise Exception("Falha ao enviar e-mail.")
        
        data_e_hora = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M:%S")
        alterar_campo_card(
            input.get("card_id"),
            "informa_es_do_email",
            f"📧 Email enviado com sucesso para os destinatários: {', '.join(emails)}. ⏰ Enviado em: {data_e_hora}"
        )
        
        return {
            "status_code": resp.status_code,
            "message": {
                "type": "E-mail enviado com sucesso",
                "message_text": f"E-mail enviado para: {', '.join(emails)} com os anexos: {list(anexos.keys())}"
            }
        }
    except Exception as e:
        logger.error(f"Erro na função main: {e}")
        return {
            "status_code": 500,
            "message": {
                "type": "Erro ao enviar e-mail",
                "message_text": str(e)
            }
        }


input = {
    "card_id": "1125069880",
    "tipo_de_solicitacao": "Solicitação de Abertura de Conta",
    "corpo_do_email": "Este é o corpo do e-mail.",
    "assunto": "Assunto do E-mail",
    "nome_da_empresa": "ELIVELTON (NÃO APAGAR) TESTE",
    "departamento": "LEGAL",
    "anexos": "link1, link2, link3"
}
if __name__ == "__main__":
    main(input)
    