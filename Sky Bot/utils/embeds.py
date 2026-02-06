# ============================================
# 🎨 GÉNÉRATEUR D'EMBEDS STYLISÉS
# ============================================
# Les "embeds" sont les jolis messages encadrés sur Discord.
# Ce fichier contient des fonctions pour créer des embeds
# de manière cohérente et jolie dans tout le bot.
# ============================================

import discord
from config import (
    COULEUR_SUCCES, COULEUR_ERREUR, COULEUR_INFO,
    COULEUR_AVERTISSEMENT, COULEUR_ECONOMIE, COULEUR_JEU,
    EMOJI_SUCCES, EMOJI_ERREUR, EMOJI_SKYCOIN, EMOJI_ATTENTE
)


def embed_succes(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed de succès (vert).
    
    Arguments:
        titre: Le titre de l'embed
        description: La description (optionnel)
    
    Exemple:
        embed = embed_succes("Achat réussi !", "Tu as acheté le rôle VIP.")
        await interaction.response.send_message(embed=embed)
    """
    embed = discord.Embed(
        title=f"{EMOJI_SUCCES} {titre}",
        description=description,
        color=COULEUR_SUCCES
    )
    return embed


def embed_erreur(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed d'erreur (rouge).
    
    Arguments:
        titre: Le titre de l'embed
        description: La description (optionnel)
    """
    embed = discord.Embed(
        title=f"{EMOJI_ERREUR} {titre}",
        description=description,
        color=COULEUR_ERREUR
    )
    return embed


def embed_info(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed d'information (bleu).
    
    Arguments:
        titre: Le titre de l'embed
        description: La description (optionnel)
    """
    embed = discord.Embed(
        title=f"ℹ️ {titre}",
        description=description,
        color=COULEUR_INFO
    )
    return embed


def embed_avertissement(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed d'avertissement (orange).
    """
    embed = discord.Embed(
        title=f"⚠️ {titre}",
        description=description,
        color=COULEUR_AVERTISSEMENT
    )
    return embed


def embed_economie(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed pour l'économie (jaune/or).
    """
    embed = discord.Embed(
        title=f"{EMOJI_SKYCOIN} {titre}",
        description=description,
        color=COULEUR_ECONOMIE
    )
    return embed


def embed_jeu(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed pour les jeux (violet).
    """
    embed = discord.Embed(
        title=f"🎮 {titre}",
        description=description,
        color=COULEUR_JEU
    )
    return embed


def embed_attente(titre: str, description: str = None) -> discord.Embed:
    """
    Crée un embed d'attente (bleu).
    """
    embed = discord.Embed(
        title=f"{EMOJI_ATTENTE} {titre}",
        description=description,
        color=COULEUR_INFO
    )
    return embed


def formater_temps(secondes: int) -> str:
    """
    Formate un temps en secondes en texte lisible.
    
    Arguments:
        secondes: Le temps en secondes
    
    Retourne:
        Un texte comme "2h 30m" ou "45m 20s"
    
    Exemple:
        formater_temps(3661) -> "1h 1m 1s"
    """
    if secondes < 60:
        return f"{secondes}s"
    
    minutes = secondes // 60
    secondes_restantes = secondes % 60
    
    if minutes < 60:
        if secondes_restantes > 0:
            return f"{minutes}m {secondes_restantes}s"
        return f"{minutes}m"
    
    heures = minutes // 60
    minutes_restantes = minutes % 60
    
    if heures < 24:
        if minutes_restantes > 0:
            return f"{heures}h {minutes_restantes}m"
        return f"{heures}h"
    
    jours = heures // 24
    heures_restantes = heures % 24
    
    if heures_restantes > 0:
        return f"{jours}j {heures_restantes}h"
    return f"{jours}j"


def formater_nombre(nombre: int) -> str:
    """
    Formate un nombre avec des espaces pour la lisibilité.
    
    Exemple:
        formater_nombre(15000) -> "15 000"
    """
    return f"{nombre:,}".replace(",", " ")
