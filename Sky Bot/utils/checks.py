# ============================================
# ✅ VÉRIFICATIONS COMMUNES
# ============================================
# Des fonctions pour vérifier des conditions
# avant d'exécuter des commandes.
# ============================================

import discord


def est_administrateur(membre: discord.Member) -> bool:
    """
    Vérifie si un membre est administrateur du serveur.
    
    Arguments:
        membre: Le membre Discord à vérifier
    
    Retourne:
        True si admin, False sinon
    """
    return membre.guild_permissions.administrator


def a_le_role(membre: discord.Member, role_id: int) -> bool:
    """
    Vérifie si un membre possède un rôle spécifique.
    
    Arguments:
        membre: Le membre Discord
        role_id: L'ID du rôle à vérifier
    
    Retourne:
        True si le membre a le rôle, False sinon
    """
    return any(role.id == role_id for role in membre.roles)


async def peut_gerer_roles(guild: discord.Guild, bot_member: discord.Member) -> bool:
    """
    Vérifie si le bot peut gérer les rôles (créer, attribuer, supprimer).
    
    Arguments:
        guild: Le serveur Discord
        bot_member: Le membre bot
    
    Retourne:
        True si le bot peut gérer les rôles
    """
    return bot_member.guild_permissions.manage_roles
