# ============================================
# 📜 COG RÈGLEMENT
# ============================================
# Ce module gère le système de règlement :
# - /reglement : Affiche les règles avec un bouton
# - Bouton "J'accepte" : Attribue le rôle
# ============================================

import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID, ROLE_REGLEMENT_ID
from utils.embeds import embed_succes, embed_erreur, embed_info
from utils.checks import a_le_role


class BoutonReglement(discord.ui.View):
    """
    Vue contenant le bouton pour accepter le règlement.
    
    Une "View" en discord.py, c'est un conteneur pour les boutons
    et autres composants interactifs.
    """
    
    def __init__(self):
        # timeout=None = le bouton reste actif indéfiniment
        super().__init__(timeout=None)
    
    @discord.ui.button(
        label="✅ J'accepte le règlement",
        style=discord.ButtonStyle.success,
        custom_id="bouton_reglement"  # ID unique pour que le bouton fonctionne après redémarrage
    )
    async def accepter_reglement(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        """
        Appelé quand quelqu'un clique sur le bouton.
        Attribue le rôle de membre.
        """
        membre = interaction.user
        guild = interaction.guild
        
        # Récupère le rôle à attribuer
        role = guild.get_role(ROLE_REGLEMENT_ID)
        
        if not role:
            embed = embed_erreur(
                "Erreur de configuration",
                "Le rôle n'a pas été trouvé. Contacte un administrateur !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie si le membre a déjà le rôle
        if a_le_role(membre, ROLE_REGLEMENT_ID):
            embed = embed_info(
                "Déjà accepté !",
                "Tu as déjà accepté le règlement 😊"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Attribue le rôle
        try:
            await membre.add_roles(role, reason="Acceptation du règlement")
            
            embed = embed_succes(
                "Bienvenue !",
                f"Tu as accepté le règlement et reçu le rôle {role.mention} !\n\n"
                "Tu as maintenant accès à tous les salons du serveur. 🎉"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = embed_erreur(
                "Erreur de permissions",
                "Je n'ai pas la permission d'attribuer ce rôle.\n"
                "Vérifie que mon rôle est au-dessus du rôle à attribuer !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class Reglement(commands.Cog):
    """
    Cog pour le système de règlement.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Quand le bot démarre, on ajoute la vue pour que
        les boutons déjà envoyés fonctionnent toujours.
        """
        self.bot.add_view(BoutonReglement())
    
    # ================================
    # 📜 COMMANDE /reglement
    # ================================
    @app_commands.command(
        name="reglement",
        description="Affiche le règlement du serveur avec un bouton pour l'accepter"
    )
    @app_commands.default_permissions(administrator=True)  # Seuls les admins peuvent l'utiliser
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def reglement(self, interaction: discord.Interaction):
        """
        Envoie un embed avec les règles et un bouton pour les accepter.
        Seuls les administrateurs peuvent utiliser cette commande.
        """
        # Crée l'embed avec les règles
        embed = discord.Embed(
            title="📜 Règlement du Serveur",
            description=(
                "Bienvenue parmi nous ! Pour garantir une expérience agréable et sécurisée pour tous, "
                "merci de lire attentivement et d'accepter ce règlement.\n\n"
                
                "**1️⃣ Respect et Courtoisie**\n"
                "Les échanges doivent rester courtois et bienveillants. "
                "Le harcèlement, les insultes, la discrimination (racisme, sexisme, homophobie, etc.) "
                "et l'incitation à la haine sont strictement interdits.\n\n"
                
                "**2️⃣ Contenu Approprié**\n"
                "Ce serveur est ouvert à tous. "
                "La diffusion de contenu pornographique (NSFW), gore, violent, politique extrême "
                "ou illégal est prohibée dans tous les salons.\n\n"
                
                "**3️⃣ Tolérance Zéro Spam**\n"
                "Pour le confort de lecture, le flood, le spam de messages, "
                "l'abus de majuscules et les mentions inutiles (@everyone, etc.) sont sanctionnés.\n\n"
                
                "**4️⃣ Publicité et Auto-promotion**\n"
                "Toute forme de publicité (liens discord, chaînes, réseaux sociaux) est interdite "
                "sans l'autorisation explicite d'un administrateur, y compris par Message Privé.\n\n"
                
                "**5️⃣ Identité et Profil**\n"
                "Les pseudonymes et avatars doivent être décents et ne pas heurter la sensibilité. "
                "L'usurpation d'identité membre ou staff est interdite.\n\n"
                
                "**6️⃣ Protection de la Vie Privée**\n"
                "La divulgation d'informations personnelles (doxxing) sur vous-même ou sur autrui "
                "est formellement interdite pour des raisons de sécurité.\n\n"
                
                "**7️⃣ Langage et Expression**\n"
                "Veillez à utiliser un langage correct. Le langage SMS abusif est déconseillé "
                "afin de maintenir des discussions lisibles et agréables pour tous.\n\n"
                
                "**8️⃣ Autorité du Staff**\n"
                "Les modérateurs et administrateurs sont là pour veiller au bon fonctionnement du serveur. "
                "Leurs décisions ne sont pas contestables publiquement. En cas de désaccord, ouvrez un ticket.\n\n"
                
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "**✅ En cliquant sur le bouton ci-dessous, vous confirmez avoir lu et accepté ce règlement.**"
            ),
            color=0x5865F2  # Bleu Discord
        )
        embed.set_footer(text="En cliquant, tu acceptes de respecter ces règles.")
        
        # Envoie l'embed avec le bouton
        await interaction.response.send_message(
            embed=embed,
            view=BoutonReglement()
        )


async def setup(bot):
    await bot.add_cog(Reglement(bot))
