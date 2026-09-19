import logging
import requests
from monitor import formatDate
import truststore

truststore.inject_into_ssl()

# Configuracao das URLs
BASE_URL = "https://tremdepassageiros.vale.com"
PESQUISA_URL = f"{BASE_URL}/sgpweb/rest/externo/VendaInternet/publico/pesquisaPassagem"

# Inicializacao global da sessao
SESSION = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=utf-8",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/",
}

# Atualiza cookies da sessao
def updateCookies() :
    try:
        # Limpa anteriores se houver
        SESSION.cookies.clear() 

        # Lanca requisicao na pagina para gerar cookies
        SESSION.get(BASE_URL, headers=HEADERS, timeout=15)

        logging.info("Sessão HTTP inicializada com a Vale.")
        return True
    
    except requests.RequestException as e:
        logging.error(f"Erro ao inicializar sessão com a Vale: {e}")
        return False

# Checa passagens
def check(payload: dict) -> list :

    # Verifica ausencia de cookies -> gera se nao houver -> se nao gerar retorna
    if not SESSION.cookies :   
        if not updateCookies() : return

    try:
        # Lanca requisicao de busca
        response = SESSION.post(PESQUISA_URL, headers=HEADERS, json=payload, timeout=30)

        # Se a sessao expirou no servidor da Vale -> renova cookies -> se nao renovar retorna
        if response.status_code in (401, 403):
            logging.warning("Sessão expirada. Renovando...")
            if not updateCookies() : return

            # Tenta novamente
            response = SESSION.post(PESQUISA_URL, headers=HEADERS, json=payload, timeout=30)

        response.raise_for_status()

        dados = response.json()
        return dados.get("passagensIda", [])

    except requests.RequestException as e:
        logging.error(f"Erro de conexão: {e}")

    return []

# Gera o payload da requisicao
def genPayload(monitor) :    
    return {
        "codigoFerrovia": "03",
        "codigoLocalOrigem": monitor["origem"],
        "codigoLocalDestino": monitor["destino"],
        "dataIda": formatDate(monitor["data"]),
        "detalheVenda": [
            {
                "detalhe": monitor["detalhe"],
                "qtd": monitor["quantidade"],
                "funcionario": False
            }
        ],
        "tremFerias": False
}