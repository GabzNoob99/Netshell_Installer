import urllib.request
import os

URL_EXE = "https://raw.githubusercontent.com/GabzNoob99/NetShell/main/ntsl_1.6.exe"

print("""
instalador do NetShell
aguardando respostas...
      """)

def instalar(pasta_destino, callback):
    """Baixa o executável mostrando progresso via callback.

    O callback recebe strings. Mensagens normais são exibidas nos logs.
    Mensagens de progresso são enviadas na forma: "PROGRESS:<percent>"
    """
    try:
        callback("Iniciando download de NetShell...")

        caminho = os.path.join(pasta_destino, "NetShell.exe")

        def reporthook(blocknum, blocksize, totalsize):
            if totalsize > 0:
                downloaded = blocknum * blocksize
                percent = int(downloaded * 100 / totalsize)
                if percent > 100:
                    percent = 100
                callback(f"PROGRESS:{percent}")
            else:
                callback("Baixando...")

        urllib.request.urlretrieve(URL_EXE, caminho, reporthook)

        callback("PROGRESS:100")
        callback("Instalação concluída!")

    except Exception as erro:
        callback(f"Erro: {erro}")