# ============================================
# 🎯 JEU DU PENDU
# ============================================
# Un jeu du pendu complet avec clavier interactif
# et représentation ASCII du pendu !
# ============================================

import discord
from discord.ext import commands
from discord import app_commands
import random

from config import GUILD_ID, MOTS_PENDU
from utils.embeds import embed_jeu, embed_succes, embed_erreur


# ASCII art du pendu selon le nombre d'erreurs
PENDU_ETAPES = [
    # 0 erreur
    """
    ┌───────┐
    │       │
    │       
    │      
    │      
    │
    ═══════════
    """,
    # 1 erreur - tête
    """
    ┌───────┐
    │       │
    │       😵
    │      
    │      
    │
    ═══════════
    """,
    # 2 erreurs - corps
    """
    ┌───────┐
    │       │
    │       😵
    │       │
    │       
    │
    ═══════════
    """,
    # 3 erreurs - bras gauche
    """
    ┌───────┐
    │       │
    │       😵
    │      /│
    │       
    │
    ═══════════
    """,
    # 4 erreurs - bras droit
    """
    ┌───────┐
    │       │
    │       😵
    │      /│\\
    │       
    │
    ═══════════
    """,
    # 5 erreurs - jambe gauche
    """
    ┌───────┐
    │       │
    │       😵
    │      /│\\
    │      / 
    │
    ═══════════
    """,
    # 6 erreurs - jambe droite (perdu)
    """
    ┌───────┐
    │       │
    │       💀
    │      /│\\
    │      / \\
    │
    ═══════════
    """
]


class BoutonLettre(discord.ui.Button):
    """
    Un bouton représentant une lettre du clavier.
    """
    
    def __init__(self, lettre: str, row: int):
        super().__init__(
            label=lettre,
            style=discord.ButtonStyle.secondary,
            row=row
        )
        self.lettre = lettre
    
    async def callback(self, interaction: discord.Interaction):
        """Appelé quand on clique sur une lettre."""
        view: VuePendu = self.view
        
        # Vérifie que c'est le bon joueur
        if interaction.user.id != view.joueur.id:
            return await interaction.response.send_message(
                "Ce n'est pas ta partie !",
                ephemeral=True
            )
        
        # Désactive le bouton
        self.disabled = True
        
        # Vérifie si la lettre est dans le mot
        if self.lettre in view.mot:
            self.style = discord.ButtonStyle.success
            view.lettres_trouvees.add(self.lettre)
        else:
            self.style = discord.ButtonStyle.danger
            view.erreurs += 1
            view.lettres_incorrectes.append(self.lettre)
        
        # Vérifie si la partie est terminée
        if view.a_gagne():
            embed = embed_succes(
                "Victoire !",
                f"🎉 Bravo ! Tu as trouvé le mot !\n\n"
                f"Le mot était : **{view.mot}**\n\n"
                f"```{PENDU_ETAPES[view.erreurs]}```"
            )
            for item in view.children:
                item.disabled = True
            view.stop()
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif view.a_perdu():
            embed = embed_erreur(
                "Perdu !",
                f"💀 Tu as été pendu !\n\n"
                f"Le mot était : **{view.mot}**\n\n"
                f"```{PENDU_ETAPES[6]}```"
            )
            for item in view.children:
                item.disabled = True
            view.stop()
            await interaction.response.edit_message(embed=embed, view=view)
            
        else:
            # Continue la partie
            embed = view.creer_embed()
            await interaction.response.edit_message(embed=embed, view=view)


class VuePendu(discord.ui.View):
    """
    Vue contenant le clavier pour le jeu du pendu.
    """
    
    def __init__(self, joueur: discord.Member, mot: str):
        super().__init__(timeout=300)  # 5 minutes
        
        self.joueur = joueur
        self.mot = mot.upper()
        self.erreurs = 0
        self.lettres_trouvees = set()
        self.lettres_incorrectes = []
        
        # Ajoute les lettres du clavier
        # Rangée 1: A-I (9 lettres)
        for lettre in "AZERTYUIO":
            self.add_item(BoutonLettre(lettre, 0))
        
        # Rangée 2: J-R (8 lettres + espace)
        for lettre in "QSDFGHJKL":
            self.add_item(BoutonLettre(lettre, 1))
        
        # Rangée 3: S-Z (8 lettres)
        for lettre in "WXCVBNMP":
            self.add_item(BoutonLettre(lettre, 2))
    
    def afficher_mot(self) -> str:
        """Affiche le mot avec les lettres trouvées et des underscores."""
        resultat = []
        for lettre in self.mot:
            if lettre in self.lettres_trouvees:
                resultat.append(lettre)
            elif lettre == " ":
                resultat.append(" ")
            else:
                resultat.append("_")
        return " ".join(resultat)
    
    def a_gagne(self) -> bool:
        """Vérifie si le joueur a trouvé toutes les lettres."""
        for lettre in self.mot:
            if lettre != " " and lettre not in self.lettres_trouvees:
                return False
        return True
    
    def a_perdu(self) -> bool:
        """Vérifie si le joueur a fait 6 erreurs."""
        return self.erreurs >= 6
    
    def creer_embed(self) -> discord.Embed:
        """Crée l'embed du jeu."""
        embed = embed_jeu(
            "Jeu du Pendu",
            f"**Joueur** : {self.joueur.mention}\n\n"
            f"```{PENDU_ETAPES[self.erreurs]}```\n"
            f"**Mot** : `{self.afficher_mot()}`\n\n"
            f"**Erreurs** : {self.erreurs}/6\n"
            f"**Lettres incorrectes** : {', '.join(self.lettres_incorrectes) if self.lettres_incorrectes else 'Aucune'}"
        )
        return embed


class Pendu(commands.Cog):
    """
    Cog pour le jeu du Pendu.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="pendu",
        description="Lance une partie de Pendu !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def pendu(self, interaction: discord.Interaction):
        """
        Lance une partie de pendu avec un mot aléatoire.
        """
        # Choisit un mot aléatoire
        mot = random.choice(MOTS_PENDU)
        
        # Crée la vue
        vue = VuePendu(interaction.user, mot)
        embed = vue.creer_embed()
        
        await interaction.response.send_message(embed=embed, view=vue)


async def setup(bot):
    await bot.add_cog(Pendu(bot))
