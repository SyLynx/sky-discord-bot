# ============================================
# 💾 GESTIONNAIRE DE BASE DE DONNÉES JSON
# ============================================
# Ce fichier gère toutes les sauvegardes et lectures
# de données dans des fichiers JSON.
# 
# JSON = format de fichier simple pour stocker des données
# C'est comme un dictionnaire Python sauvegardé sur le disque.
# ============================================

import json
import os
from typing import Any
import time


# Chemin du dossier où sont stockées les données
DOSSIER_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def assurer_dossier_existe():
    """
    Crée le dossier 'data' s'il n'existe pas.
    C'est appelé automatiquement quand on sauvegarde quelque chose.
    """
    if not os.path.exists(DOSSIER_DATA):
        os.makedirs(DOSSIER_DATA)


def charger_json(nom_fichier: str, defaut: Any = None) -> Any:
    """
    Charge un fichier JSON et retourne son contenu.
    
    Arguments:
        nom_fichier: Le nom du fichier (ex: "economy.json")
        defaut: La valeur à retourner si le fichier n'existe pas
    
    Retourne:
        Le contenu du fichier, ou la valeur par défaut
    
    Exemple:
        soldes = charger_json("economy.json", {})
        print(soldes)  # {"123456789": 500, "987654321": 1500}
    """
    assurer_dossier_existe()
    chemin = os.path.join(DOSSIER_DATA, nom_fichier)
    
    # Si le fichier n'existe pas, retourne la valeur par défaut
    if not os.path.exists(chemin):
        return defaut if defaut is not None else {}
    
    # Lit et retourne le contenu du fichier
    try:
        with open(chemin, "r", encoding="utf-8") as fichier:
            return json.load(fichier)
    except json.JSONDecodeError:
        # Si le fichier est corrompu, retourne la valeur par défaut
        print(f"⚠️ Fichier {nom_fichier} corrompu, utilisation des valeurs par défaut")
        return defaut if defaut is not None else {}


def sauvegarder_json(nom_fichier: str, donnees: Any):
    """
    Sauvegarde des données dans un fichier JSON.
    
    Arguments:
        nom_fichier: Le nom du fichier (ex: "economy.json")
        donnees: Les données à sauvegarder (dict, list, etc.)
    
    Exemple:
        soldes = {"123456789": 500}
        sauvegarder_json("economy.json", soldes)
    """
    assurer_dossier_existe()
    chemin = os.path.join(DOSSIER_DATA, nom_fichier)
    
    # Sauvegarde avec une jolie indentation (indent=4)
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, indent=4, ensure_ascii=False)


# ============================================
# 💰 FONCTIONS ÉCONOMIE
# ============================================

def obtenir_solde(user_id: int) -> int:
    """
    Récupère le solde d'un utilisateur.
    
    Arguments:
        user_id: L'ID Discord de l'utilisateur
    
    Retourne:
        Le solde en Skycoins (0 si l'utilisateur n'a pas de compte)
    """
    economie = charger_json("economy.json", {})
    return economie.get(str(user_id), 0)


def modifier_solde(user_id: int, montant: int) -> int:
    """
    Ajoute ou retire des Skycoins au solde d'un utilisateur.
    
    Arguments:
        user_id: L'ID Discord de l'utilisateur
        montant: Le montant à ajouter (positif) ou retirer (négatif)
    
    Retourne:
        Le nouveau solde
    
    Exemple:
        modifier_solde(123456789, 500)   # Ajoute 500
        modifier_solde(123456789, -200)  # Retire 200
    """
    economie = charger_json("economy.json", {})
    
    # Récupère le solde actuel ou 0
    solde_actuel = economie.get(str(user_id), 0)
    
    # Calcule le nouveau solde (minimum 0, on ne peut pas être négatif)
    nouveau_solde = max(0, solde_actuel + montant)
    
    # Sauvegarde
    economie[str(user_id)] = nouveau_solde
    sauvegarder_json("economy.json", economie)
    
    return nouveau_solde


