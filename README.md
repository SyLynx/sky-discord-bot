# 🤖 Sky's Discord Bot (Advanced Economy & Games)

A complete, modular, and professional Discord bot built with **Python** and **discord.py**. Specifically designed for server engagement with a complex economy system, a custom shop, and interactive mini-games.

---

## 🎯 The Story

This bot was custom-built for a customer to meet a specific set of high-end community requirements:

- **Automated Onboarding**: A rules system with a one-click button for role assignment.
- **Smart Forms**: Integrated modal windows for filming applications and staff recruitment.
- **Advanced Economy**: Multi-tier rewards (daily, weekly, monthly) and a persistent currency database.
- **Self-Service Shop**:
  - **VIP Subscriptions**: 30-day roles with automatic cleanup.
  - **Custom Role Engine**: An automated system for users to buy, design, and maintain their own unique server roles (including monthly "taxes" and sharing options).
- **Game Center**: Full-featured interactive games (Snake, Hangman, Tic-Tac-Toe) with rewards.

---

## 📋 Features

### 💰 Economy System

- `/day` - Claims daily rewards (500 Skycoins).
- `/week` - Claims weekly rewards (1000 Skycoins).
- `/month` - Claims monthly rewards (2000 Skycoins).
- `/solde` - Checks your balance or another member's balance.
- `/classement` - View the Top 10 richest players on the server.

### 📜 Automated Rules System

- `/reglement` - Sends a professional rules embed with an **Accept Button**.
- Automatic role assignment upon acceptance.
- Detailed 8-point community guidelines.

### 🛒 Custom Shop

- `/shop` - Interactive shop menu featuring:
  - **👑 VIP Status**: Purchasable 30-day role with automatic expiration.
  - **🎨 Custom Roles**: Create your own role (name, color, emoji).
- `/partager-role` - Share your custom role with friends for a small fee.
- **Monthly Invoicing**: Automated monthly fees for custom role maintenance.

### 🎮 Interactive Mini-Games

- `/morpion` - Tic-Tac-Toe with buttons (Play vs. Friends or Random).
- `/pendu` - Hangman with a full interactive keyboard UI.
- `/snake` - Snake game on an emoji grid with directional controls and rewards.

### 📢 Recruitment & Applications

- `/annonce-tournage` - Integrated modal form for film/video applications.
- `/recrutement` - Direct access to community recruitment forms (Moderation/Animation).

---

## 🚀 Installation

### 1. Prerequisites

- **Python 3.10** or higher.
- `pip` (Python package manager).

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

1. Rename or open the `.env` file.
2. Replace `(A FILL)` with your **Discord Bot Token**.
3. Set the `GUILD_ID` to your server's ID.
4. Update role IDs and prices in `config.py`.

### 4. Running the Bot

```bash
python main.py
```

---

## ⚙️ Advanced Configuration

All core settings are centralized in `config.py`:

| Parameter                  | Description                      | Default Value |
| -------------------------- | -------------------------------- | ------------- |
| `RECOMPENSE_JOUR`        | Reward for `/day`              | 500 SC        |
| `PRIX_VIP`               | VIP Role price                   | 5000 SC       |
| `PRIX_ROLE_PERSO`        | Custom Role creation price       | 20000 SC      |
| `FACTURE_MENSUELLE_ROLE` | Maintenance fee for custom roles | 1000 SC       |

### Recruitment Links

Customize your Google Forms links in `config.py`:

```python
LIEN_FORM_MODERATION = "https://forms.google.com/..."
LIEN_FORM_ANIMATION = "https://forms.google.com/..."
```

---

## 📁 Project Structure

```text
.
├── main.py              # Entry point
├── bot.py               # Main Bot class & logic
├── config.py            # Central configuration
├── .env                 # Secret environment variables
├── cogs/                # Modular features
│   ├── economie.py      # Economy logic
│   ├── reglement.py     # Rules & Role assignment
│   ├── annonces.py      # Apps & Recruitment
│   ├── shop.py          # Shop & Subscription system
│   └── jeux/            # Mini-games subdirectory
├── utils/               # Helpers & Tools
│   ├── database.py      # Persistent JSON storage
│   ├── embeds.py        # Styled Discord UI tools
│   └── checks.py        # Permission handlers
└── data/                # Database folder (Auto-generated)
```

---

## 🎨 Visual Customization

### Theming

Modify hex colors in `config.py` to match your server's branding:

```python
COULEUR_SUCCES = 0x2ECC71
COULEUR_ECONOMIE = 0xF1C40F
```

---

## 📜 Credits

Developed with ❤️ for **Sky**.
*Feel free to use and modify for your own server!*
