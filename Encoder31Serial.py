import serial

# Fonction pour encoder BCH(31,8) t=2
def bch_encode_31_8(binary_message):
    generator = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1]  # g(x) pour BCH(31,8)
    
    # Convertir le message binaire en liste d'entiers
    binary_message = [int(bit) for bit in binary_message]

    # Ajouter les bits redondants (x^23)
    shifted_message = binary_message + [0] * 23

    # Diviser par le polynôme générateur pour calculer le reste
    remainder = shifted_message[:]
    for i in range(len(binary_message)):
        if remainder[i] == 1:
            for j in range(len(generator)):
                remainder[i + j] ^= generator[j]

    # Ajouter le reste aux bits d'information
    encoded_message = binary_message + remainder[len(binary_message):]

    return encoded_message

# Fonction pour convertir un caractère ASCII en binaire (8 bits)
def ascii_to_binary(char):
    return f"{ord(char):08b}"

# Fonction pour envoyer un message encodé via liaison série
def send_serial(encoded_message, port="COM3", baudrate=9600):
    try:
        # Initialiser la liaison série
        ser = serial.Serial(port, baudrate)

        # Convertir le message en bytearray
        byte_array = bytearray()
        for i in range(0, len(encoded_message), 8):
            byte = 0
            for j in range(8):
                if i + j < len(encoded_message):
                    byte |= (encoded_message[i + j] << (7 - j))
            byte_array.append(byte)

        # Envoyer les données
        ser.write(byte_array)
        print("Message envoyé sur la liaison série.")

        # Fermer la liaison série
        ser.close()
    except serial.SerialException as e:
        print("Erreur lors de l'envoi sur la liaison série :", e)

# Programme principal
def main():
    # Demander à l'utilisateur de saisir un message ASCII
    ascii_message = input("Saisissez un message ASCII : ").strip()

    # Convertir chaque caractère en binaire et encoder en BCH(31,8)
    full_encoded_message = []
    for char in ascii_message:
        binary_message = ascii_to_binary(char)
        print(f"Caractère '{char}' en binaire : {binary_message}")
        encoded_message = bch_encode_31_8(binary_message)
        print(f"Caractère '{char}' encodé (BCH 31,8) : {encoded_message}")
        full_encoded_message.extend(encoded_message)

    # Supprimer les doublons en s'assurant que chaque caractère est encodé une seule fois
    unique_encoded_message = full_encoded_message

    # Envoi via la liaison série
    send_serial(unique_encoded_message)

if __name__ == "__main__":
    main()
