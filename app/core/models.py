from __future__ import annotations


class Movel:
    def __init__(
        self,
        id,
        nome,
        tipo,
        material,
        cor,
        preco_base,
        L_mm,
        A_mm,
        P_mm,
        area,
        descricao,
    ):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.material = material
        self.cor = cor
        self.preco_base = preco_base
        self.L_mm = L_mm
        self.A_mm = A_mm
        self.P_mm = P_mm
        self.area = area
        self.descricao = descricao


class Componente:
    def __init__(
        self,
        nome,
        categoria_funcional,
        quantidade,
        preco_unitario,
        material=None,
        cor=None,
    ):
        self.nome = nome
        self.categoria_funcional = categoria_funcional
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.material = material
        self.cor = cor

    def total(self):
        return self.quantidade * self.preco_unitario


class ConfiguracaoMovel:
    def __init__(self, movel):
        self.movel = movel
        self.componentes = []

        self.L_mm = movel.L_mm
        self.A_mm = movel.A_mm
        self.P_mm = movel.P_mm

        self.material = movel.material
        self.cor = movel.cor

        self.preco_atual = movel.preco_base

    def area_atual(self):
        return (self.L_mm / 1000) * (self.P_mm / 1000)

    def recalcular_preco_por_area(self):
        fator = self.area_atual() / self.movel.area
        self.preco_atual = self.movel.preco_base * fator

    def total_componentes(self):
        return sum(c.total() for c in self.componentes)

    def total_geral(self):
        return self.preco_atual + self.total_componentes()

