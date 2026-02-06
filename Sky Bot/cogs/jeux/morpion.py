# ============================================
# ❌⭕ JEU DU MORPION (TIC-TAC-TOE)
# ============================================
# Un jeu de morpion complet jouable sur Discord
# avec des boutons interactifs !
# ============================================

import discord
from discord.ext import commands
from discord import app_commands
import random

from config import GUILD_ID
from utils.embeds import embed_jeu, embed_succes, embed_erreur, embed_info
from utils.database import modifier_solde, obtenir_solde


class BoutonCase(discord.ui.Button):
    """
    Un bouton représentant une case du morpion.
    """
    
    def __init__(self, x: int, y: int):
        # Position de la case dans la grille (0-2, 0-2)
        self.x = x
        self.y = y
        
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="\u200b",  # Caractère invisible pour avoir un bouton vide
            row=y
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Appelé quand on clique sur une case."""
        # Vérifie que c'est bien le tour du joueur
        assert self.view is not None
        view: VueMorpion = self.view
        
        # Vérifie que c'est un des deux joueurs
        if interaction.user.id not in [view.joueur_x.id, view.joueur_o.id]:
            return await interaction.response.send_message(
                "Tu ne participes pas à cette partie !",
                ephemeral=True
            )
        
        # Vérifie que c'est le bon tour
        joueur_actuel = view.joueur_x if view.tour_x else view.joueur_o
        if interaction.user.id != joueur_actuel.id:
            return await interaction.response.send_message(
                "Ce n'est pas ton tour !",
                ephemeral=True
            )
        
        # Place le symbole
        symbole = "❌" if view.tour_x else "⭕"
        view.grille[self.y][self.x] = symbole
        
        # Met à jour le bouton
        self.label = symbole
        self.style = discord.ButtonStyle.danger if view.tour_x else discord.ButtonStyle.primary
        self.disabled = True
        
        # Vérifie s'il y a un gagnant
        gagnant = view.verifier_victoire()
        match_nul = view.verifier_match_nul()
        
        if gagnant:
            # Désactive tous les boutons
            for item in view.children:
                item.disabled = True
            
            # Détermine le gagnant
            if gagnant == "❌":
                vainqueur = view.joueur_x
                perdant = view.joueur_o
            else:
                vainqueur = view.joueur_o
                perdant = view.joueur_x
            
            embed = embed_succes(
                "Victoire !",
                f"🎉 {vainqueur.mention} a gagné !\n\n"
                f"{view.afficher_grille()}"
            )
            
            view.stop()
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif match_nul:
            # Désactive tous les boutons
            for item in view.children:
                item.disabled = True
            
            embed = embed_info(
                "Match Nul !",
                f"🤝 Personne n'a gagné !\n\n"
                f"{view.afficher_grille()}"
            )
            
            view.stop()
            await interaction.response.edit_message(embed=embed, view=view)
            
        else:
            # Change de tour
            view.tour_x = not view.tour_x
            prochain_joueur = view.joueur_x if view.tour_x else view.joueur_o
            symbole_prochain = "❌" if view.tour_x else "⭕"
            
            embed = embed_jeu(
                "Morpion",
                f"C'est au tour de {prochain_joueur.mention} ({symbole_prochain})\n\n"
                f"**{view.joueur_x.display_name}** (❌) vs **{view.joueur_o.display_name}** (⭕)\n\n"
                f"{view.afficher_grille()}"
            )
            
            await interaction.response.edit_message(embed=embed, view=view)


class VueMorpion(discord.ui.View):
    """
    Vue contenant la grille de morpion.
    """
    
    def __init__(self, joueur_x: discord.Member, joueur_o: discord.Member):
        super().__init__(timeout=300)  # 5 minutes
        
        self.joueur_x = joueur_x  # Premier joueur (❌)
        self.joueur_o = joueur_o  # Deuxième joueur (⭕)
        self.tour_x = True  # True = tour de X, False = tour de O
        
        # Grille 3x3 (None = case vide)
        self.grille = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        
        # Ajoute les 9 boutons
        for y in range(3):
            for x in range(3):
                self.add_item(BoutonCase(x, y))
    
    def afficher_grille(self) -> str:
        """Retourne une représentation textuelle de la grille."""
        lignes = []
        for ligne in self.grille:
            cases = []
            for case in ligne:
                if case is None:
                    cases.append("⬜")
                else:
                    cases.append(case)
            lignes.append(" ".join(cases))
        return "\n".join(lignes)
    
    def verifier_victoire(self) -> str | None:
        """
        Vérifie s'il y a un gagnant.
        Retourne le symbole gagnant ("❌" ou "⭕") ou None.
        """
        # Lignes horizontales
        for ligne in self.grille:
            if ligne[0] and ligne[0] == ligne[1] == ligne[2]:
                return ligne[0]
        
        # Colonnes verticales
        for x in range(3):
            if self.grille[0][x] and self.grille[0][x] == self.grille[1][x] == self.grille[2][x]:
                return self.grille[0][x]
        
        # Diagonales
        if self.grille[0][0] and self.grille[0][0] == self.grille[1][1] == self.grille[2][2]:
            return self.grille[0][0]
        if self.grille[0][2] and self.grille[0][2] == self.grille[1][1] == self.grille[2][0]:
            return self.grille[0][2]
        
        return None
    
    def verifier_match_nul(self) -> bool:
        """Vérifie si toutes les cases sont remplies (match nul)."""
        for ligne in self.grille:
            for case in ligne:
                if case is None:
                    return False
        return True
    
    async def on_timeout(self):
        """Appelé quand le timeout est atteint."""
        for item in self.children:
            item.disabled = True


class VueChoixAdversaire(discord.ui.View):
    """
    Vue pour choisir l'adversaire du morpion.
    """
    
    def __init__(self, joueur: discord.Member):
        super().__init__(timeout=60)
        self.joueur = joueur
        self.adversaire = None
    
    @discord.ui.button(label="🎲 Adversaire Aléatoire", style=discord.ButtonStyle.primary)
    async def aleatoire(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cherche un adversaire aléatoire."""
        if interaction.user.id != self.joueur.id:
            return await interaction.response.send_message(
                "Ce n'est pas ton bouton !",
                ephemeral=True
            )
        
        # On attend qu'un autre membre clique sur le bouton "Rejoindre"
        embed = embed_jeu(
            "Morpion - Recherche d'adversaire",
            f"{self.joueur.mention} cherche un adversaire !\n\n"
            "Clique sur **Rejoindre** pour l'affronter !"
        )
        
        vue_rejoindre = VueRejoindre(self.joueur)
        await interaction.response.edit_message(embed=embed, view=vue_rejoindre)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def annuler(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annule la recherche."""
        if interaction.user.id != self.joueur.id:
            return await interaction.response.send_message(
                "Ce n'est pas ton bouton !",
                ephemeral=True
            )
        
        embed = embed_erreur("Partie annulée", "Tu as annulé la partie.")
        await interaction.response.edit_message(embed=embed, view=None)


class VueRejoindre(discord.ui.View):
    """
    Vue pour rejoindre une partie de morpion.
    """
    
    def __init__(self, joueur: discord.Member):
        super().__init__(timeout=120)
        self.joueur = joueur
    
    @discord.ui.button(label="🎮 Rejoindre la partie", style=discord.ButtonStyle.success)
    async def rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Un joueur rejoint la partie."""
        if interaction.user.id == self.joueur.id:
            return await interaction.response.send_message(
                "Tu ne peux pas jouer contre toi-même ! 😅",
                ephemeral=True
            )
        
        # Détermine aléatoirement qui joue en premier
        if random.choice([True, False]):
            joueur_x = self.joueur
            joueur_o = interaction.user
        else:
            joueur_x = interaction.user
            joueur_o = self.joueur
        
        # Lance la partie
        embed = embed_jeu(
            "Morpion",
            f"C'est au tour de {joueur_x.mention} (❌)\n\n"
            f"**{joueur_x.display_name}** (❌) vs **{joueur_o.display_name}** (⭕)"
        )
        
        vue = VueMorpion(joueur_x, joueur_o)
        await interaction.response.edit_message(embed=embed, view=vue)


class Morpion(commands.Cog):
    """
    Cog pour le jeu du Morpion.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="morpion",
        description="Lance une partie de Morpion !"
    )
    @app_commands.describe(adversaire="La personne contre qui tu veux jouer (optionnel)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def morpion(
        self,
        interaction: discord.Interaction,
        adversaire: discord.Member = None
    ):
        """
        Lance une partie de morpion.
        Si un adversaire est mentionné, la partie commence directement.
        Sinon, propose de chercher un adversaire aléatoire.
        """
        if adversaire:
            # Vérifie qu'on ne joue pas contre soi-même
            if adversaire.id == interaction.user.id:
                return await interaction.response.send_message(
                    "Tu ne peux pas jouer contre toi-même ! 😅",
                    ephemeral=True
                )
            
            # Vérifie que ce n'est pas un bot
            if adversaire.bot:
                return await interaction.response.send_message(
                    "Tu ne peux pas jouer contre un bot !",
                    ephemeral=True
                )
            
            # Détermine aléatoirement qui joue en premier
            if random.choice([True, False]):
                joueur_x = interaction.user
                joueur_o = adversaire
            else:
                joueur_x = adversaire
                joueur_o = interaction.user
            
            embed = embed_jeu(
                "Morpion",
                f"C'est au tour de {joueur_x.mention} (❌)\n\n"
                f"**{joueur_x.display_name}** (❌) vs **{joueur_o.display_name}** (⭕)"
            )
            
            vue = VueMorpion(joueur_x, joueur_o)
            await interaction.response.send_message(embed=embed, view=vue)
            
        else:
            # Propose de chercher un adversaire
            embed = embed_jeu(
                "Morpion",
                "Comment veux-tu jouer ?\n\n"
                "🎲 **Aléatoire** : N'importe qui peut te rejoindre"
            )
            
            vue = VueChoixAdversaire(interaction.user)
            await interaction.response.send_message(embed=embed, view=vue)


async def setup(bot):
    await bot.add_cog(Morpion(bot))
