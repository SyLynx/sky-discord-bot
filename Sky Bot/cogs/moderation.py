# ============================================
# 🛡️ COG MODÉRATION
# ============================================
# Ce module gère les commandes de modération :
# - /clear : Supprime entre 1 et 100 messages
# - /clear-salon : Supprime et recrée le salon
# ============================================

import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID
from utils.embeds import embed_succes, embed_erreur, embed_info


class Moderation(commands.Cog):
    """
    Cog pour les commandes de modération du serveur.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    # ================================
    # 🧹 COMMANDE /clear
    # ================================
    @app_commands.command(
        name="clear",
        description="[ADMIN] Supprime un nombre de messages dans le salon"
    )
    @app_commands.describe(
        nombre="Nombre de messages à supprimer (1-100)"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def clear(
        self,
        interaction: discord.Interaction,
        nombre: app_commands.Range[int, 1, 100]
    ):
        """
        Supprime entre 1 et 100 messages récents du salon.
        Note Discord : seuls les messages de moins de 14 jours peuvent être supprimés en masse.
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # purge() supprime les messages en masse (max 14 jours d'ancienneté)
            messages_supprimes = await interaction.channel.purge(limit=nombre)
            
            nb = len(messages_supprimes)
            
            embed = embed_succes(
                "Messages supprimés !",
                f"🧹 **{nb}** message{'s' if nb > 1 else ''} "
                f"{'ont été supprimés' if nb > 1 else 'a été supprimé'} dans ce salon."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except discord.Forbidden:
            embed = embed_erreur(
                "Permissions insuffisantes",
                "Je n'ai pas la permission de supprimer des messages dans ce salon !\n"
                "Vérifie que j'ai la permission **Gérer les messages**."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except discord.HTTPException as e:
            embed = embed_erreur(
                "Erreur",
                f"Une erreur s'est produite : {e}\n\n"
                "💡 **Note :** Discord ne permet pas de supprimer en masse "
                "des messages de plus de **14 jours**."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ================================
    # 💣 COMMANDE /clear-salon
    # ================================
    @app_commands.command(
        name="clear-salon",
        description="[ADMIN] Vide entièrement un salon en le recréant à l'identique"
    )
    @app_commands.describe(
        confirmation="Tape 'confirmer' pour valider (action irréversible !)"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def clear_salon(
        self,
        interaction: discord.Interaction,
        confirmation: str
    ):
        """
        Supprime le salon et le recrée au même endroit avec les mêmes
        permissions, catégorie, topic, slowmode, NSFW, etc.
        C'est la méthode la plus efficace pour vider TOUS les messages.
        """
        # Vérifie la confirmation
        if confirmation.lower() != "confirmer":
            embed = embed_erreur(
                "Confirmation requise",
                "⚠️ Cette action est **irréversible** !\n\n"
                "Pour confirmer, tape exactement :\n"
                "`/clear-salon confirmation:confirmer`\n\n"
                "**Tous les messages** de ce salon seront perdus définitivement."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        salon = interaction.channel
        
        # Sauvegarde toutes les propriétés du salon
        nom = salon.name
        categorie = salon.category
        position = salon.position
        topic = salon.topic
        slowmode = salon.slowmode_delay
        nsfw = salon.is_nsfw()
        overwrites = salon.overwrites  # Toutes les permissions personnalisées
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Crée le nouveau salon avec les mêmes propriétés
            nouveau_salon = await salon.guild.create_text_channel(
                name=nom,
                category=categorie,
                topic=topic,
                slowmode_delay=slowmode,
                nsfw=nsfw,
                overwrites=overwrites,
                position=position,
                reason=f"Clear-salon par {interaction.user.name}"
            )
            
            # Supprime l'ancien salon
            await salon.delete(reason=f"Clear-salon par {interaction.user.name}")
            
            # Envoie un message de confirmation dans le nouveau salon
            embed = embed_succes(
                "Salon vidé !",
                f"🧹 Le salon **#{nom}** a été vidé avec succès !\n\n"
                f"📋 Toutes les permissions ont été conservées.\n"
                f"👤 Action effectuée par {interaction.user.mention}"
            )
            await nouveau_salon.send(embed=embed)
        
        except discord.Forbidden:
            embed = embed_erreur(
                "Permissions insuffisantes",
                "Je n'ai pas les permissions nécessaires !\n\n"
                "Il me faut :\n"
                "• **Gérer les salons** (pour créer/supprimer)\n"
                "• **Gérer les rôles** (pour copier les permissions)"
            )
            # Le salon original existe encore, on peut répondre
            try:
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass
        
        except Exception as e:
            embed = embed_erreur("Erreur", f"Une erreur s'est produite : {e}")
            try:
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass


async def setup(bot):
    await bot.add_cog(Moderation(bot))
