# ============================================
# 🛡️ PROTECTION ANTI-PING POUR SKY
# ============================================
# Ce module supprime automatiquement les messages
# qui mentionnent Sky.
#
# Important :
# Discord envoie souvent la notification AVANT que
# le bot puisse supprimer le message.
# Le bot ne peut donc pas empêcher la notif à 100%,
# mais il peut supprimer le message très vite.
# ============================================

import discord
from discord.ext import commands


# ============================================
# ⚙️ CONFIGURATION
# ============================================

# ID Discord de Sky
SKY_ID = 1340405386318053388

# Si True, les admins/modérateurs ne sont pas supprimés
IGNORER_MODERATEURS = True

# Si tu veux un salon de logs, mets son ID ici.
# Exemple : SALON_LOG_ID = 123456789012345678
# Laisse None pour désactiver les logs.
SALON_LOG_ID = None


# ============================================
# 🧠 COG PRINCIPAL
# ============================================

class PingGuard(commands.Cog):
    """
    Cog qui surveille les messages et supprime ceux
    qui mentionnent Sky.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ============================================
    # 📩 MESSAGE CRÉÉ
    # ============================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self._traiter_message(message, evenement="création")

    # ============================================
    # ✏️ MESSAGE MODIFIÉ
    # ============================================

    @commands.Cog.listener()
    async def on_message_edit(self, ancien_message: discord.Message, nouveau_message: discord.Message):
        await self._traiter_message(nouveau_message, evenement="édition")

    # ============================================
    # 🔍 TRAITEMENT PRINCIPAL
    # ============================================

    async def _traiter_message(self, message: discord.Message, evenement: str):
        """
        Vérifie si un message ping Sky.
        Si oui, le bot tente de le supprimer.
        """

        try:
            # Ignore les messages privés
            if message.guild is None:
                return

            # Ignore les messages du bot lui-même
            if self.bot.user and message.author.id == self.bot.user.id:
                return

            # Sky peut évidemment se mentionner elle-même
            if message.author.id == SKY_ID:
                return

            # Vérifie si Sky est mentionnée directement
            sky_mentionnee = any(utilisateur.id == SKY_ID for utilisateur in message.mentions)

            # Fallback robuste au cas où Discord ne remplit pas bien message.mentions
            # Exemples possibles : <@134...> ou <@!134...>
            contenu = message.content or ""
            sky_mentionnee_texte = (
                f"<@{SKY_ID}>" in contenu
                or f"<@!{SKY_ID}>" in contenu
            )

            if not sky_mentionnee and not sky_mentionnee_texte:
                return

            # Option : ne pas supprimer les messages des modos/admins
            if IGNORER_MODERATEURS:
                est_modo = await self._auteur_est_moderateur(message)
                if est_modo:
                    return

            # Vérifie que le bot a le droit de supprimer
            membre_bot = message.guild.me

            if membre_bot is None:
                return

            permissions_bot = message.channel.permissions_for(membre_bot)

            if not permissions_bot.manage_messages:
                print(
                    f"⚠️ PingGuard : permission 'Gérer les messages' manquante "
                    f"dans le salon #{message.channel}."
                )
                return

            # Supprime le message
            await message.delete()

            print(
                f"🛡️ PingGuard : message supprimé | "
                f"Auteur: {message.author} ({message.author.id}) | "
                f"Salon: #{message.channel} | "
                f"Événement: {evenement}"
            )

            await self._journaliser_suppression(message, evenement)

        except discord.NotFound:
            # Le message a déjà été supprimé
            return

        except discord.Forbidden:
            print("❌ PingGuard : permission refusée pour supprimer le message.")

        except discord.HTTPException as erreur:
            print(f"❌ PingGuard : erreur Discord HTTP : {erreur}")

        except Exception as erreur:
            print(f"❌ PingGuard : erreur inattendue : {erreur}")

    # ============================================
    # 👮 VÉRIFICATION MODÉRATEUR / ADMIN
    # ============================================

    async def _auteur_est_moderateur(self, message: discord.Message) -> bool:
        """
        Retourne True si l'auteur est propriétaire, admin,
        ou possède des permissions de modération dans le salon.
        """

        if message.guild.owner_id == message.author.id:
            return True

        membre = message.guild.get_member(message.author.id)

        if membre is None:
            try:
                membre = await message.guild.fetch_member(message.author.id)
            except discord.HTTPException:
                return False

        permissions_salon = message.channel.permissions_for(membre)

        return (
            membre.guild_permissions.administrator
            or permissions_salon.manage_messages
            or permissions_salon.moderate_members
        )

    # ============================================
    # 📝 LOGS OPTIONNELS
    # ============================================

    async def _journaliser_suppression(self, message: discord.Message, evenement: str):
        """
        Envoie un log dans un salon dédié si SALON_LOG_ID est configuré.
        """

        if SALON_LOG_ID is None:
            return

        salon = self.bot.get_channel(SALON_LOG_ID)

        if salon is None:
            try:
                salon = await self.bot.fetch_channel(SALON_LOG_ID)
            except discord.HTTPException:
                return

        if not isinstance(salon, discord.TextChannel):
            return

        await salon.send(
            content=(
                "🛡️ **PingGuard**\n"
                f"Message supprimé.\n"
                f"Auteur : `{message.author}` / `{message.author.id}`\n"
                f"Salon : {message.channel.mention}\n"
                f"Événement : `{evenement}`"
            ),
            allowed_mentions=discord.AllowedMentions.none()
        )


# ============================================
# 🔌 CHARGEMENT DU COG
# ============================================

async def setup(bot: commands.Bot):
    await bot.add_cog(PingGuard(bot))
