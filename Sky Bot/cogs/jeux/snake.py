# ============================================
# 🐍 JEU DU SNAKE
# ============================================
# Un jeu Snake adapté pour Discord avec une
# grille emoji et des boutons directionnels !
# ============================================

import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

from config import GUILD_ID, EMOJI_SKYCOIN
from utils.embeds import embed_jeu, embed_succes, embed_erreur
from utils.database import modifier_solde


# Émojis pour le jeu
EMOJI_VIDE = "⬛"
EMOJI_SERPENT = "🟩"
EMOJI_TETE = "🐍"
EMOJI_POMME = "🍎"
EMOJI_MUR = "🟫"


class VueSnake(discord.ui.View):
    """
    Vue contenant les contrôles du Snake.
    """
    
    def __init__(self, joueur: discord.Member, taille_grille: int = 8):
        super().__init__(timeout=120)  # 2 minutes max
        
        self.joueur = joueur
        self.taille = taille_grille
        self.score = 0
        self.partie_finie = False
        
        # Direction actuelle : 0=haut, 1=droite, 2=bas, 3=gauche
        self.direction = 1  # Commence vers la droite
        
        # Position du serpent (liste de tuples (x, y))
        # La tête est le premier élément
        centre = taille_grille // 2
        self.serpent = [(centre, centre), (centre - 1, centre), (centre - 2, centre)]
        
        # Position de la pomme
        self.pomme = self.spawn_pomme()
    
    def spawn_pomme(self) -> tuple:
        """Place une pomme à une position aléatoire libre."""
        positions_libres = []
        for x in range(self.taille):
            for y in range(self.taille):
                if (x, y) not in self.serpent:
                    positions_libres.append((x, y))
        
        if not positions_libres:
            return None
        
        return random.choice(positions_libres)
    
    def afficher_grille(self) -> str:
        """Génère l'affichage de la grille en émojis."""
        lignes = []
        
        for y in range(self.taille):
            ligne = []
            for x in range(self.taille):
                pos = (x, y)
                
                if pos == self.serpent[0]:  # Tête
                    ligne.append(EMOJI_TETE)
                elif pos in self.serpent:  # Corps
                    ligne.append(EMOJI_SERPENT)
                elif pos == self.pomme:  # Pomme
                    ligne.append(EMOJI_POMME)
                else:  # Vide
                    ligne.append(EMOJI_VIDE)
            
            lignes.append("".join(ligne))
        
        return "\n".join(lignes)
    
    def bouger(self, nouvelle_direction: int) -> bool:
        """
        Déplace le serpent dans une direction.
        Retourne False si le serpent meurt.
        """
        # Empêche de faire demi-tour
        opposees = {0: 2, 1: 3, 2: 0, 3: 1}
        if nouvelle_direction == opposees.get(self.direction):
            nouvelle_direction = self.direction
        
        self.direction = nouvelle_direction
        
        # Calcule la nouvelle position de la tête
        tete_x, tete_y = self.serpent[0]
        
        if self.direction == 0:  # Haut
            nouvelle_tete = (tete_x, tete_y - 1)
        elif self.direction == 1:  # Droite
            nouvelle_tete = (tete_x + 1, tete_y)
        elif self.direction == 2:  # Bas
            nouvelle_tete = (tete_x, tete_y + 1)
        else:  # Gauche
            nouvelle_tete = (tete_x - 1, tete_y)
        
        # Vérifie les collisions avec les murs
        if (nouvelle_tete[0] < 0 or nouvelle_tete[0] >= self.taille or
            nouvelle_tete[1] < 0 or nouvelle_tete[1] >= self.taille):
            return False
        
        # Vérifie les collisions avec le corps
        if nouvelle_tete in self.serpent[:-1]:
            return False
        
        # Ajoute la nouvelle tête
        self.serpent.insert(0, nouvelle_tete)
        
        # Vérifie si on mange une pomme
        if nouvelle_tete == self.pomme:
            self.score += 1
            self.pomme = self.spawn_pomme()
            # Ne pas enlever la queue = le serpent grandit
        else:
            # Enlève la queue
            self.serpent.pop()
        
        return True
    
    def creer_embed(self) -> discord.Embed:
        """Crée l'embed du jeu."""
        embed = embed_jeu(
            "Snake",
            f"**Joueur** : {self.joueur.mention}\n"
            f"**Score** : {self.score} 🍎\n\n"
            f"{self.afficher_grille()}\n\n"
            f"Utilise les boutons pour diriger le serpent !"
        )
        return embed
    
    async def terminer_partie(self, interaction: discord.Interaction, victoire: bool = False):
        """Termine la partie."""
        self.partie_finie = True
        
        for item in self.children:
            item.disabled = True
        
        # Calcule les récompenses
        recompense = self.score * 10  # 10 Skycoins par pomme mangée
        
        if victoire:
            embed = embed_succes(
                "Victoire Parfaite !",
                f"🎉 Incroyable ! Tu as rempli toute la grille !\n\n"
                f"**Score final** : {self.score} 🍎\n"
                f"**Récompense** : +{recompense} {EMOJI_SKYCOIN} Skycoins"
            )
        else:
            embed = embed_erreur(
                "Game Over !",
                f"💀 Tu as percuté un mur ou ton propre corps !\n\n"
                f"{self.afficher_grille()}\n\n"
                f"**Score final** : {self.score} 🍎\n"
                f"**Récompense** : +{recompense} {EMOJI_SKYCOIN} Skycoins"
            )
        
        # Ajoute les Skycoins si le score > 0
        if recompense > 0:
            modifier_solde(self.joueur.id, recompense)
        
        self.stop()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def gerer_mouvement(self, interaction: discord.Interaction, direction: int):
        """Gère un mouvement."""
        if interaction.user.id != self.joueur.id:
            return await interaction.response.send_message(
                "Ce n'est pas ta partie !",
                ephemeral=True
            )
        
        if self.partie_finie:
            return
        
        survit = self.bouger(direction)
        
        if not survit:
            await self.terminer_partie(interaction)
        elif self.pomme is None:  # Plus de place pour les pommes = victoire
            await self.terminer_partie(interaction, victoire=True)
        else:
            embed = self.creer_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    # Boutons de direction
    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.secondary, disabled=True, row=0)
    async def vide1(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    
    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.primary, row=0)
    async def haut(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerer_mouvement(interaction, 0)
    
    @discord.ui.button(label="\u200b", style=discord.ButtonStyle.secondary, disabled=True, row=0)
    async def vide2(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, row=1)
    async def gauche(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerer_mouvement(interaction, 3)
    
    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.primary, row=1)
    async def bas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerer_mouvement(interaction, 2)
    
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary, row=1)
    async def droite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerer_mouvement(interaction, 1)


class Snake(commands.Cog):
    """
    Cog pour le jeu Snake.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="snake",
        description="Lance une partie de Snake !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def snake(self, interaction: discord.Interaction):
        """
        Lance une partie de Snake.
        Utilise les boutons pour diriger le serpent.
        Mange des pommes pour gagner des Skycoins !
        """
        vue = VueSnake(interaction.user)
        embed = vue.creer_embed()
        
        await interaction.response.send_message(embed=embed, view=vue)


async def setup(bot):
    await bot.add_cog(Snake(bot))
