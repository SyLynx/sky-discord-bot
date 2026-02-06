# ============================================
# 💰 COG ÉCONOMIE
# ============================================
# Ce module gère tout le système d'économie :
# - /day, /week, /month (récompenses avec cooldown)
# - /solde (voir son argent)
# - /classement (top des plus riches)
# ============================================

import discord
from discord.ext import commands
from discord import app_commands

from config import (
    GUILD_ID,
    RECOMPENSE_JOUR, RECOMPENSE_SEMAINE, RECOMPENSE_MOIS,
    COOLDOWN_JOUR, COOLDOWN_SEMAINE, COOLDOWN_MOIS,
    EMOJI_SKYCOIN
)
from utils.database import (
    obtenir_solde, modifier_solde,
    verifier_cooldown, enregistrer_cooldown,
    obtenir_classement
)
from utils.embeds import (
    embed_succes, embed_erreur, embed_economie,
    formater_temps, formater_nombre
)


class Economie(commands.Cog):
    """
    Cog pour le système d'économie du serveur.
    
    Un "Cog" c'est comme un module/plugin qui ajoute des commandes au bot.
    Ça permet d'organiser le code proprement.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    # ================================
    # 📅 COMMANDE /day
    # ================================
    @app_commands.command(
        name="day",
        description="Récupère ta récompense quotidienne de Skycoins !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def day(self, interaction: discord.Interaction):
        """
        Commande pour récupérer 500 Skycoins par jour.
        Cooldown : 24 heures
        """
        user_id = interaction.user.id
        
        # Vérifie si le cooldown est terminé
        peut_utiliser, temps_restant = verifier_cooldown(
            user_id, "day", COOLDOWN_JOUR
        )
        
        if not peut_utiliser:
            # Le joueur doit encore attendre
            embed = embed_erreur(
                "Patience !",
                f"Tu pourras récupérer ta récompense quotidienne dans **{formater_temps(temps_restant)}** !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Ajoute les Skycoins et enregistre le cooldown
        nouveau_solde = modifier_solde(user_id, RECOMPENSE_JOUR)
        enregistrer_cooldown(user_id, "day")
        
        # Message de succès
        embed = embed_economie(
            "Récompense Quotidienne !",
            f"Tu as reçu **+{formater_nombre(RECOMPENSE_JOUR)}** {EMOJI_SKYCOIN} Skycoins !\n\n"
            f"💳 Nouveau solde : **{formater_nombre(nouveau_solde)}** Skycoins"
        )
        embed.set_footer(text="Reviens demain pour une nouvelle récompense !")
        
        await interaction.response.send_message(embed=embed)
    
    # ================================
    # 📅 COMMANDE /week
    # ================================
    @app_commands.command(
        name="week",
        description="Récupère ta récompense hebdomadaire de Skycoins !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def week(self, interaction: discord.Interaction):
        """
        Commande pour récupérer 1000 Skycoins par semaine.
        Cooldown : 7 jours
        """
        user_id = interaction.user.id
        
        peut_utiliser, temps_restant = verifier_cooldown(
            user_id, "week", COOLDOWN_SEMAINE
        )
        
        if not peut_utiliser:
            embed = embed_erreur(
                "Patience !",
                f"Tu pourras récupérer ta récompense hebdomadaire dans **{formater_temps(temps_restant)}** !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        nouveau_solde = modifier_solde(user_id, RECOMPENSE_SEMAINE)
        enregistrer_cooldown(user_id, "week")
        
        embed = embed_economie(
            "Récompense Hebdomadaire !",
            f"Tu as reçu **+{formater_nombre(RECOMPENSE_SEMAINE)}** {EMOJI_SKYCOIN} Skycoins !\n\n"
            f"💳 Nouveau solde : **{formater_nombre(nouveau_solde)}** Skycoins"
        )
        embed.set_footer(text="Reviens la semaine prochaine pour une nouvelle récompense !")
        
        await interaction.response.send_message(embed=embed)
    
    # ================================
    # 📅 COMMANDE /month
    # ================================
    @app_commands.command(
        name="month",
        description="Récupère ta récompense mensuelle de Skycoins !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def month(self, interaction: discord.Interaction):
        """
        Commande pour récupérer 2000 Skycoins par mois.
        Cooldown : 30 jours
        """
        user_id = interaction.user.id
        
        peut_utiliser, temps_restant = verifier_cooldown(
            user_id, "month", COOLDOWN_MOIS
        )
        
        if not peut_utiliser:
            embed = embed_erreur(
                "Patience !",
                f"Tu pourras récupérer ta récompense mensuelle dans **{formater_temps(temps_restant)}** !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        nouveau_solde = modifier_solde(user_id, RECOMPENSE_MOIS)
        enregistrer_cooldown(user_id, "month")
        
        embed = embed_economie(
            "Récompense Mensuelle !",
            f"Tu as reçu **+{formater_nombre(RECOMPENSE_MOIS)}** {EMOJI_SKYCOIN} Skycoins !\n\n"
            f"💳 Nouveau solde : **{formater_nombre(nouveau_solde)}** Skycoins"
        )
        embed.set_footer(text="Reviens le mois prochain pour une nouvelle récompense !")
        
        await interaction.response.send_message(embed=embed)
    
    # ================================
    # 💳 COMMANDE /solde
    # ================================
    @app_commands.command(
        name="solde",
        description="Affiche ton solde de Skycoins (ou celui d'un autre membre)"
    )
    @app_commands.describe(membre="Le membre dont tu veux voir le solde (optionnel)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def solde(
        self,
        interaction: discord.Interaction,
        membre: discord.Member = None
    ):
        """
        Affiche le solde d'un utilisateur.
        Si aucun membre n'est mentionné, affiche le solde de l'utilisateur.
        """
        # Si pas de membre spécifié, on prend l'utilisateur qui a fait la commande
        cible = membre or interaction.user
        solde = obtenir_solde(cible.id)
        
        # Détermine si c'est son propre solde ou celui d'un autre
        if cible.id == interaction.user.id:
            titre = "Ton Solde"
            description = f"Tu possèdes **{formater_nombre(solde)}** {EMOJI_SKYCOIN} Skycoins"
        else:
            titre = f"Solde de {cible.display_name}"
            description = f"{cible.mention} possède **{formater_nombre(solde)}** {EMOJI_SKYCOIN} Skycoins"
        
        embed = embed_economie(titre, description)
        embed.set_thumbnail(url=cible.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    # ================================
    # 🏆 COMMANDE /classement
    # ================================
    @app_commands.command(
        name="classement",
        description="Affiche le top 10 des membres les plus riches !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def classement(self, interaction: discord.Interaction):
        """
        Affiche le classement des 10 membres les plus riches.
        """
        await interaction.response.defer()  # Peut prendre du temps
        
        classement = obtenir_classement(10)
        
        if not classement:
            embed = embed_erreur(
                "Classement vide",
                "Personne n'a encore de Skycoins !\nUtilise `/day` pour commencer."
            )
            return await interaction.followup.send(embed=embed)
        
        # Construit le texte du classement
        lignes = []
        for i, (user_id, solde) in enumerate(classement, start=1):
            # Émojis pour le podium
            if i == 1:
                emoji = "🥇"
            elif i == 2:
                emoji = "🥈"
            elif i == 3:
                emoji = "🥉"
            else:
                emoji = f"**{i}.**"
            
            # Essaie de récupérer le nom du membre
            try:
                membre = await self.bot.fetch_user(int(user_id))
                nom = membre.display_name
            except:
                nom = f"Utilisateur inconnu"
            
            lignes.append(f"{emoji} {nom} — **{formater_nombre(solde)}** {EMOJI_SKYCOIN}")
        
        embed = embed_economie(
            "🏆 Classement des Skycoins",
            "\n".join(lignes)
        )
        
        # Ajoute la position de l'utilisateur s'il n'est pas dans le top 10
        user_solde = obtenir_solde(interaction.user.id)
        position = None
        for i, (user_id, _) in enumerate(obtenir_classement(100), start=1):
            if int(user_id) == interaction.user.id:
                position = i
                break
        
        if position and position > 10:
            embed.set_footer(text=f"Ta position : #{position} avec {formater_nombre(user_solde)} Skycoins")
        
        await interaction.followup.send(embed=embed)


# ============================================
# 🔧 FONCTION DE SETUP
# ============================================
# Cette fonction est appelée automatiquement par Discord.py
# quand le bot charge ce cog.

async def setup(bot):
    await bot.add_cog(Economie(bot))
