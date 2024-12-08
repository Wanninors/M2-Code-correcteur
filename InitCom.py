import serial
import time

# Configuration du port COM
ser = serial.Serial(
    port='COM3',        # Remplacez par le nom de votre port
    baudrate=9600,      # Vitesse de transmission
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1           # Timeout pour la lecture/écriture
)

# Vérification si le port est ouvert
if ser.is_open:
    print("Port série ouvert : ", ser.name)

# Envoi d'un message
message = "HELLO, COM PORT!\r\n"
ser.write(message.encode('utf-8'))  # Encodage en bytes
print("Message envoyé : ", message)

# Attente avant la fermeture
time.sleep(2)

# Fermeture du port série
ser.close()
print("Port série fermé.")
