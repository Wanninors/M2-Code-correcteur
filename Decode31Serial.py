import serial

# Fonction pour encoder BCH(31,8) t=2
def bch_encode_31_8(binary_message):
    # Définir le polynôme générateur pour BCH(31,8)
    generator = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1]  # g(x) pour BCH(31,8)
    
    # Convertir le message binaire en une liste d'entiers
    binary_message = [int(bit) for bit in binary_message]

    # Ajouter des bits redondants (x^23) à la fin du message
    shifted_message = binary_message + [0] * 23

    # Effectuer une division polynomiale pour calculer le reste
    remainder = shifted_message[:]
    for i in range(len(binary_message)):
        if remainder[i] == 1:  # Si le bit courant est 1, effectuer XOR avec le générateur
            for j in range(len(generator)):
                remainder[i + j] ^= generator[j]

    # Ajouter le reste calculé aux bits d'information pour former le message encodé
    encoded_message = binary_message + remainder[len(binary_message):]

    return encoded_message

# Fonction pour décoder BCH(31,8) t=2
def bch_decode_31_8(encoded_message):
    # Définir le polynôme générateur pour BCH(31,8)
    generator = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1]  # g(x) pour BCH(31,8)

    # Calculer le syndrome en effectuant une division polynomiale
    syndrome = encoded_message[:]
    for i in range(len(encoded_message) - len(generator) + 1):
        if syndrome[i] == 1:  # Si le bit courant est 1, effectuer XOR avec le générateur
            for j in range(len(generator)):
                syndrome[i + j] ^= generator[j]

    syndrome = syndrome[len(encoded_message) - len(generator):]  # Conserver uniquement les bits du syndrome

    # Vérification explicite du syndrome
    print(f"Syndrome calculé : {syndrome}")

    # Si le syndrome est nul, il n'y a pas d'erreurs
    if sum(syndrome) == 0:
        return encoded_message[:8], "No errors", []

    # Essayer de corriger jusqu'à deux erreurs
    corrected_message = encoded_message[:]
    error_positions = []

    # Tenter de corriger une erreur
    for i in range(len(encoded_message)):
        corrected_message[i] ^= 1  # Inverser le bit courant

        # Recalculer le syndrome après inversion
        test_syndrome = corrected_message[:]
        for k in range(len(test_syndrome) - len(generator) + 1):
            if test_syndrome[k] == 1:
                for j in range(len(generator)):
                    test_syndrome[k + j] ^= generator[j]

        test_syndrome = test_syndrome[len(test_syndrome) - len(generator):]

        if sum(test_syndrome) == 0:  # Si le syndrome est nul, la correction a réussi
            error_positions.append(i)
            return corrected_message[:8], "Errors corrected", error_positions

        corrected_message[i] ^= 1  # Restaurer si la correction échoue

    # Tenter de corriger deux erreurs
    for i in range(len(encoded_message)):
        for j in range(i + 1, len(encoded_message)):
            corrected_message[i] ^= 1
            corrected_message[j] ^= 1

            # Recalculer le syndrome après inversion de deux bits
            test_syndrome = corrected_message[:]
            for k in range(len(test_syndrome) - len(generator) + 1):
                if test_syndrome[k] == 1:
                    for m in range(len(generator)):
                        test_syndrome[k + m] ^= generator[m]

            test_syndrome = test_syndrome[len(test_syndrome) - len(generator):]

            if sum(test_syndrome) == 0:  # Si le syndrome est nul, la correction a réussi
                error_positions.extend([i, j])
                print(f"Corrections appliquées aux positions {i} et {j}")
                return corrected_message[:8], "Errors corrected", error_positions

            corrected_message[i] ^= 1
            corrected_message[j] ^= 1  # Restaurer si la correction échoue

    # Si aucune correction n'a pu être faite
    print("Erreur non corrigée avec le syndrome :", syndrome)
    return encoded_message[:8], "Errors detected but not corrected", []

# Fonction pour lire un message depuis la liaison série
def read_serial(port="COM3", baudrate=9600, expected_characters=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)  # Initialiser la liaison série
        print("En attente de données...")
        buffer = []

        # Lire les données jusqu'à ce que le nombre attendu de bits soit atteint
        while len(buffer) < expected_characters * 31:
            data = ser.read(32)  # Lire un bloc de données
            if data:
                for byte in data:
                    for i in range(8):
                        buffer.append((byte >> (7 - i)) & 1)

        # Découper les blocs en trames de 31 bits
        encoded_messages = []
        while len(buffer) >= 31:
            encoded_messages.append(buffer[:31])
            buffer = buffer[31:]

        ser.close()  # Fermer la liaison série
        print("Messages reçus via la liaison série :", encoded_messages)
        return encoded_messages

    except serial.SerialException as e:
        print("Erreur lors de la lecture de la liaison série :", e)
        return None

# Fonction pour introduire des erreurs dans un caractère spécifique
def introduce_errors_multiple(encoded_messages):
    # Demander à l'utilisateur de choisir un caractère à corrompre
    char_index = int(input(f"Entrez l'index du caractère (0-{len(encoded_messages)-1}) que vous souhaitez corrompre : "))
    if 0 <= char_index < len(encoded_messages):
        encoded_message = encoded_messages[char_index]
        num_errors = int(input("Combien d'erreurs voulez-vous introduire (1 ou 2) ? : "))
        if num_errors not in [1, 2]:
            print("Nombre d'erreurs non valide.")
            return encoded_messages

        positions = []
        for _ in range(num_errors):
            # Demander à l'utilisateur les positions des erreurs
            pos = int(input(f"Entrez la position de l'erreur (0-30) dans le caractère {char_index} : "))
            if 0 <= pos < len(encoded_message):
                positions.append(pos)
                encoded_message[pos] ^= 1  # Inverser le bit pour introduire une erreur
            else:
                print("Position invalide.")
        print(f"Erreurs introduites aux positions {positions} pour le caractère {char_index}")
        encoded_messages[char_index] = encoded_message
    else:
        print("Index de caractère invalide.")
    return encoded_messages

# Programme principal
def main():
    # Demander à l'utilisateur le nombre de caractères attendus
    expected_characters = int(input("Combien de caractères attendez-vous ? "))

    print("Démarrage de la réception...")
    received_messages = read_serial(expected_characters=expected_characters)
    if received_messages is None:
        return

    # Afficher les messages reçus
    for idx, encoded_message in enumerate(received_messages):
        print(f"Message encodé reçu pour le caractère {idx} : {encoded_message}")

    # Proposer d'introduire des erreurs
    user_choice = input("Voulez-vous introduire des erreurs dans un caractère ? (oui/non) : ").strip().lower()
    if user_choice == "oui":
        received_messages = introduce_errors_multiple(received_messages)

    # Décoder chaque message
    decoded_message = ""
    for encoded_message in received_messages:
        decoded_char, status, error_positions = bch_decode_31_8(encoded_message)
        print(f"Caractère décodé : {decoded_char}, Statut : {status}")
        decoded_message += chr(int("".join(map(str, decoded_char)), 2))

    print("Message complet décodé :", decoded_message)

if __name__ == "__main__":
    main()
