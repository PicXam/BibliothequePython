import uuid

class Livre:
    def __init__(self, titre, auteur):
        self.id = str(uuid.uuid4())
        self.titre = titre
        self.auteur = auteur
        self.est_emprunte = False
        # Ajout du genre pour être cohérent avec les classes enfants
        self.genre = "Livre"

class Roman(Livre):
    def __init__(self, titre, auteur):
        super().__init__(titre, auteur)
        self.genre = "Roman"

class ManuelScolaire(Livre):
    def __init__(self, titre, auteur):
        super().__init__(titre, auteur)
        self.genre = "Manuel Scolaire"

class LivreFactory:
    @staticmethod
    def creer_livre(type_livre, titre, auteur):
        if type_livre == "roman":
            return Roman(titre, auteur)
        elif type_livre == "manuel":
            return ManuelScolaire(titre, auteur)
        else:
            raise ValueError("Type de livre non supporté")