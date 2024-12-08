import tkinter as tk
from tkinter import scrolledtext, messagebox

# Fonction pour envoyer les données
def send_data():
    data = input_text.get("1.0", tk.END).strip()
    if not data:
        messagebox.showerror("Erreur", "Veuillez entrer des données.")
        return
    encoded_data = f"Encoded: {data}"  # Simulation d'encodage
    output_text.insert(tk.END, f"Trame envoyée : {encoded_data}\n")
    # Simuler une transmission avec une erreur
    if simulate_error.get():
        corrupted_data = f"Corrupted: {data[:-1]}X"
        output_text.insert(tk.END, f"Trame reçue (avec erreur) : {corrupted_data}\n")
        corrected_data = f"Corrected: {data}"
        output_text.insert(tk.END, f"Trame corrigée : {corrected_data}\n")
    else:
        output_text.insert(tk.END, f"Trame reçue : {encoded_data}\n")

# Fonction pour réinitialiser l'interface
def reset_interface():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    simulate_error.set(False)

# Fenêtre principale
window = tk.Tk()
window.title("Transmission Fiabilisée de Données")

# Section d'entrée des données
tk.Label(window, text="Entrée des données :").grid(row=0, column=0, sticky="w", padx=10, pady=5)
input_text = scrolledtext.ScrolledText(window, width=50, height=5)
input_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Boutons d'action
simulate_error = tk.BooleanVar()
tk.Checkbutton(window, text="Simuler une erreur", variable=simulate_error).grid(row=2, column=0, sticky="w", padx=10)
tk.Button(window, text="Envoyer", command=send_data).grid(row=2, column=1, sticky="e", padx=10)

# Section d'affichage des résultats
tk.Label(window, text="Résultats :").grid(row=3, column=0, sticky="w", padx=10, pady=5)
output_text = scrolledtext.ScrolledText(window, width=50, height=10)
output_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

# Bouton de réinitialisation
tk.Button(window, text="Réinitialiser", command=reset_interface).grid(row=5, column=0, columnspan=2, pady=10)

# Démarrer l'interface
window.mainloop()
