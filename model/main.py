import string

from Pokemon import Pokemon
from Entrenador import Entrenador
from TipoPokemon import PokemonType
import duckdb
import re #Expresiones regulares

from model.Compras import Compras
from model.TipoAddress import AddressType
from model.TipoMetodoPago import MoneyType

# Conexión a la base de datos
conen = duckdb.connect(database='pokemon_duckdb')

# Crear tabla de pokemon
conen.execute("""
CREATE TABLE IF NOT EXISTS pokemons (
    id INT PRIMARY KEY,
    name TEXT,
    type TEXT,
    height REAL,
    weight REAL,
    abilities TEXT
);
""")

#Crar tabla de entrenadores
conen.execute("""
CREATE TABLE IF NOT EXISTS entrenadores (
    id INT PRIMARY KEY,
    mail TEXT,
    phoneNumber TEXT,
    address TEXT
);
""")

# Crear tabla de compras
conen.execute("""
CREATE TABLE IF NOT EXISTS compras (
    idCompra INT PRIMARY KEY,
    fechaYHora TIMESTAMP,
    idEntrenador INT,
    idPokemon INT,
    cantidad INT,
    precioTotal REAL,
    metodoDePago TEXT,
    FOREIGN KEY (idEntrenador) REFERENCES entrenadores(id),
    FOREIGN KEY (idPokemon) REFERENCES pokemons(id)
);
""")


