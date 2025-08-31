import tkinter as tk
from tkinter import ttk
from Singleton import BibliothequeDB
from Factory import LivreFactory
from Observer import LivreObservable, Utilisateur


class BibliothequeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Bibliothèque")

        self.db = BibliothequeDB()
        self.utilisateurs_observateurs = {}
        self.livres_observables = {}
        self.notifications = []

        self.creer_widgets()
        self.rafraichir_liste_livres()
        self.rafraichir_liste_utilisateurs()
        self.rafraichir_notifications()

    def creer_widgets(self):
        # Cadre de saisie pour les livres
        frame_saisie = tk.LabelFrame(self.root, text="Ajouter un Livre")
        frame_saisie.pack(padx=10, pady=10)

        tk.Label(frame_saisie, text="Titre:").pack()
        self.titre_entry = tk.Entry(frame_saisie)
        self.titre_entry.pack()

        tk.Label(frame_saisie, text="Auteur:").pack()
        self.auteur_entry = tk.Entry(frame_saisie)
        self.auteur_entry.pack()

        tk.Label(frame_saisie, text="Type:").pack()
        self.type_var = tk.StringVar(value="roman")
        tk.Radiobutton(frame_saisie, text="Roman", variable=self.type_var, value="roman").pack(anchor=tk.W)
        tk.Radiobutton(frame_saisie, text="Manuel Scolaire", variable=self.type_var, value="manuel").pack(anchor=tk.W)

        tk.Button(frame_saisie, text="Ajouter Livre", command=self.ajouter_livre).pack(pady=5)

        # Cadre pour la gestion des utilisateurs
        frame_utilisateurs = tk.LabelFrame(self.root, text="Gérer les Utilisateurs")
        frame_utilisateurs.pack(padx=10, pady=10)

        tk.Label(frame_utilisateurs, text="Nom d'utilisateur:").pack()
        self.utilisateur_entry = tk.Entry(frame_utilisateurs)
        self.utilisateur_entry.pack()

        tk.Button(frame_utilisateurs, text="Ajouter Utilisateur", command=self.ajouter_utilisateur).pack(pady=5)

        # Cadre d'affichage
        frame_affichage = tk.LabelFrame(self.root, text="Bibliothèque et Utilisateurs")
        frame_affichage.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Listes
        listes_frame = tk.Frame(frame_affichage)
        listes_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Liste des livres
        frame_livres = tk.LabelFrame(listes_frame, text="Livres Disponibles")
        frame_livres.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.livres_listbox = tk.Listbox(frame_livres, height=10)
        self.livres_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.livres_ids_list = []
        self.livres_scrollbar = tk.Scrollbar(frame_livres)
        self.livres_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.livres_listbox.config(yscrollcommand=self.livres_scrollbar.set)
        self.livres_scrollbar.config(command=self.livres_listbox.yview)

        # Remplacement de la liste des utilisateurs par un Combobox
        frame_utilisateurs_combo = tk.LabelFrame(listes_frame, text="Sélectionner un Utilisateur")
        frame_utilisateurs_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Label(frame_utilisateurs_combo, text="Utilisateur:").pack(pady=5)
        self.utilisateur_combobox = ttk.Combobox(frame_utilisateurs_combo, state="readonly")
        self.utilisateur_combobox.pack(fill=tk.X, padx=5, pady=5)
        self.utilisateurs_ids_list = []

        # Cadre pour les boutons d'action
        frame_actions = tk.LabelFrame(self.root, text="Actions")
        frame_actions.pack(padx=10, pady=10)
        tk.Button(frame_actions, text="Emprunter Livre", command=self.emprunter_livre).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_actions, text="Rendre Livre", command=self.rendre_livre).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_actions, text="Sauvegarder et Quitter", command=self.sauvegarder_et_quitter).pack(side=tk.LEFT,
                                                                                                          padx=5)

        # Cadre pour les notifications
        frame_notifications = tk.LabelFrame(self.root, text="Notifications")
        frame_notifications.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.notifications_text = tk.Text(frame_notifications, height=5, state=tk.DISABLED)
        self.notifications_text.pack(fill=tk.BOTH, expand=True)

    def rafraichir_liste_livres(self):
        self.livres_listbox.delete(0, tk.END)
        self.livres_ids_list = []
        for livre_id, livre in self.db.livres.items():
            statut = " (Emprunté)" if livre.est_emprunte else " (Disponible)"
            self.livres_listbox.insert(tk.END, f"{livre.titre} par {livre.auteur} - {livre.genre}{statut}")
            self.livres_ids_list.append(livre_id)
            if livre_id not in self.livres_observables:
                self.livres_observables[livre_id] = LivreObservable(livre.titre, livre.auteur)

    def rafraichir_liste_utilisateurs(self):
        self.utilisateurs_ids_list = []
        noms_utilisateurs = []
        for user_id, user_data in self.db.utilisateurs.items():
            self.utilisateurs_ids_list.append(user_id)
            noms_utilisateurs.append(user_data['nom'])
            if user_id not in self.utilisateurs_observateurs:
                self.utilisateurs_observateurs[user_id] = Utilisateur(user_data['nom'], self.afficher_notification)

        self.utilisateur_combobox['values'] = noms_utilisateurs
        if noms_utilisateurs:
            self.utilisateur_combobox.current(0)

    def rafraichir_notifications(self):
        self.notifications_text.config(state=tk.NORMAL)
        self.notifications_text.delete('1.0', tk.END)
        for notif in self.notifications:
            self.notifications_text.insert(tk.END, notif + "\n")
        self.notifications_text.config(state=tk.DISABLED)

    def ajouter_livre(self):
        titre = self.titre_entry.get()
        auteur = self.auteur_entry.get()
        type_livre = self.type_var.get()
        if titre and auteur:
            try:
                livre = LivreFactory.creer_livre(type_livre, titre, auteur)
                self.db.ajouter_livre(livre)
                self.rafraichir_liste_livres()
                self.afficher_notification(f"Livre '{titre}' ajouté avec succès.")
                self.titre_entry.delete(0, tk.END)
                self.auteur_entry.delete(0, tk.END)
            except ValueError as e:
                self.afficher_notification(f"Erreur: {e}")

    def ajouter_utilisateur(self):
        nom_utilisateur = self.utilisateur_entry.get()
        if nom_utilisateur:
            user_id = self.db.ajouter_utilisateur(nom_utilisateur)
            self.rafraichir_liste_utilisateurs()
            # Ajout du nouvel utilisateur à la liste des observateurs
            self.utilisateurs_observateurs[user_id] = Utilisateur(nom_utilisateur, self.afficher_notification)
            self.afficher_notification(f"Utilisateur '{nom_utilisateur}' ajouté.")
            self.utilisateur_entry.delete(0, tk.END)

    def emprunter_livre(self):
        livre_selection = self.livres_listbox.curselection()
        utilisateur_selection = self.utilisateur_combobox.get()

        if livre_selection and utilisateur_selection:
            livre_index = livre_selection[0]
            livre_id = self.livres_ids_list[livre_index]

            user_id = None
            for u_id, u_data in self.db.utilisateurs.items():
                if u_data['nom'] == utilisateur_selection:
                    user_id = u_id
                    break

            if user_id is None:
                self.afficher_notification("Erreur: Utilisateur sélectionné introuvable.")
                return

            livre_observable = self.livres_observables.get(livre_id)
            observateur = self.utilisateurs_observateurs.get(user_id)

            if observateur and livre_observable:
                livre_observable.ajouter_observateur(observateur)

            if self.db.emprunter_livre(livre_id, user_id):
                if livre_observable:
                    livre_observable.emprunter()
                self.afficher_notification(
                    f"Le livre '{self.db.livres[livre_id].titre}' a été emprunté par '{self.db.utilisateurs[user_id]['nom']}'.")
            else:
                self.afficher_notification("Erreur: Le livre est déjà emprunté.")

            self.rafraichir_liste_livres()
        else:
            self.afficher_notification("Veuillez sélectionner un livre ET un utilisateur.")

    def rendre_livre(self):
        selection = self.livres_listbox.curselection()

        if selection:
            index = selection[0]
            livre_id = self.livres_ids_list[index]

            emprunteur_id = self.db.livres_empruntes.get(livre_id)
            if emprunteur_id:
                livre_observable = self.livres_observables.get(livre_id)
                observateur = self.utilisateurs_observateurs.get(emprunteur_id)

                if observateur and livre_observable:
                    livre_observable.retirer_observateur(observateur)

            if self.db.rendre_livre(livre_id):
                if livre_observable:
                    livre_observable.rendre()
                self.afficher_notification(f"Le livre '{self.db.livres[livre_id].titre}' a été rendu.")
            else:
                self.afficher_notification("Erreur: Le livre n'est pas emprunté ou introuvable.")

            self.rafraichir_liste_livres()

    def afficher_notification(self, message):
        self.notifications.append(message)
        self.rafraichir_notifications()
        self.db.sauvegarder_donnees()

    def sauvegarder_et_quitter(self):
        self.db.sauvegarder_donnees()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BibliothequeApp(root)
    root.mainloop()