# ============================================
# ⚙️ CONFIGURATION CENTRALISÉE DU BOT
# ============================================
# Toutes les valeurs importantes sont ici !
# Modifie ce fichier pour personnaliser le bot.
# ============================================

import os
from dotenv import load_dotenv

# Charge les variables du fichier .env (override=True pour forcer le rechargement)
load_dotenv(override=True)

# ============================================
# 🔐 IDENTIFIANTS (depuis .env)
# ============================================

# Token du bot Discord
TOKEN = os.getenv("DISCORD_TOKEN")

# ID du serveur Discord
GUILD_ID = int(os.getenv("GUILD_ID", "0"))


# ============================================
# 🎭 RÔLES
# ============================================

# Rôle attribué quand quelqu'un accepte le règlement
ROLE_REGLEMENT_ID = (A REMPLIR)

# Rôle VIP achetable dans la boutique
ROLE_VIP_ID = (A REMPLIR)


# ============================================
# 💰 ÉCONOMIE - RÉCOMPENSES
# ============================================

# Récompenses des commandes quotidiennes/hebdo/mensuelles
RECOMPENSE_JOUR = 500       # /day
RECOMPENSE_SEMAINE = 1000   # /week  
RECOMPENSE_MOIS = 2000      # /month

# Cooldowns en secondes
COOLDOWN_JOUR = 86400       # 24 heures
COOLDOWN_SEMAINE = 604800   # 7 jours
COOLDOWN_MOIS = 2592000     # 30 jours


# ============================================
# 🛒 BOUTIQUE - PRIX
# ============================================

# Prix du rôle VIP (durée : 1 mois)
PRIX_VIP = 5000

# Prix du rôle personnalisé
PRIX_ROLE_PERSO = 20000

# Prix pour partager son rôle perso avec quelqu'un
PRIX_PARTAGE_ROLE = 50

# Facture mensuelle pour garder son rôle perso
FACTURE_MENSUELLE_ROLE = 1000


# ============================================
# 📝 LIENS DE RECRUTEMENT
# ============================================

# Lien du formulaire Google pour le recrutement modération
LIEN_FORM_MODERATION = "https://forms.google.com/(A REMPLIR)"

# Lien du formulaire Google pour le recrutement animation
LIEN_FORM_ANIMATION = "https://forms.google.com/(A REMPLIR)"


# ============================================
# 📢 SALONS
# ============================================

# ID du salon où envoyer les candidatures de tournage
# (à remplir avec l'ID du salon souhaité)
SALON_CANDIDATURES_TOURNAGE = None  # Exemple: 1234567890123456789


# ============================================
# 🎮 JEUX
# ============================================

# Liste de mots pour le jeu du Pendu (en majuscules)
MOTS_PENDU = [
    "DISCORD", "FORTNITE", "VICTOIRE", "GAMING", "STREAM",
    "TWITCH", "YOUTUBE", "MANETTE", "CLAVIER", "SOURIS",
    "ECRAN", "CASQUE", "MICRO", "SERVEUR", "SALON",
    "MESSAGE", "EMOJI", "REACTION", "BOOST", "NITRO",
    "SKIN", "EMOTE", "DANSE", "COMBAT", "EQUIPE",
    "PARTIE", "SCORE", "NIVEAU", "BADGE", "RANG"
]


# ============================================
# 🎨 COULEURS DES EMBEDS
# ============================================

# Couleurs en hexadécimal pour les embeds Discord
COULEUR_SUCCES = 0x2ECC71      # Vert
COULEUR_ERREUR = 0xE74C3C      # Rouge  
COULEUR_INFO = 0x3498DB        # Bleu
COULEUR_AVERTISSEMENT = 0xF39C12  # Orange
COULEUR_ECONOMIE = 0xF1C40F    # Jaune/Or
COULEUR_JEU = 0x9B59B6         # Violet


# ============================================
# 📊 EMOJIS PERSONNALISÉS
# ============================================

# Tu peux remplacer ces emojis par des emojis custom de ton serveur
EMOJI_SKYCOIN = "💰"
EMOJI_SUCCES = "✅"
EMOJI_ERREUR = "❌"
EMOJI_ATTENTE = "⏳"
EMOJI_VIP = "👑"
EMOJI_CADEAU = "🎁"