def definir_solde(user_id: int, montant: int) -> int:
    """
    Définit le solde exact d'un utilisateur.
    
    Arguments:
        user_id: L'ID Discord de l'utilisateur
        montant: Le nouveau solde
    
    Retourne:
        Le nouveau solde
    """
    economie = charger_json("economy.json", {})
    economie[str(user_id)] = max(0, montant)
    sauvegarder_json("economy.json", economie)
    return economie[str(user_id)]


def obtenir_classement(limite: int = 10) -> list:
    """
    Récupère le classement des utilisateurs les plus riches.
    
    Arguments:
        limite: Nombre maximum d'utilisateurs à retourner
    
    Retourne:
        Liste de tuples (user_id, solde) triée par solde décroissant
    """
    economie = charger_json("economy.json", {})
    
    # Trie par solde décroissant
    classement = sorted(economie.items(), key=lambda x: x[1], reverse=True)
    
    return classement[:limite]


# ============================================
# ⏱️ FONCTIONS COOLDOWNS
# ============================================

def verifier_cooldown(user_id: int, type_cooldown: str, duree_secondes: int) -> tuple[bool, int]:
    """
    Vérifie si un utilisateur peut utiliser une commande (cooldown terminé).
    
    Arguments:
        user_id: L'ID Discord de l'utilisateur
        type_cooldown: Le type de cooldown ("day", "week", "month")
        duree_secondes: La durée du cooldown en secondes
    
    Retourne:
        (peut_utiliser, temps_restant)
        - peut_utiliser: True si le cooldown est terminé
        - temps_restant: Secondes restantes avant de pouvoir réutiliser
    
    Exemple:
        peut_utiliser, temps_restant = verifier_cooldown(123, "day", 86400)
        if not peut_utiliser:
            print(f"Attends encore {temps_restant} secondes !")
    """
    cooldowns = charger_json("cooldowns.json", {})
    
    cle = f"{user_id}_{type_cooldown}"
    maintenant = time.time()
    
    # Récupère le timestamp de la dernière utilisation
    derniere_utilisation = cooldowns.get(cle, 0)
    
    # Calcule le temps écoulé
    temps_ecoule = maintenant - derniere_utilisation
    
    if temps_ecoule >= duree_secondes:
        return True, 0
    else:
        temps_restant = int(duree_secondes - temps_ecoule)
        return False, temps_restant


def enregistrer_cooldown(user_id: int, type_cooldown: str):
    """
    Enregistre qu'un utilisateur vient d'utiliser une commande.
    
    Arguments:
        user_id: L'ID Discord de l'utilisateur
        type_cooldown: Le type de cooldown ("day", "week", "month")
    """
    cooldowns = charger_json("cooldowns.json", {})
    
    cle = f"{user_id}_{type_cooldown}"
    cooldowns[cle] = time.time()
    
    sauvegarder_json("cooldowns.json", cooldowns)


# ============================================
# 🎭 FONCTIONS RÔLES PERSONNALISÉS
# ============================================

def obtenir_roles_perso() -> dict:
    """
    Récupère tous les rôles personnalisés.
    
    Retourne:
        Dictionnaire {user_id: {role_id, nom, couleur, membres, derniere_facture}}
    """
    return charger_json("custom_roles.json", {})


def sauvegarder_role_perso(user_id: int, role_id: int, nom: str, couleur: int):
    """
    Sauvegarde un nouveau rôle personnalisé.
    
    Arguments:
        user_id: L'ID du propriétaire du rôle
        role_id: L'ID du rôle Discord créé
        nom: Le nom du rôle
        couleur: La couleur du rôle (en entier)
    """
    roles = obtenir_roles_perso()
    
    roles[str(user_id)] = {
        "role_id": role_id,
        "nom": nom,
        "couleur": couleur,
        "membres": [user_id],  # Liste des membres qui ont le rôle
        "derniere_facture": time.time(),
        "date_creation": time.time()
    }
    
    sauvegarder_json("custom_roles.json", roles)


