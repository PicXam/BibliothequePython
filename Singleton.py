import uuid
import pickle
import os

class BibliothequeDB:
    _instance = None
    _fichier_sauvegarde = "bibliotheque.pkl"

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(BibliothequeDB, cls).__new__(cls)
            cls._instance.livres = {}
            cls._instance.utilisateurs = {}
            cls._instance.livres_empruntes = {}
            cls._instance.charger_donnees()
        return cls._instance

    def ajouter_livre(self, livre):
        self.livres[livre.id] = livre
        print(f"Le livre '{livre.titre}' a été ajouté à la base de données.")

    def ajouter_utilisateur(self, nom_utilisateur):
        user_id = str(uuid.uuid4())
        self.utilisateurs[user_id] = {'nom': nom_utilisateur}
        print(f"Utilisateur '{nom_utilisateur}' ajouté.")
        return user_id

    def emprunter_livre(self, livre_id, user_id):
        livre = self.livres.get(livre_id)
        if livre and not livre.est_emprunte:
            livre.est_emprunte = True
            self.livres_empruntes[livre_id] = user_id
            return True
        return False

    def rendre_livre(self, livre_id):
        if livre_id in self.livres_empruntes:
            livre = self.livres.get(livre_id)
            if livre:
                livre.est_emprunte = False
                del self.livres_empruntes[livre_id]
                return True
        return False

    def get_emprunteur(self, livre_id):
        user_id = self.livres_empruntes.get(livre_id)
        if user_id:
            return self.utilisateurs.get(user_id, {}).get('nom')
        return None

    def sauvegarder_donnees(self):
        donnees_a_sauvegarder = {
            'livres': self.livres,
            'utilisateurs': self.utilisateurs,
            'livres_empruntes': self.livres_empruntes
        }
        with open(self._fichier_sauvegarde, 'wb') as f:
            pickle.dump(donnees_a_sauvegarder, f)
        print("Données de la bibliothèque sauvegardées avec pickle.")

    def charger_donnees(self):
        if os.path.exists(self._fichier_sauvegarde):
            try:
                with open(self._fichier_sauvegarde, 'rb') as f:
                    donnees_chargees = pickle.load(f)
                    self.livres = donnees_chargees.get('livres', {})
                    self.utilisateurs = donnees_chargees.get('utilisateurs', {})
                    self.livres_empruntes = donnees_chargees.get('livres_empruntes', {})
                print("Données de la bibliothèque chargées avec pickle.")
            except (pickle.UnpicklingError, EOFError) as e:
                print(f"Erreur lors du chargement des données (pickle): {e}. Création d'une nouvelle base de données.")
                self.livres = {}
                self.utilisateurs = {}
                self.livres_empruntes = {}
        else:
            print("Aucun fichier de sauvegarde trouvé, création d'une nouvelle base de données.")