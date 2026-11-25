"""
Trecho do gerenciador do Clica & Pede (versão simplificada).

Publica o catálogo da loja no GitHub pela API, sem precisar ter o Git
instalado no computador: compara os arquivos locais com os do repositório
e envia só o que mudou, num único commit. A Cloudflare Pages percebe o
commit novo e atualiza o site sozinha.
"""

import base64
import hashlib
import json
import urllib.request
from datetime import datetime

API = "https://api.github.com"


def gh(caminho, token, metodo="GET", dados=None):
    """Faz uma chamada à API do GitHub e devolve a resposta em JSON."""
    req = urllib.request.Request(
        API + caminho,
        method=metodo,
        data=json.dumps(dados).encode() if dados is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resposta:
        return json.load(resposta)


def sha_do_arquivo(caminho):
    """Calcula o mesmo SHA que o Git usa, para comparar sem baixar nada."""
    with open(caminho, "rb") as f:
        dados = f.read()
    return hashlib.sha1(f"blob {len(dados)}\0".encode() + dados).hexdigest()


def publicar(repo, branch, token, arquivos):
    """Envia para o GitHub só os arquivos do catálogo que mudaram.

    Devolve quantos arquivos foram publicados (0 quando já está tudo igual).
    """
    api = f"/repos/{repo}"

    # Situação atual do repositório
    head = gh(f"{api}/git/ref/heads/{branch}", token)["object"]["sha"]
    base_tree = gh(f"{api}/git/commits/{head}", token)["tree"]["sha"]
    arvore = gh(f"{api}/git/trees/{base_tree}?recursive=1", token)
    remoto = {e["path"]: e["sha"] for e in arvore["tree"] if e["type"] == "blob"}

    # Compara arquivo por arquivo e sobe só o que é diferente
    mudancas = []
    for caminho in arquivos:
        if remoto.get(caminho) == sha_do_arquivo(caminho):
            continue  # já está igual no GitHub
        with open(caminho, "rb") as f:
            conteudo = base64.b64encode(f.read()).decode("ascii")
        blob = gh(f"{api}/git/blobs", token, "POST",
                  {"content": conteudo, "encoding": "base64"})
        mudancas.append({"path": caminho, "mode": "100644",
                         "type": "blob", "sha": blob["sha"]})

    if not mudancas:
        return 0

    # Junta tudo num único commit e move a branch para ele
    nova_arvore = gh(f"{api}/git/trees", token, "POST",
                     {"base_tree": base_tree, "tree": mudancas})
    commit = gh(f"{api}/git/commits", token, "POST", {
        "message": f"Atualização do catálogo ({datetime.now():%d/%m/%Y %H:%M})",
        "tree": nova_arvore["sha"],
        "parents": [head],
    })
    gh(f"{api}/git/refs/heads/{branch}", token, "PATCH", {"sha": commit["sha"]})
    return len(mudancas)