class PokemonManager:
    pokemon_list = []

    @staticmethod
    def menu_options():
        while True:
            print("\n-------- POKEMON MANAGER ---------")
            print("1 - Añadir Pokémon")
            print("2 - Editar Pokémon")
            print("3 - Borrar Pokémon")
            print("4 - Listar Pokémon")
            print("5 - Volver al menú principal")

            option = input("Elige una opción (1-5): ")

            actions = {
                "1": PokemonManager.add_pokemon,
                "2": PokemonManager.edit_pokemon,
                "3": PokemonManager.delete_pokemon,
                "4": PokemonManager.list_pokemon,
                "5": lambda : None # Regresar al menú principal
            }

            action = actions.get(option)
            if action:
                if option == "5":
                    break
                action()
            else:
                print("ERROR: Opción inválida.")

    @staticmethod
    def add_pokemon():
        print("\nHas elegido la opción de crear y añadir un Pokémon.")
        while True:
            try:
                id = int(input("Introduce el ID del Pokémon: "))
                if id <= 0:
                    raise ValueError ("ERROR: El ID no puede ser negativo o 0")
                idExist = conen.execute("SELECT id FROM pokemons WHERE id = ?;", (id,)).fetchall()
                if idExist:
                    print("ERROR: Este ID ya existe")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un ID valido")

        name = input("Introduce el nombre del Pokémon: ")

        print("Tipos disponibles:")
        for poke_type in PokemonType:
            print(f"- {poke_type.value}")

        while True:
            pokemon_type_input = input("Introduce el tipo del Pokémon (elige de la lista): ")
            try:
                pokemon_type = PokemonType(pokemon_type_input)
                break
            except ValueError:
                print("ERROR: Tipo de Pokémon no válido. Elige un tipo de la lista.")

        while True:
            try:
                height = float(input("Introduce la altura del Pokémon (metros): "))
                if height <= 0:
                    print("ERROR: La altura tiene que ser mayor que 0")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número válido.")

        while True:
            try:
                weight = float(input("Introduce el peso del Pokémon (kilogramos): "))
                if weight <= 0:
                    print("ERROR: El peso debe ser mayor que 0.")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número válido para el peso.")

        abilities_input = input("Introduce las habilidades del Pokémon (separado por comas): ")
        abilities = [ability.strip() for ability in abilities_input.split(",")]

        pokemon = Pokemon(id, name, pokemon_type, height, weight, abilities)
        PokemonManager.pokemon_list.append(pokemon)

        print(f"El Pokémon {name} se ha añadido correctamente!")

        conen.execute("""
            INSERT INTO pokemons (id, name, type, height, weight, abilities)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (id, name, pokemon_type.value, height, weight, ", ".join(abilities)))

    @staticmethod
    def edit_pokemon():
        print("\nHas elegido la opción de editar un Pokémon.")

        # Verificar si el Pokémon existe antes de editarlo
        while True:
            try:
                id = int(input("Introduce el ID del Pokémon que quieres editar: "))
                existing_pokemon = conen.execute("SELECT * FROM pokemons WHERE id = ?;", (id,)).fetchone()
                if not existing_pokemon:
                    print("ERROR: No existe un Pokémon con ese ID.")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número entero válido para el ID.")

        print("\nIntroduce los nuevos datos del Pokémon (presiona ENTER para mantener el valor actual)")

        # Pedir el nuevo nombre
        new_name = input(f"Nombre actual: {existing_pokemon[1]} → Nuevo nombre: ") or existing_pokemon[1]

        # Pedir el nuevo tipo (validado con el Enum)
        print("Tipos disponibles:")
        for poke_type in PokemonType:
            print(f"- {poke_type.value}")

        while True:
            new_type_input = input(f"Tipo actual: {existing_pokemon[2]} → Nuevo tipo (elige de la lista): ") or \
                             existing_pokemon[2]
            if new_type_input in PokemonType._value2member_map_:
                new_type = PokemonType(new_type_input)
                break
            print("ERROR: Tipo de Pokémon no válido. Debes elegir un tipo de la lista.")

        # Validar nueva altura
        while True:
            new_height = input(f"Altura actual: {existing_pokemon[3]} → Nueva altura (metros): ") or existing_pokemon[3]
            try:
                new_height = float(new_height)
                if new_height <= 0:
                    raise ValueError
                break
            except ValueError:
                print("ERROR: Ingresa un número válido mayor que 0.")

        # Validar nuevo peso
        while True:
            new_weight = input(f"Peso actual: {existing_pokemon[4]} → Nuevo peso (kg): ") or existing_pokemon[4]
            try:
                new_weight = float(new_weight)
                if new_weight <= 0:
                    raise ValueError
                break
            except ValueError:
                print("ERROR: Ingresa un número válido mayor que 0.")

        # Pedir nuevas habilidades
        new_abilities_input = input(
            f"Habilidades actuales: {existing_pokemon[5]} → Nuevas habilidades (separadas por comas): ") or \
                              existing_pokemon[5]
        new_abilities = ", ".join([ability.strip() for ability in new_abilities_input.split(",")])

        # Actualizar en la base de datos
        conen.execute("""
            UPDATE pokemons 
            SET name = ?, type = ?, height = ?, weight = ?, abilities = ?
            WHERE id = ?;
        """, (new_name, new_type.value, new_height, new_weight, new_abilities, id))

        print(f"Pokémon con ID ({id}) actualizado correctamente.")

    @staticmethod
    def delete_pokemon():
        id_pokemon_borrar = int(input("Introduce el ID del Pokémon a borrar: "))
        conen.execute("DELETE FROM pokemons WHERE id = ?;", (id_pokemon_borrar,))
        print(f"Pokémon con ID ({id_pokemon_borrar}) eliminado.")

    @staticmethod
    def list_pokemon():
        conen.table("pokemons").show()

class EntrenadorManager:
    entrenadores_list = []

    @staticmethod
    def menu_options():
        while True:
            print("\n-------- TRAINER MANAGER --------")
            print("1 - Añadir Entrenador")
            print("2 - Editar Entrenador")
            print("3 - Borrar Entrenador")
            print("4 - Listar Entrenador")
            print("5 - Volver al menú principal")

            option = input("Elige una opción (1-5): ")

            actions = {
                "1": EntrenadorManager.add_trainer,
                "2": EntrenadorManager.edit_trainer,
                "3": EntrenadorManager.delete_trainer,
                "4": EntrenadorManager.list_trainers,
                "5": lambda:None
            }

            action = actions.get(option)
            if action:
                if option == "5":
                    MainMenu.menu_options()
                action()
            else:
                print("ERROR: Opción inválida.")

    @staticmethod
    def add_trainer():
        print("\nHas elegido la opción de crear y añadir un Entrenador.")

        while True:
            try:
                id = int(input("Introduce el ID del Entrenador: "))
                if id <= 0:
                    raise ValueError ("ERROR: El ID no puede ser negativo")
                idExist = conen.execute("SELECT id FROM entrenadores WHERE id = ?;", (id,)).fetchall()
                if idExist:
                    print("ERROR: Este ID ya existe")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un ID valido")
        while True:
            mail = input("Introduce el correo del entrenador: ")
            if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", mail):
                break
            print("ERROR: Ingresa un correo válido (ejemplo: usuario@email.com).")
        while True:
            phoneNumber = input("Introduce el número de teléfono del entrenador: ")
            if re.match(r"^\d{7,15}$", phoneNumber):
                break
            print("ERROR: Ingresa un número de teléfono válido (7 a 15 dígitos numéricos).")

        print("Tipos disponibles:")
        for address_type in AddressType:
            print(f"- {address_type.value}")

        while True:
            address_type_input = input("Introduce el tipo de dirección (elige de la lista): ")
            try:
                address_type = AddressType(address_type_input)
                break
            except ValueError:
                print("ERROR: Tipo de Pokémon no válido. Elige un tipo de la lista.")

        entrenador = Entrenador(id, mail, phoneNumber, address_type.value)
        EntrenadorManager.entrenadores_list.append(entrenador)

        print(f"Entrenador con ID ({id}) añadido correctamente!")

        conen.execute("""
            INSERT INTO entrenadores (id, mail, phoneNumber, address)
            VALUES (?, ?, ?, ?);
        """, (id, mail, phoneNumber, address_type.value))

    @staticmethod
    def edit_trainer():

        print("\nHas elegido la opción de editar un Entrenador.")

        # Verificar si el entrenador existe antes de editarlo
        while True:
            try:
                id = int(input("Introduce el ID del Entrenador que quieres editar: "))
                existing_trainer = conen.execute("SELECT * FROM entrenadores WHERE id = ?;", (id,)).fetchone()
                if not existing_trainer:
                    print("ERROR: No existe un Entrenador con ese ID.")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número entero válido para el ID.")

        print("\nIntroduce los nuevos datos del Entrenador (presiona ENTER para mantener el valor actual)")

        # Pedir el nuevo correo (validado)
        while True:
            new_mail = input(f"Correo actual: {existing_trainer[1]} → Nuevo correo: ") or existing_trainer[1]
            if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", new_mail):
                break
            print("ERROR: Ingresa un correo válido (ejemplo: usuario@email.com).")

        # Pedir el nuevo número de teléfono (validado)
        while True:
            new_phone = input(f"Teléfono actual: {existing_trainer[2]} → Nuevo teléfono: ") or existing_trainer[2]
            if re.match(r"^\d{7,15}$", new_phone):
                break
            print("ERROR: Ingresa un número de teléfono válido (7 a 15 dígitos numéricos).")

        # Pedir nueva dirección (validado con el Enum)
        print("Tipos de dirección disponibles:")
        for tipo in AddressType:
            print(f"- {tipo.value}")

        while True:
            new_address_input = input(
                f"Dirección actual: {existing_trainer[3]} → Nueva dirección (Fisica o Virtual): ") or existing_trainer[
                                    3]
            if new_address_input in AddressType._value2member_map_:
                new_address = AddressType(new_address_input)
                break
            print("ERROR: Tipo de dirección no válido. Debes elegir 'Fisica' o 'Virtual'.")

        # Actualizar en la base de datos
        conen.execute("""
            UPDATE entrenadores 
            SET mail = ?, phoneNumber = ?, address = ?
            WHERE id = ?;
        """, (new_mail, new_phone, new_address.value, id))

        print(f"Entrenador con ID ({id}) actualizado correctamente.")
    @staticmethod
    def delete_trainer():
        id_entrenador_borrar = int(input("Introduce el ID del entrenador a borrar: "))
        conen.execute("DELETE FROM entrenadores WHERE id = ?;", (id_entrenador_borrar,))
        print(f"Entrenador con ID ({id_entrenador_borrar}) eliminado.")

    @staticmethod
    def list_trainers():
        conen.table("entrenadores").show()


class CompraManager:
    compras_list = []

    @staticmethod
    def menu_options():
        while True:
            print("\n-------- POKEMON MANAGER ---------")
            print("1 - Añadir Compra")
            print("2 - Editar Compra")
            print("3 - Borrar Compra")
            print("4 - Listar Compra")
            print("5 - Volver al menú principal")

            option = input("Elige una opción (1-5): ")

            actions = {
                "1": CompraManager.add_compra,
                "2": CompraManager,
                "3": CompraManager.delete_compra,
                "4": CompraManager.list_compras,
                "5": lambda: None  # Regresar al menú principal
            }

            action = actions.get(option)
            if action:
                if option == "5":
                    break
                action()
            else:
                print("ERROR: Opción inválida.")

    @staticmethod
    def add_compra():
        print("\nHas elegido la opción de añadir una compra.")

        # Verificar si hay Entrenadores disponibles
        entrenadores_count = conen.execute("SELECT COUNT(*) FROM entrenadores;").fetchone()[0]
        if entrenadores_count == 0:
            print("ERROR: No hay entrenadores disponibles para realizar compras.")
            return  # Terminamos la función si no hay entrenadores

        # Verificar si hay Pokémon disponibles
        pokemons_count = conen.execute("SELECT COUNT(*) FROM pokemons;").fetchone()[0]
        if pokemons_count == 0:
            print("ERROR: No hay Pokémon disponibles para comprar.")
            return  # Terminamos la función si no hay Pokémon

        # Si hay entrenadores y Pokémon disponibles, procedemos a crear la compra
        while True:
            try:
                idCompra = int(input("Introduce el ID de la compra: "))
                if idCompra <= 0:
                    raise ValueError("ERROR: El ID no puede ser negativo o 0")
                idExist = conen.execute("SELECT idCompra FROM compras WHERE idCompra = ?;", (idCompra,)).fetchall()
                if idExist:
                    print("ERROR: Este ID ya existe")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un ID valido")

        # ENTRENADOR (comprador)
        while True:
            try:
                idEntrenador = int(input("Introduce el ID del entrenador comprador: "))
                existing_trainer = conen.execute("SELECT id FROM entrenadores WHERE id = ?;",
                                                 (idEntrenador,)).fetchone()
                if not existing_trainer:
                    print("ERROR: No existe un entrenador con ese ID.")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número entero válido para el ID del entrenador.")

        # POKEMON (producto comprado)
        while True:
            try:
                idPokemon = int(input("Introduce el ID del Pokémon comprado: "))
                existing_pokemon = conen.execute("SELECT id FROM pokemons WHERE id = ?;", (idPokemon,)).fetchone()
                if not existing_pokemon:
                    print("ERROR: No existe un Pokémon con ese ID.")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número entero válido para el ID del Pokémon.")

        # CANTIDAD
        while True:
            try:
                cantidad = int(input("Introduce la cantidad de Pokémon que deseas comprar: "))
                if cantidad <= 0:
                    raise ValueError("ERROR: La cantidad debe ser mayor que 0.")
                break
            except ValueError:
                print("ERROR: Ingresa una cantidad válida (mayor que 0).")

        # PRECIO TOTAL
        while True:
            try:
                precioUnitario = float(input("Introduce el precio unitario de la compra de ese Pokémon: "))
                if precioUnitario <= 0:
                    raise ValueError("ERROR: El precio debe ser mayor que 0")
                break
            except ValueError:
                print("ERROR: Debes ingresar un precio válido.")

        # Calcular el precio total
        precioTotal = precioUnitario * cantidad
        print(f"El precio total de la compra es: {precioTotal}")

        # Método de Pago
        print("Métodos de pago disponibles:")
        for method in MoneyType:
            print(f"- {method.value}")

        while True:
            metodoDePago_input = input("Introduce el método de pago (elige de la lista): ")
            try:
                metodoDePago = MoneyType(metodoDePago_input)
                break
            except ValueError:
                print("ERROR: Método de pago no válido. Elige de la lista.")

        fechaYHora = input("Introduce la fecha y hora de la compra (YYYY-MM-DD HH:MM:SS): ")

        # Crear la compra
        compra = Compras(idCompra, fechaYHora, idEntrenador, idPokemon, cantidad, precioTotal, metodoDePago.value)
        print(f"Compra con ID ({idCompra}) añadida correctamente!")

        # Insertar en la base de datos
        conen.execute("""
                INSERT INTO compras (idCompra, fechaYHora, idEntrenador, idPokemon, cantidad, precioTotal, metodoDePago)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (idCompra, fechaYHora, idEntrenador, idPokemon, cantidad, precioTotal, metodoDePago.value))

    #EDITAR COMPRA
    @staticmethod
    def edit_compra():
        print("\nHas elegido la opción de editar una compra.")

        # Verificar si la compra existe antes de editarla
        while True:
            try:
                idCompra = int(input("Introduce el ID de la compra que quieres editar: "))
                existing_compra = conen.execute("SELECT * FROM compras WHERE idCompra = ?;", (idCompra,)).fetchone()
                if not existing_compra:
                    print("ERROR: No existe una compra con ese ID.")
                    continue
                break
            except ValueError:
                print("ERROR: Debes ingresar un número entero válido para el ID de la compra.")

        print("\nIntroduce los nuevos datos de la compra (presiona ENTER para mantener el valor actual)")

        # Pedir la nueva cantidad
        while True:
            new_cantidad = input(f"Cantidad actual: {existing_compra[4]} → Nueva cantidad: ") or existing_compra[4]
            try:
                new_cantidad = int(new_cantidad)
                if new_cantidad <= 0:
                    raise ValueError
                break
            except ValueError:
                print("ERROR: Ingresa un número válido mayor que 0.")

        # Pedir el nuevo precio total
        while True:
            new_precioTotal = input(f"Precio actual: {existing_compra[5]} → Nuevo precio total: ") or existing_compra[5]
            try:
                new_precioTotal = float(new_precioTotal)
                if new_precioTotal <= 0:
                    raise ValueError
                break
            except ValueError:
                print("ERROR: Ingresa un número válido mayor que 0.")

        # Pedir el nuevo método de pago
        print("Métodos de pago disponibles:")
        for method in MoneyType:
            print(f"- {method.value}")

        while True:
            new_metodoDePago_input = input(f"Método de pago actual: {existing_compra[6]} → Nuevo método de pago: ") or \
                                     existing_compra[6]
            try:
                new_metodoDePago = MoneyType(new_metodoDePago_input)
                break
            except ValueError:
                print("ERROR: Método de pago no válido. Elige de la lista.")

        # Actualizar en la base de datos
        conen.execute("""
            UPDATE compras 
            SET cantidad = ?, precioTotal = ?, metodoDePago = ? 
            WHERE idCompra = ?;
        """, (new_cantidad, new_precioTotal, new_metodoDePago.value, idCompra))

        print(f"Compra con ID ({idCompra}) actualizada correctamente.")

    #BORRAR COMPRA
    @staticmethod
    def delete_compra():

        comprar_count = conen.execute("SELECT COUNT(*) FROM compras").fetchone()[0]
        if comprar_count == 0:
            print("ERROR: No existe ninguna compra.")
            return
        idCompra = int(input("Introduce el ID de la compra a eliminar: "))
        conen.execute("DELETE FROM compras WHERE idCompra = ?;", (idCompra,))
        print(f"Compra con ID ({idCompra}) eliminada.")

    #LISTAR COMPRAS
    @staticmethod
    def list_compras():
        conen.table("compras").show()


class MainMenu:
    @staticmethod
    def menu_options():
        while True:
            print("\n-------- MAIN MENU ---------")
            print("1 - Gestionar Pokémon")
            print("2 - Gestionar Entrenadores")
            print("3 - Gestionar Compras")
            print("4 - Salir")

            option = input("Elige una opción (1-4): ")

            if option == "1":
                PokemonManager.menu_options()
            elif option == "2":
                EntrenadorManager.menu_options()
            elif option == "3":
                CompraManager.menu_options()
            elif option == "4":
                print("Saliendo del programa...")
                exit()
            else:
                print("ERROR: Opción inválida.")


if __name__ == "__main__":
    MainMenu.menu_options()
