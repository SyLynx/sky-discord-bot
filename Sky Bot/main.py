# ============================================
# 🚀 POINT D'ENTRÉE DU BOT
# ============================================
# C'est ce fichier que tu lances pour démarrer le bot !
# Commande : python main.py
# ============================================

from bot import SkyBot
from config import TOKEN

# Vérifie que le token est configuré
if not TOKEN or TOKEN == "ton_token_ici":
    print("❌ ERREUR : Tu dois configurer ton token dans le fichier .env !")
    print("📝 Ouvre le fichier .env et remplace 'ton_token_ici' par ton vrai token.")
    exit(1)

# Crée et lance le bot
if __name__ == "__main__":
    bot = SkyBot()
    bot.run(TOKEN)
