import serial

# Fonction pour encoder BCH(15,7) t=2
def bch_encode_15_7(binary_message):
    generator = [1, 1, 1, 0, 1, 0, 0, 0, 1]  # g(x) pour BCH(15,7)
    
    # Convertir le message binaire en liste d'entiers
    binary_message = [int(bit) for bit in binary_message]

    # Ajouter les bits redondants (x^8)
    shifted_message = binary_message + [0] * 8

    # Diviser par le polynôme générateur pour calculer le reste
    remainder = shifted_message[:]
    for i in range(len(binary_message)):
        if remainder[i] == 1:
            for j in range(len(generator)):
                remainder[i + j] ^= generator[j]

    # Ajouter le reste aux bits d'information
    encoded_message = binary_message + remainder[len(binary_message):]

    return encoded_message

# Fonction pour décoder BCH(15,7) t=2
def bch_decode_15_7(encoded_message):
    generator = [1, 1, 1, 0, 1, 0, 0, 0, 1]  # g(x) pour BCH(15,7)

    # Calculer le syndrome
    syndrome = encoded_message[len(encoded_message) - len(generator):]
    
    # Si le syndrome est nul, pas d'erreur
    if sum(syndrome) == 0:
        return encoded_message[:7], "No errors", []

    # Tentative de correction des erreurs pour t=2
    corrected_message = encoded_message[:]
    error_positions = []
    for i in range(len(encoded_message)):
        corrected_message[i] ^= 1  # Inverser le bit
        test_syndrome = corrected_message[len(corrected_message) - len(generator):]

        # Recalculer le syndrome
        if sum(test_syndrome) == 0:
            error_positions.append(i)
            return corrected_message[:7], "Errors corrected", error_positions
        corrected_message[i] ^= 1  # Restaurer si la correction échoue

    return encoded_message[:7], "Errors detected but not corrected", []

# Fonction pour introduire des erreurs

def introduce_errors(encoded_message, num_errors):
    positions = []
    for _ in range(num_errors):
        pos = int(input(f"Entrez la position de l'erreur (0-{len(encoded_message)-1}) : "))
        if 0 <= pos < len(encoded_message):
            positions.append(pos)
            encoded_message[pos] ^= 1
        else:
            print("Position invalide.")
    print(f"Erreurs introduites aux positions : {positions}")
    return encoded_message

# Fonction pour lire un message depuis la liaison série
def read_serial(port="COM3", baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate)
        print("En attente de données...")
        data = ser.read(2)  # Lecture de 2 octets (16 bits)
        encoded_message = []
        for byte in data:
            for i in range(8):
                encoded_message.append((byte >> (7 - i)) & 1)
        ser.close()
        encoded_message = encoded_message[:15] # Retirer le bit de remplissage 
        print("Message reçu via la liaison série :", encoded_message)
        return encoded_message
    except serial.SerialException as e:
        print("Erreur lors de la lecture de la liaison série :", e)
        return None
# Fonction pour vérifier et corriger les erreurs dans un message BCH(15,7)
def verify_and_correct_bch15_7(encoded_message):
    generator = [1, 1, 1, 0, 1, 0, 0, 0, 1]  # g(x) pour BCH(15,7)
    # Calculer le syndrome en effectuant une division polynomiale
    syndrome = encoded_message[:]
    for i in range(len(encoded_message) - len(generator) + 1):
        if syndrome[i] == 1:
            for j in range(len(generator)):
                syndrome[i + j] ^= generator[j]

    syndrome = syndrome[len(encoded_message) - len(generator):]

    # Vérification explicite du syndrome
    print(f"Syndrome calculé : {syndrome}")

    # Si le syndrome est nul, le message n'est pas corrompu
    if sum(syndrome) == 0:
        print("Aucune erreur détectée dans le message.")
        return encoded_message[:7], "No errors", []

    # Essayer de corriger une erreur (max t=1)
    corrected_message = encoded_message[:]
    error_positions = []

    for i in range(len(encoded_message)):
        corrected_message[i] ^= 1  # Inverser le bit

        # Recalculer le syndrome après inversion
        test_syndrome = corrected_message[:]
        for k in range(len(test_syndrome) - len(generator) + 1):
            if test_syndrome[k] == 1:
                for j in range(len(generator)):
                    test_syndrome[k + j] ^= generator[j]

        test_syndrome = test_syndrome[len(test_syndrome) - len(generator):]

        if sum(test_syndrome) == 0:
            error_positions.append(i)
            print(f"Correction appliquée à la position {i}")
            return corrected_message[:7], "Errors corrected", error_positions

        corrected_message[i] ^= 1  # Restaurer si correction échoue

    # Essayer de corriger deux erreurs (max t=2)
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

            if sum(test_syndrome) == 0:
                error_positions.extend([i, j])
                print(f"Corrections appliquées aux positions {i} et {j}")
                return corrected_message[:7], "Errors corrected", error_positions

            corrected_message[i] ^= 1
            corrected_message[j] ^= 1  # Restaurer si correction échoue

    # Si aucune correction n'a pu être faite
    print("Erreur non corrigée avec le syndrome :", syndrome)
    return encoded_message[:7], "Errors detected but not corrected", []

# Programme principal
def main():
    while True:
        # Lire depuis la liaison série
        encoded_message = read_serial()
        if encoded_message is None:
            continue

        # Afficher le message reçu
        print("Message reçu (BCH encodé) :", encoded_message)

        # Proposer d'introduire des erreurs
        user_choice = input("Voulez-vous introduire des erreurs dans le message ? (oui/non) : ").strip().lower()
        if user_choice == "oui":
            try:
                num_errors = int(input("Combien d'erreurs voulez-vous introduire (1 ou 2) ? : "))
                if num_errors not in [1, 2]:
                    print("Nombre d'erreurs non valide.")
                else:
                    encoded_message = introduce_errors(encoded_message, num_errors)
                    print("Message avec erreurs :", encoded_message)
            except ValueError:
                print("Entrée non valide.")

        # Décodage BCH
        print("--- Décodage BCH ---")
        decoded_message, status, error_positions = verify_and_correct_bch15_7(encoded_message)
        print("Message décodé :", decoded_message)
        print("Statut :", status)
        if error_positions:
            print("Positions des erreurs corrigées :", error_positions)

if __name__ == "__main__":
    main()