def ajouter_membre_role_perso(proprietaire_id: int, membre_id: int) -> bool:
    """
    Ajoute un membre à un rôle personnalisé.
    
    Arguments:
        proprietaire_id: L'ID du propriétaire du rôle
        membre_id: L'ID du membre à ajouter
    
    Retourne:
        True si ajouté, False si le rôle n'existe pas
    """
    roles = obtenir_roles_perso()
    
    if str(proprietaire_id) not in roles:
        return False
    
    if membre_id not in roles[str(proprietaire_id)]["membres"]:
        roles[str(proprietaire_id)]["membres"].append(membre_id)
        sauvegarder_json("custom_roles.json", roles)
    
    return True


def supprimer_role_perso(user_id: int) -> int | None:
    """
    Supprime un rôle personnalisé des données.
    
    Arguments:
        user_id: L'ID du propriétaire du rôle
    
    Retourne:
        L'ID du rôle Discord à supprimer, ou None si pas trouvé
    """
    roles = obtenir_roles_perso()
    
    if str(user_id) in roles:
        role_id = roles[str(user_id)]["role_id"]
        del roles[str(user_id)]
        sauvegarder_json("custom_roles.json", roles)
        return role_id
    
    return None


# ============================================
# 👑 FONCTIONS RÔLES VIP
# ============================================

def obtenir_vip() -> dict:
    """
    Récupère tous les utilisateurs VIP.
    
    Retourne:
        Dictionnaire {user_id: timestamp_expiration}
    """
    return charger_json("vip_roles.json", {})


def ajouter_vip(user_id: int, duree_jours: int = 30):
    """
    Ajoute un utilisateur comme VIP.
    
    Arguments:
        user_id: L'ID de l'utilisateur
        duree_jours: Durée du VIP en jours (défaut: 30)
    """
    vip = obtenir_vip()
    
    # Calcule la date d'expiration
    expiration = time.time() + (duree_jours * 86400)
    
    vip[str(user_id)] = expiration
    sauvegarder_json("vip_roles.json", vip)


def verifier_vip_expire(user_id: int) -> bool:
    """
    Vérifie si le VIP d'un utilisateur a expiré.
    
    Arguments:
        user_id: L'ID de l'utilisateur
    
    Retourne:
        True si expiré ou pas VIP, False sinon
    """
    vip = obtenir_vip()
    
    if str(user_id) not in vip:
        return True
    
    return time.time() > vip[str(user_id)]


def supprimer_vip(user_id: int):
    """
    Retire le statut VIP d'un utilisateur.
    """
    vip = obtenir_vip()
    
    if str(user_id) in vip:
        del vip[str(user_id)]
        sauvegarder_json("vip_roles.json", vip)


def obtenir_vip_expires() -> list:
    """
    Récupère la liste des VIP qui ont expiré.
    
    Retourne:
        Liste des user_id dont le VIP a expiré
    """
    vip = obtenir_vip()
    maintenant = time.time()
    
    expires = []
    for user_id, expiration in vip.items():
        if maintenant > expiration:
            expires.append(int(user_id))
    
    return expires


# ============================================
# 📝 FONCTIONS LIENS DE RECRUTEMENT
# ============================================

def obtenir_liens_recrutement() -> dict:
    """
    Récupère les liens de recrutement sauvegardés.
    
    Retourne:
        Dictionnaire {"moderation": "lien", "animation": "lien"}
    """
    return charger_json("recrutement.json", {})


def sauvegarder_lien_recrutement(type_poste: str, lien: str):
    """
    Sauvegarde un lien de recrutement.
    
    Arguments:
        type_poste: "moderation" ou "animation"
        lien: Le lien du formulaire Google Forms
    """
    liens = obtenir_liens_recrutement()
    liens[type_poste] = lien
    sauvegarder_json("recrutement.json", liens)


# ============================================
# 🎉 FONCTIONS GIVEAWAYS
# ============================================

def obtenir_giveaways() -> dict:
    """
    Récupère tous les giveaways (actifs et terminés).
    
    Retourne:
        Dictionnaire {message_id: {prix, fin, nb_gagnants, participants, ...}}
    """
    return charger_json("giveaways.json", {})


def sauvegarder_giveaways(giveaways: dict):
    """
    Sauvegarde tous les giveaways.
    """
    sauvegarder_json("giveaways.json", giveaways)

