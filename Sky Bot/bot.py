# ============================================
# 🤖 CLASSE PRINCIPALE DU BOT
# ============================================
# Cette classe gère tout le bot : connexion, 
# chargement des modules (cogs), événements...
# ============================================

import discord
from discord.ext import commands
import asyncio
import os

from config import GUILD_ID


class SkyBot(commands.Bot):
    """
    Classe principale du bot Discord de Sky.
    
    Un "Bot" c'est comme le cerveau de ton application Discord.
    Il gère toutes les commandes, les événements, et la connexion.
    """
    
    def __init__(self):
        # Configuration des "intents" (permissions du bot)
        # all() = le bot peut tout voir (messages, membres, etc.)
        intents = discord.Intents.all()
        
        # Initialise le bot avec un préfixe de commande
        # Pas vraiment utilisé ici car le bot utilise surtout des slash commands
        super().__init__(
            command_prefix="!",  # Préfixe pour les commandes texte, exemple : !aide
            intents=intents,
            help_command=None  # On désactive la commande d'aide par défaut
        )
        
        # L'objet "guild" représente ton serveur Discord
        self.guild_object = discord.Object(id=GUILD_ID)
    
    async def setup_hook(self):
        """
        Cette fonction s'exécute AVANT que le bot soit complètement connecté.
        C'est ici qu'on charge tous les modules (cogs).
        
        Un "cog" c'est comme un plugin : ça ajoute des fonctionnalités au bot.
        """
        print("🔧 Chargement des modules...")
        
        # Liste des cogs à charger
        # Chaque cog est dans un fichier séparé dans le dossier "cogs/"
        cogs_a_charger = [
            "cogs.economie",      # Système d'économie (/day, /week, /month, /solde)
            "cogs.reglement",     # Système de règlement avec bouton
            "cogs.annonces",      # Annonces tournage + recrutement
            "cogs.shop",          # Boutique (rôles VIP et perso)
            "cogs.giveaway",      # Système de giveaway
            "cogs.moderation",    # Commandes de modération (/clear, /clear-salon)

            # Protection anti-ping de Sky
            # Supprime automatiquement les messages qui mentionnent Sky
            "cogs.ping_guard",

            "cogs.jeux.morpion",  # Jeu du Morpion
            "cogs.jeux.pendu",    # Jeu du Pendu
            "cogs.jeux.snake",    # Jeu du Snake
        ]
        
        # Charge chaque cog un par un
        for cog in cogs_a_charger:
            try:
                await self.load_extension(cog)
                print(f"  ✅ {cog} chargé")
            except Exception as e:
                print(f"  ❌ Erreur en chargeant {cog}: {e}")
        
        # Synchronise les slash commands avec Discord
        # Cela permet à Discord de connaître les commandes disponibles
        print("🔄 Synchronisation des commandes...")
        
        # Nettoie les commandes globales résiduelles
        # Cela évite les doublons.
        #
        # Les commandes sont toutes enregistrées au niveau du serveur,
        # donc on vide les commandes globales pour ne pas avoir de doublons.
        self.tree.clear_commands(guild=None)
        await self.tree.sync()  # Sync global vide = supprime les commandes globales
        
        # Synchronise les commandes du serveur
        await self.tree.sync(guild=self.guild_object)
        print("✅ Commandes synchronisées !")
    
    async def on_ready(self):
        """
        Cette fonction s'exécute quand le bot est complètement connecté et prêt.
        """
        print("=" * 50)
        print(f"🚀 {self.user.name} est en ligne !")
        print(f"🆔 ID du bot : {self.user.id}")
        print(f"🌐 Serveurs connectés : {len(self.guilds)}")
        print("=" * 50)
        
        # Change le statut du bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="code créateur: skyeee ⭐"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """
        Gère les erreurs des commandes.
        Ça évite que le bot plante quand quelqu'un fait une erreur.
        """
        # Si la commande n'existe pas, on ignore
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Pour les autres erreurs, on affiche dans la console
        print(f"❌ Erreur: {error}")
