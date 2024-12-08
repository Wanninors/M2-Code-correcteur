import reedsolo

# Initialisation de l'encodeur RS
rs = reedsolo.RSCodec(4)  # 4 symboles de redondance (corrige jusqu'à 2 erreurs)

# Message à transmettre
data = b"hello"

# Encodage des données
encoded = rs.encode(data)
print("Données encodées :", encoded)

# Simuler une erreur
corrupted = bytearray(encoded)
corrupted[2] = 0x00  # Modifier un octet pour simuler une erreur
corrupted[5] = 0xFF  # Ajouter une deuxième erreur
print("Données corrompues :", corrupted)

# Décodage et correction
try:
    decoded = rs.decode(corrupted)
    print("Données corrigées :", decoded)
except reedsolo.ReedSolomonError as e:
    print("Erreur non corrigible :", e)
