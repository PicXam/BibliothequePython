from Factory import Livre

class Utilisateur:
    def __init__(self, nom, callback_mise_a_jour=None):
        self.nom = nom
        self.callback_mise_a_jour = callback_mise_a_jour

    def mettre_a_jour(self, livre_titre, statut):
        message = f"Notification pour {self.nom} : Le livre '{livre_titre}' est maintenant {statut}."
        if self.callback_mise_a_jour:
            self.callback_mise_a_jour(message)
        else:
            print(message)

class LivreObservable(Livre):
    def __init__(self, titre, auteur):
        super().__init__(titre, auteur)
        self._observateurs = []

    def ajouter_observateur(self, observateur):
        if observateur not in self._observateurs:
            self._observateurs.append(observateur)

    def retirer_observateur(self, observateur):
        if observateur in self._observateurs:
            self._observateurs.remove(observateur)

    def notifier_observateurs(self, statut):
        for observateur in self._observateurs:
            observateur.mettre_a_jour(self.titre, statut)

    def emprunter(self):
        # L'observable ne notifie que si l'emprunt est un succès
        if not self.est_emprunte:
            self.est_emprunte = True
            self.notifier_observateurs("emprunté")
            return True
        return False

    def rendre(self):
        # L'observable ne notifie que si le rendu est un succès
        if self.est_emprunte:
            self.est_emprunte = False
            self.notifier_observateurs("rendu")
            return True
        return False