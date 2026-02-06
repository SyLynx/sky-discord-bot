# ============================================
# 🛒 COG BOUTIQUE (SHOP)
# ============================================
# Ce module gère la boutique :
# - /shop : Affiche la boutique
# - Achat rôle VIP (5000 Skycoins, 1 mois)
# - Achat rôle personnalisé (20000 Skycoins)
# - Partage de rôle personnalisé (50 Skycoins)
# ============================================

import discord
from discord.ext import commands, tasks
from discord import app_commands

from config import (
    GUILD_ID,
    ROLE_VIP_ID,
    PRIX_VIP,
    PRIX_ROLE_PERSO,
    PRIX_PARTAGE_ROLE,
    FACTURE_MENSUELLE_ROLE,
    EMOJI_SKYCOIN, EMOJI_VIP
)
from utils.database import (
    obtenir_solde, modifier_solde,
    ajouter_vip, obtenir_vip_expires, supprimer_vip,
    sauvegarder_role_perso, obtenir_roles_perso,
    ajouter_membre_role_perso, supprimer_role_perso
)
from utils.embeds import embed_succes, embed_erreur, embed_info, formater_nombre


# ============================================
# 📝 MODAL PERSONNALISATION RÔLE
# ============================================

class ModalPersonnalisationRole(discord.ui.Modal):
    """
    Formulaire pour personnaliser son rôle custom.
    """
    
    def __init__(self):
        super().__init__(title="🎨 Personnalise ton Rôle")
    
    nom_role = discord.ui.TextInput(
        label="Nom du rôle",
        placeholder="Ex: ★ VIP Sky ★",
        required=True,
        max_length=50
    )
    
    couleur = discord.ui.TextInput(
        label="Couleur (code hex sans #)",
        placeholder="Ex: FF5733 ou E91E63",
        required=True,
        max_length=6,
        min_length=6
    )
    
    emoji = discord.ui.TextInput(
        label="Emoji pour le rôle (optionnel)",
        placeholder="Ex: ⭐ ou 🎮",
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        Crée le rôle personnalisé quand le formulaire est soumis.
        """
        user = interaction.user
        guild = interaction.guild
        
        # Vérifie que l'utilisateur a assez d'argent
        solde = obtenir_solde(user.id)
        if solde < PRIX_ROLE_PERSO:
            embed = embed_erreur(
                "Solde insuffisant",
                f"Il te faut **{formater_nombre(PRIX_ROLE_PERSO)}** {EMOJI_SKYCOIN} Skycoins.\n"
                f"Tu n'as que **{formater_nombre(solde)}** Skycoins."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie la couleur
        try:
            couleur_int = int(self.couleur.value, 16)
        except ValueError:
            embed = embed_erreur(
                "Couleur invalide",
                "La couleur doit être un code hexadécimal valide.\n"
                "Exemple : `FF5733` (orange) ou `3498DB` (bleu)"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Prépare le nom du rôle (avec emoji si fourni)
        nom_final = self.nom_role.value
        if self.emoji.value:
            nom_final = f"{self.emoji.value} {nom_final}"
        
        try:
            # Crée le rôle
            # On le place juste en dessous du rôle le plus haut du bot
            bot_member = guild.get_member(interaction.client.user.id)
            position = bot_member.top_role.position - 1
            
            role = await guild.create_role(
                name=nom_final,
                colour=discord.Colour(couleur_int),
                reason=f"Rôle personnalisé acheté par {user.name}"
            )
            
            # Déplace le rôle à la bonne position
            await role.edit(position=max(1, position))
            
            # Attribue le rôle à l'utilisateur
            await user.add_roles(role)
            
            # Retire l'argent
            modifier_solde(user.id, -PRIX_ROLE_PERSO)
            
            # Sauvegarde dans la base de données
            sauvegarder_role_perso(user.id, role.id, nom_final, couleur_int)
            
            embed = embed_succes(
                "Rôle créé !",
                f"Ton rôle {role.mention} a été créé avec succès !\n\n"
                f"💰 **-{formater_nombre(PRIX_ROLE_PERSO)}** Skycoins\n\n"
                f"⚠️ **Attention** : Tu devras payer **{formater_nombre(FACTURE_MENSUELLE_ROLE)}** Skycoins "
                f"par mois pour le garder !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = embed_erreur(
                "Erreur de permissions",
                "Je n'ai pas la permission de créer des rôles !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = embed_erreur(
                "Erreur",
                f"Une erreur s'est produite : {e}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================
# 🔘 VUE DE LA BOUTIQUE
# ============================================

class VueBoutique(discord.ui.View):
    """
    Vue avec les boutons de la boutique.
    """
    
    def __init__(self):
        super().__init__(timeout=180)  # 3 minutes
    
    @discord.ui.button(
        label=f"👑 Rôle VIP ({formater_nombre(PRIX_VIP)} SC)",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def acheter_vip(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        """Achète le rôle VIP."""
        user = interaction.user
        guild = interaction.guild
        
        # Vérifie le solde
        solde = obtenir_solde(user.id)
        if solde < PRIX_VIP:
            embed = embed_erreur(
                "Solde insuffisant",
                f"Il te faut **{formater_nombre(PRIX_VIP)}** {EMOJI_SKYCOIN} Skycoins.\n"
                f"Tu n'as que **{formater_nombre(solde)}** Skycoins."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Récupère le rôle VIP
        role_vip = guild.get_role(ROLE_VIP_ID)
        if not role_vip:
            embed = embed_erreur(
                "Erreur de configuration",
                "Le rôle VIP n'a pas été trouvé !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie si l'utilisateur a déjà le rôle
        if role_vip in user.roles:
            embed = embed_info(
                "Déjà VIP !",
                "Tu possèdes déjà le rôle VIP. 👑"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            # Attribue le rôle et retire l'argent
            await user.add_roles(role_vip)
            modifier_solde(user.id, -PRIX_VIP)
            ajouter_vip(user.id, 30)  # 30 jours
            
            embed = embed_succes(
                "Achat réussi !",
                f"Tu as acheté le rôle {role_vip.mention} pour **1 mois** !\n\n"
                f"💰 **-{formater_nombre(PRIX_VIP)}** Skycoins\n\n"
                f"Profite bien de tes avantages VIP ! 👑"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = embed_erreur(
                "Erreur de permissions",
                "Je n'ai pas la permission d'attribuer ce rôle !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        label=f"🎨 Rôle Personnalisé ({formater_nombre(PRIX_ROLE_PERSO)} SC)",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def acheter_role_perso(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        """Ouvre le formulaire de personnalisation."""
        # Vérifie si l'utilisateur a déjà un rôle perso
        roles_perso = obtenir_roles_perso()
        if str(interaction.user.id) in roles_perso:
            embed = embed_info(
                "Tu as déjà un rôle !",
                "Tu possèdes déjà un rôle personnalisé.\n"
                "Utilise `/partager-role` pour le partager avec quelqu'un !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie le solde avant d'ouvrir le modal
        solde = obtenir_solde(interaction.user.id)
        if solde < PRIX_ROLE_PERSO:
            embed = embed_erreur(
                "Solde insuffisant",
                f"Il te faut **{formater_nombre(PRIX_ROLE_PERSO)}** {EMOJI_SKYCOIN} Skycoins.\n"
                f"Tu n'as que **{formater_nombre(solde)}** Skycoins."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.send_modal(ModalPersonnalisationRole())


class Shop(commands.Cog):
    """
    Cog pour la boutique du serveur.
    """
    
    def __init__(self, bot):
        self.bot = bot
        # Démarre la tâche de vérification des VIP expirés
        self.verifier_vip_expires.start()
        self.facturer_roles_perso.start()
    
    def cog_unload(self):
        """Appelé quand le cog est déchargé."""
        self.verifier_vip_expires.cancel()
        self.facturer_roles_perso.cancel()
    
    # ================================
    # 🛒 COMMANDE /shop
    # ================================
    @app_commands.command(
        name="shop",
        description="Ouvre la boutique du serveur !"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def shop(self, interaction: discord.Interaction):
        """
        Affiche la boutique avec tous les articles disponibles.
        """
        solde = obtenir_solde(interaction.user.id)
        
        embed = discord.Embed(
            title="🛒  BOUTIQUE DU SERVEUR",
            description=(
                f"Bienvenue dans la boutique officielle !\n"
                f"Dépense tes **Skycoins** durement gagnés ici.\n\n"
                f"💰 **TON SOLDE ACTUEL**\n"
                f"# `{formater_nombre(solde)}` {EMOJI_SKYCOIN}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0xFFD700  # Or Plus Brillant
        )
        
        # --- IMAGE D'ILLUSTRATION (Thumbnail) ---
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        else:
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        # --- ARTICLE 1 : VIP ---
        embed.add_field(
            name=f"{EMOJI_VIP}  Statut VIP (1 Mois)",
            value=(
                f"> **Prix :** `{formater_nombre(PRIX_VIP)}` {EMOJI_SKYCOIN}\n"
                "🔹 Accès aux salons privés\n"
                "🔹 Grade exclusif en haut de la liste\n"
                "🔹 Badges et avantages spéciaux\n"
                "⏳ *Expire automatiquement après 30 jours*"
            ),
            inline=False
        )
        
        # --- SEPARATEUR ---
        embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
        
        # --- ARTICLE 2 : ROLE PERSO ---
        embed.add_field(
            name=f"🎨  Création de Rôle Personnalisé",
            value=(
                f"> **Prix :** `{formater_nombre(PRIX_ROLE_PERSO)}` {EMOJI_SKYCOIN}\n"
                "🔸 Choisis ton **Nom** unique\n"
                "🔸 Choisis ta **Couleur** préférée\n"
                "🔸 Ajoute un **Emoji** personnalisé\n"
                f"💸 *Coût d'entretien : {formater_nombre(FACTURE_MENSUELLE_ROLE)} {EMOJI_SKYCOIN}/mois*"
            ),
            inline=False
        )
        
        embed.set_footer(text="🛒 Clique sur les boutons ci-dessous pour commander !")
        
        await interaction.response.send_message(
            embed=embed,
            view=VueBoutique(),
            ephemeral=True
        )
    
    # ================================
    # 🤝 COMMANDE /partager-role
    # ================================
    @app_commands.command(
        name="partager-role",
        description="Partage ton rôle personnalisé avec quelqu'un"
    )
    @app_commands.describe(membre="La personne avec qui partager ton rôle")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def partager_role(
        self,
        interaction: discord.Interaction,
        membre: discord.Member
    ):
        """
        Partage son rôle personnalisé avec un autre membre.
        Coûte 50 Skycoins.
        """
        user = interaction.user
        
        # Vérifie que l'utilisateur a un rôle perso
        roles_perso = obtenir_roles_perso()
        if str(user.id) not in roles_perso:
            embed = embed_erreur(
                "Pas de rôle personnalisé",
                "Tu n'as pas de rôle personnalisé à partager !\n"
                "Achète-en un dans `/shop`."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie qu'on ne partage pas avec soi-même
        if membre.id == user.id:
            embed = embed_erreur(
                "Erreur",
                "Tu ne peux pas partager ton rôle avec toi-même ! 😅"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie le solde
        solde = obtenir_solde(user.id)
        if solde < PRIX_PARTAGE_ROLE:
            embed = embed_erreur(
                "Solde insuffisant",
                f"Il te faut **{PRIX_PARTAGE_ROLE}** {EMOJI_SKYCOIN} Skycoins."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Récupère le rôle
        role_data = roles_perso[str(user.id)]
        role = interaction.guild.get_role(role_data["role_id"])
        
        if not role:
            embed = embed_erreur(
                "Rôle introuvable",
                "Ton rôle semble avoir été supprimé !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Vérifie si le membre a déjà le rôle
        if role in membre.roles:
            embed = embed_info(
                "Déjà partagé",
                f"{membre.mention} a déjà ton rôle !"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            # Attribue le rôle et retire l'argent
            await membre.add_roles(role)
            modifier_solde(user.id, -PRIX_PARTAGE_ROLE)
            ajouter_membre_role_perso(user.id, membre.id)
            
            embed = embed_succes(
                "Rôle partagé !",
                f"Tu as partagé ton rôle {role.mention} avec {membre.mention} !\n\n"
                f"💰 **-{PRIX_PARTAGE_ROLE}** Skycoins"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = embed_erreur(
                "Erreur de permissions",
                "Je n'ai pas la permission d'attribuer ce rôle !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ================================
    # ⏰ TÂCHE : VÉRIFIER LES VIP EXPIRÉS
    # ================================
    @tasks.loop(hours=1)
    async def verifier_vip_expires(self):
        """
        Vérifie toutes les heures si des VIP ont expiré.
        Retire automatiquement le rôle si c'est le cas.
        """
        expires = obtenir_vip_expires()
        
        if not expires:
            return
        
        # Récupère le serveur
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        
        role_vip = guild.get_role(ROLE_VIP_ID)
        if not role_vip:
            return
        
        for user_id in expires:
            try:
                membre = guild.get_member(user_id)
                if membre and role_vip in membre.roles:
                    await membre.remove_roles(role_vip, reason="VIP expiré")
                    
                    # Envoie un DM à l'utilisateur
                    try:
                        embed = embed_info(
                            "VIP Expiré",
                            "Ton statut VIP a expiré ! 👑\n"
                            "Tu peux le racheter dans `/shop`."
                        )
                        await membre.send(embed=embed)
                    except:
                        pass  # Ignore si on ne peut pas envoyer de DM
                
                # Supprime de la base de données
                supprimer_vip(user_id)
                
            except Exception as e:
                print(f"Erreur lors du retrait VIP pour {user_id}: {e}")
    
    @verifier_vip_expires.before_loop
    async def avant_verif_vip(self):
        """Attend que le bot soit prêt avant de démarrer la tâche."""
        await self.bot.wait_until_ready()
    
    # ================================
    # ⏰ TÂCHE : FACTURER LES RÔLES PERSO
    # ================================
    @tasks.loop(hours=24)
    async def facturer_roles_perso(self):
        """
        Vérifie tous les jours si des factures de rôles perso sont dues.
        """
        import time
        roles_perso = obtenir_roles_perso()
        
        if not roles_perso:
            return
        
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        
        maintenant = time.time()
        un_mois = 30 * 24 * 60 * 60  # 30 jours en secondes
        
        for user_id, data in list(roles_perso.items()):
            derniere_facture = data.get("derniere_facture", 0)
            
            # Vérifie si un mois s'est écoulé
            if maintenant - derniere_facture < un_mois:
                continue
            
            user_id_int = int(user_id)
            solde = obtenir_solde(user_id_int)
            
            if solde >= FACTURE_MENSUELLE_ROLE:
                # L'utilisateur peut payer
                modifier_solde(user_id_int, -FACTURE_MENSUELLE_ROLE)
                
                # Met à jour la date de facturation
                roles_perso[user_id]["derniere_facture"] = maintenant
                from utils.database import sauvegarder_json
                sauvegarder_json("custom_roles.json", roles_perso)
                
                # Notifie l'utilisateur
                try:
                    membre = guild.get_member(user_id_int)
                    if membre:
                        embed = embed_info(
                            "Facture Rôle Perso",
                            f"Ta facture mensuelle de **{formater_nombre(FACTURE_MENSUELLE_ROLE)}** Skycoins "
                            "a été prélevée pour ton rôle personnalisé !"
                        )
                        await membre.send(embed=embed)
                except:
                    pass
            else:
                # L'utilisateur ne peut pas payer, on supprime le rôle
                role_id = data.get("role_id")
                if role_id:
                    role = guild.get_role(role_id)
                    if role:
                        try:
                            await role.delete(reason="Facture mensuelle non payée")
                        except:
                            pass
                
                # Supprime de la base de données
                supprimer_role_perso(user_id_int)
                
                # Notifie l'utilisateur
                try:
                    membre = guild.get_member(user_id_int)
                    if membre:
                        embed = embed_erreur(
                            "Rôle Supprimé",
                            f"Tu n'avais pas assez de Skycoins pour payer la facture "
                            f"de **{formater_nombre(FACTURE_MENSUELLE_ROLE)}** Skycoins.\n"
                            "Ton rôle personnalisé a été supprimé. 😢"
                        )
                        await membre.send(embed=embed)
                except:
                    pass
    
    @facturer_roles_perso.before_loop
    async def avant_facturation(self):
        """Attend que le bot soit prêt avant de démarrer la tâche."""
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Shop(bot))
