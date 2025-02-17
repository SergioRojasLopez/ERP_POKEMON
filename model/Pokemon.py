class Pokemon:
    def __init__(self, id, name, pokemon_type, height, weight, abilities):
        self.id = id
        self.name = name
        self.pokemon_type = pokemon_type
        self.height = height
        self.weight = weight
        self.abilities = abilities

    def display_info(self):
        print(f"\n------ POKEMON INFO ------")
        print(f"ID: {self.id}")
        print(f"Nombre: {self.name}")
        print(f"Tipo: {self.pokemon_type.value}")
        print(f"Altura: {self.height} m")
        print(f"Peso: {self.weight} kg")
        print(f"Habilidades: {', '.join(self.abilities)}")
        print("----------------------------")