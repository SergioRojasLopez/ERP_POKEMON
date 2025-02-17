class Entrenador:
    def __init__(self, id, mail, phone_number, address):
        self.id = id
        self.mail = mail
        self.phone_number = phone_number
        self.address = address

    def display_info(self):
        print("\n------ ENTRENADOR INFO ------")
        print(f"ID: {self.id}")
        print(f"Correo: {self.mail}")
        print(f"Teléfono: {self.phone_number}")
        print(f"Dirección: {self.address}")
        print("----------------------------")