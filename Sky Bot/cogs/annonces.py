# ============================================
# 📢 COG ANNONCES & RECRUTEMENT
# ============================================
# Ce module gère :
# - /annonce-tournage : Formulaire pour postuler à un tournage
# - /recrutement : Liens vers les formulaires de recrutement
# ============================================

import discord
from discord.ext import commands
from discord import app_commands

from config import (
    GUILD_ID,
    LIEN_FORM_MODERATION,
    LIEN_FORM_ANIMATION,
    SALON_CANDIDATURES_TOURNAGE
)
from utils.embeds import embed_succes, embed_erreur, embed_info


# ============================================
# 📝 MODAL POUR CANDIDATURE TOURNAGE
# ============================================

class ModalCandidatureTournage(discord.ui.Modal):
    """
    Un "Modal" c'est une fenêtre popup avec des champs de texte.
    Ici, c'est le formulaire pour postuler à un tournage.
    """
    
    def __init__(self):
        super().__init__(title="📽️ Candidature Tournage")
    
    # Champ 1 : Pseudo Epic Games
    pseudo_epic = discord.ui.TextInput(
        label="Pseudo Epic Games",
        placeholder="Ex: SkyPlayer2000",
        required=True,
        max_length=100
    )
    
    # Champ 2 : Plateforme
    plateforme = discord.ui.TextInput(
        label="Plateforme",
        placeholder="PC / PlayStation / Xbox / Switch / Mobile",
        required=True,
        max_length=50
    )
    
    # Champ 3 : Disponibilités
    disponibilites = discord.ui.TextInput(
        label="Tes disponibilités",
        placeholder="Ex: Tous les soirs après 18h, week-ends...",
        style=discord.TextStyle.paragraph,  # Champ plus grand
        required=True,
        max_length=500
    )
    
    # Champ 4 : Informations supplémentaires
    infos = discord.ui.TextInput(
        label="Informations supplémentaires (optionnel)",
        placeholder="Expérience, motivation, équipement...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        Appelé quand le formulaire est envoyé.
        """
        # Crée l'embed récapitulatif
        embed = discord.Embed(
            title="📽️ Nouvelle Candidature Tournage",
            color=0xE91E63  # Rose
        )
        
        embed.add_field(
            name="👤 Candidat",
            value=f"{interaction.user.mention}\n`{interaction.user.name}`",
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID Discord",
            value=f"`{interaction.user.id}`",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Pseudo Epic Games",
            value=f"`{self.pseudo_epic.value}`",
            inline=True
        )
        
        embed.add_field(
            name="🖥️ Plateforme",
            value=self.plateforme.value,
            inline=True
        )
        
        embed.add_field(
            name="📅 Disponibilités",
            value=self.disponibilites.value,
            inline=False
        )
        
        if self.infos.value:
            embed.add_field(
                name="📝 Informations supplémentaires",
                value=self.infos.value,
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Candidature envoyée le {discord.utils.format_dt(discord.utils.utcnow(), 'F')}")
        
        # Détermine où envoyer la candidature
        if SALON_CANDIDATURES_TOURNAGE:
            # Si un salon est configuré, envoie la candidature dedans
            salon = interaction.guild.get_channel(SALON_CANDIDATURES_TOURNAGE)
            if salon:
                await salon.send(embed=embed)
                
                # Confirmation à l'utilisateur
                embed_confirmation = embed_succes(
                    "Candidature envoyée !",
                    "Ta candidature a été transmise au staff.\n"
                    "Tu seras contacté si tu es retenu ! 🎬"
                )
                await interaction.response.send_message(embed=embed_confirmation, ephemeral=True)
            else:
                # Salon non trouvé, envoie ici
                await interaction.response.send_message(embed=embed)
        else:
            # Pas de salon configuré, envoie dans le salon actuel
            await interaction.response.send_message(embed=embed)


class Annonces(commands.Cog):
    """
    Cog pour les annonces et le recrutement.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    # ================================
    # 📽️ COMMANDE /annonce-tournage
    # ================================
    @app_commands.command(
        name="annonce-tournage",
        description="Postule pour participer à un tournage !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def annonce_tournage(self, interaction: discord.Interaction):
        """
        Ouvre le formulaire de candidature pour un tournage.
        """
        await interaction.response.send_modal(ModalCandidatureTournage())
    
    # ================================
    # 👥 COMMANDE /recrutement
    # ================================
    @app_commands.command(
        name="recrutement",
        description="Obtiens les liens pour postuler au staff !"
    )
    @app_commands.describe(poste="Le poste pour lequel tu veux postuler")
    @app_commands.choices(poste=[
        app_commands.Choice(name="🛡️ Modération", value="moderation"),
        app_commands.Choice(name="🎉 Animation", value="animation"),
    ])
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def recrutement(
        self,
        interaction: discord.Interaction,
        poste: app_commands.Choice[str]
    ):
        """
        Envoie le lien du formulaire Google Forms correspondant au poste choisi.
        """
        if poste.value == "moderation":
            lien = LIEN_FORM_MODERATION
            titre = "🛡️ Recrutement Modération"
            description = (
                "Tu veux rejoindre l'équipe de modération ?\n\n"
                "**Ce qu'on recherche :**\n"
                "• Être actif et disponible\n"
                "• Avoir une bonne connaissance de Discord\n"
                "• Être mature et responsable\n"
                "• Savoir gérer les conflits\n\n"
                f"**👉 [Clique ici pour postuler !]({lien})**"
            )
            couleur = 0x3498DB  # Bleu
            
        else:  # animation
            lien = LIEN_FORM_ANIMATION
            titre = "🎉 Recrutement Animation"
            description = (
                "Tu veux rejoindre l'équipe d'animation ?\n\n"
                "**Ce qu'on recherche :**\n"
                "• Être créatif et dynamique\n"
                "• Avoir des idées d'événements\n"
                "• Savoir animer une communauté\n"
                "• Être disponible pour organiser des events\n\n"
                f"**👉 [Clique ici pour postuler !]({lien})**"
            )
            couleur = 0xE91E63  # Rose
        
        embed = discord.Embed(
            title=titre,
            description=description,
            color=couleur
        )
        embed.set_footer(text="Bonne chance pour ta candidature ! 🍀")
        
        # Ajoute un bouton avec le lien
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="📝 Remplir le formulaire",
            url=lien,
            style=discord.ButtonStyle.link
        ))
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Annonces(bot))
