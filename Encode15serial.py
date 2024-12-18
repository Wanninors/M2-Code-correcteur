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
    # Demander à l'utilisateur de saisir un message de 7 bits
    while True:
        binary_message = input("Saisissez un message binaire de 7 bits : ").strip()
        if len(binary_message) == 7 and all(bit in '01' for bit in binary_message):
            break
        else:
            print("Erreur : Veuillez saisir exactement 7 bits (0 ou 1).")

    print("Message binaire saisi :", binary_message)

    # Encodage BCH
    encoded_message = bch_encode_15_7(binary_message)
    print("Message encodé (BCH 15,7) :", encoded_message)

    # Envoi via la liaison série
    send_serial(encoded_message)

if __name__ == "__main__":
    main()