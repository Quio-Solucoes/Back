CORES_DISPONIVEIS = [
    {"id": "BRA", "nome": "Branco"},
    {"id": "PRE", "nome": "Preto"},
    {"id": "AME", "nome": "Amadeirado"},
]

MATERIAIS_DISPONIVEIS = [
    {"id": "MDP", "nome": "MDP"},
    {"id": "MDF", "nome": "MDF"},
    {"id": "ALU", "nome": "Alumínio"},
]

DIMENSOES_PRESETS = {
    "P": {"label": "📐 Padrão", "L": None, "P": None},
    "M": {"label": "📐 Médio", "L": 600, "P": 600},
    "G": {"label": "📐 Grande", "L": 800, "P": 600},
}

CATALOGO_SUBSTITUICOES = {
    "puxador": [
        {
            "id": "PUX01",
            "nome": "Puxador Simples Cromado",
            "preco_unitario": 30.00
        },
        {
            "id": "PUX02",
            "nome": "Puxador Alça Alumínio Escovado",
            "preco_unitario": 55.00
        },
        {
            "id": "PUX03",
            "nome": "Puxador Zen Preto Fosco",
            "preco_unitario": 85.00
        },
        {
            "id": "PUX04",
            "nome": "Perfil Cava Embutido",
            "preco_unitario": 120.00
        },
    ],

    "gaveta": [
        {
            "id": "GAV01",
            "nome": "Gaveta Simples Metálica",
            "preco_unitario": 120.00
        },
        {
            "id": "GAV02",
            "nome": "Gaveta Invisível Soft Close",
            "preco_unitario": 240.00
        },
    ],

    "dobradiça": [
        {
            "id": "DOB01",
            "nome": "Dobradiça Simples",
            "preco_unitario": 18.00
        },
        {
            "id": "DOB02",
            "nome": "Dobradiça Soft Close",
            "preco_unitario": 32.00
        },
    ],
}