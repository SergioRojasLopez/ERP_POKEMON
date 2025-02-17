class Compras:
    def __init__(self, idCompra, fechaYHora,entrenadorComprador,pokemonComprado,cantidad,precioTotal,metodoDePago ):
        self.idCompra = idCompra
        self.fechaYHora = fechaYHora
        self.entrenadorComprador = entrenadorComprador
        self.pokemonComprado = pokemonComprado
        self.cantidad = cantidad
        self.precioTotal = precioTotal
        self.metodoDePago = metodoDePago


    def display_info(self):
        print("\n ------ COMPRAS INFO -------")
        print(f"idCompra:", self.idCompra)
        print(f"fechaYHora:", self.fechaYHora)
        print(f"entrenadorComprador:", self.entrenadorComprador)
        print(f"pokemonComprado:", self.pokemonComprado)
        print(f"cantidad:", self.cantidad)
        print(f"precioTotal:", self.precioTotal)
        print(f"metodoDePago",self.metodoDePago)
        print("----------------------------")