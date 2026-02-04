from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
import unicodedata

from states import ESTADOS
from models import Componente
from repositories import (
    buscar_movel_por_nome,
    buscar_catalogo_componentes,
)
from services import criar_configuracao_padrao
from utils import gerar_resumo_configuracao, resposta_com_opcoes



def normalizar(txt):
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    if txt.endswith("s"):
        txt = txt[:-1]
    return txt


app = Flask(__name__, template_folder="templates", static_folder="static")

CORS(app, resources={
    r"/chat": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

conversas = {}
CATALOGO = buscar_catalogo_componentes()


class Conversa:
    def __init__(self):
        self.estado = ESTADOS["INICIO"]
        self.configuracao = None
        self.categoria_selecionada = None


# ─────────────────────────────
# ROTAS
# ─────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")



@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"response": "❌ Requisição inválida"}), 400
            
        message = str(data.get("message", "")).strip()
        session_id = data.get("session_id", "default")
    except Exception as e:
        print(f"❌ Erro ao processar JSON: {e}")
        return jsonify({"response": "❌ Erro ao processar requisição"}), 400

    conversa = conversas.setdefault(session_id, Conversa())

    ##### INÍCIO

    if conversa.estado == ESTADOS["INICIO"]:
        movel = buscar_movel_por_nome(message)

        if not movel:
            return jsonify({"response": "❌ Móvel não encontrado. Tente: Guarda-roupa, Cozinha, Rack..."})

        conversa.configuracao = criar_configuracao_padrao(movel)
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return jsonify(
            resposta_com_opcoes(
                gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "📏 Dimensão"},
                    {"id": "2", "label": "🎨 Cor"},
                    {"id": "3", "label": "🪵 Material"},
                    {"id": "4", "label": "🔧 Componentes"},
                    {"id": "5", "label": "✅ Confirmar"},
                ],
            )
        )

    # MENU PRINCIPAL
    if conversa.estado == ESTADOS["CONFIGURANDO_MOVEL"]:

        # DIMENSÃO
        if message == "1":
            conversa.estado = ESTADOS["ALTERAR_DIMENSAO"]
            return jsonify({
                "response": (
                    "📏 Digite as dimensões no formato:\n\n"
                    "L x A x P\n\n"
                    "Exemplo:\n"
                    "800 x 700 x 600"
                )
            })

        # COR
        if message == "2":
            conversa.estado = ESTADOS["ESCOLHER_COR"]
            return jsonify(
                resposta_com_opcoes(
                    "🎨 Escolha a cor:",
                    [
                        {"id": "branco", "label": "Branco"},
                        {"id": "preto", "label": "Preto"},
                        {"id": "amadeirado", "label": "Amadeirado"},
                    ],
                )
            )

        # MATERIAL
        if message == "3":
            conversa.estado = ESTADOS["ESCOLHER_MATERIAL"]
            return jsonify(
                resposta_com_opcoes(
                    "🪵 Escolha o material:",
                    [
                        {"id": "mdp", "label": "MDP"},
                        {"id": "mdf", "label": "MDF"},
                        {"id": "aluminio", "label": "Alumínio"},
                    ],
                )
            )

        # COMPONENTES
        if message == "4":
            categorias = sorted(
                {normalizar(c.categoria_funcional) for c in conversa.configuracao.componentes}
            )

            conversa.estado = ESTADOS["ESCOLHER_CATEGORIA_COMPONENTE"]

            return jsonify(
                resposta_com_opcoes(
                    "🔧 Qual componente deseja alterar?",
                    [{"id": c, "label": c.capitalize()} for c in categorias]
                    + [{"id": "0", "label": "⬅ Voltar"}],
                )
            )

        # confirmar
        if message == "5":
            total = conversa.configuracao.total_geral()
            return jsonify({
                "response": f"✅ Orçamento finalizado!\n\nTotal final: R$ {total:.2f}\n\nObrigado por usar nosso sistema!"
            })

    # dimensão
    if conversa.estado == ESTADOS["ALTERAR_DIMENSAO"]:
        try:
            partes = message.lower().replace(" ", "").split("x")
            L, A, P = map(float, partes)

            conversa.configuracao.L_mm = L
            conversa.configuracao.A_mm = A
            conversa.configuracao.P_mm = P
            conversa.configuracao.recalcular_preco_por_area()

            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

            return jsonify(
                resposta_com_opcoes(
                    "📏 Dimensão atualizada!\n\n"
                    + gerar_resumo_configuracao(conversa.configuracao),
                    [
                        {"id": "1", "label": "📏 Dimensão"},
                        {"id": "2", "label": "🎨 Cor"},
                        {"id": "3", "label": "🪵 Material"},
                        {"id": "4", "label": "🔧 Componentes"},
                        {"id": "5", "label": "✅ Confirmar"},
                    ],
                )
            )
        except Exception as e:
            print(f"❌ Erro ao processar dimensão: {e}")
            return jsonify({"response": "❌ Formato inválido. Use: 800 x 700 x 600"})

   #cor
    if conversa.estado == ESTADOS["ESCOLHER_COR"]:
        conversa.configuracao.cor = message.capitalize()
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return jsonify(
            resposta_com_opcoes(
                gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "📏 Dimensão"},
                    {"id": "2", "label": "🎨 Cor"},
                    {"id": "3", "label": "🪵 Material"},
                    {"id": "4", "label": "🔧 Componentes"},
                    {"id": "5", "label": "✅ Confirmar"},
                ],
            )
        )

    #material
    if conversa.estado == ESTADOS["ESCOLHER_MATERIAL"]:
        conversa.configuracao.material = message.upper()
        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return jsonify(
            resposta_com_opcoes(
                gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "📏 Dimensão"},
                    {"id": "2", "label": "🎨 Cor"},
                    {"id": "3", "label": "🪵 Material"},
                    {"id": "4", "label": "🔧 Componentes"},
                    {"id": "5", "label": "✅ Confirmar"},
                ],
            )
        )

   #Componente
    if conversa.estado == ESTADOS["ESCOLHER_CATEGORIA_COMPONENTE"]:
        if message == "0":
            conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]
            return jsonify(
                resposta_com_opcoes(
                    "↩ Voltando ao menu principal...\n\n" + gerar_resumo_configuracao(conversa.configuracao),
                    [
                        {"id": "1", "label": "📏 Dimensão"},
                        {"id": "2", "label": "🎨 Cor"},
                        {"id": "3", "label": "🪵 Material"},
                        {"id": "4", "label": "🔧 Componentes"},
                        {"id": "5", "label": "✅ Confirmar"},
                    ],
                )
            )

        categoria = normalizar(message)
        if categoria not in CATALOGO:
            return jsonify({"response": "❌ Categoria inválida. Tente novamente."})

        conversa.categoria_selecionada = categoria
        conversa.estado = ESTADOS["ESCOLHER_COMPONENTE"]

        return jsonify(
            resposta_com_opcoes(
                "🔁 Escolha o novo componente:",
                [
                    {
                        "id": c["id"],
                        "label": f'{c["nome"]} (R$ {c["preco_unitario"]:.2f})',
                    }
                    for c in CATALOGO[categoria]
                ],
            )
        )

    # ESCOLHER COMPONENTE
    if conversa.estado == ESTADOS["ESCOLHER_COMPONENTE"]:
        categoria = conversa.categoria_selecionada

        opcao = next(
            (c for c in CATALOGO[categoria] if c["id"] == message),
            None,
        )

        if not opcao:
            return jsonify({"response": "❌ Opção inválida. Tente novamente."})

        conversa.configuracao.componentes = [
            c
            for c in conversa.configuracao.componentes
            if normalizar(c.categoria_funcional) != categoria
        ]

        conversa.configuracao.componentes.append(
            Componente(
                nome=opcao["nome"],
                categoria_funcional=categoria,
                quantidade=1,
                preco_unitario=opcao["preco_unitario"],
            )
        )

        conversa.estado = ESTADOS["CONFIGURANDO_MOVEL"]

        return jsonify(
            resposta_com_opcoes(
                "✅ Componente atualizado!\n\n"
                + gerar_resumo_configuracao(conversa.configuracao),
                [
                    {"id": "1", "label": "📏 Dimensão"},
                    {"id": "2", "label": "🎨 Cor"},
                    {"id": "3", "label": "🪵 Material"},
                    {"id": "4", "label": "🔧 Componentes"},
                    {"id": "5", "label": "✅ Confirmar"},
                ],
            )
        )

    return jsonify({"response": "❓ Não entendi. Tente novamente."})


#Endpoint de health check para verificar se o backend está rodando
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend Flask rodando com sucesso! ✅"
    })


# Endpoint para resetar uma conversa específica
@app.route("/reset/<session_id>", methods=["POST"])
def reset_conversa(session_id):
    if session_id in conversas:
        del conversas[session_id]
        return jsonify({"response": "✅ Conversa resetada com sucesso!"})
    return jsonify({"response": "⚠️ Conversa não encontrada."})


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Servidor Flask iniciado!")
    print("📍 Rodando em: http://localhost:5001")
    print("💬 Endpoint do chat: http://localhost:5001/chat")
    print("🏥 Health check: http://localhost:5001/health")
    print("=" * 60)
    app.run(debug=True, port=5001)