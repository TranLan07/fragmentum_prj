import json
import os

# Définir le chemin du dossier de sauvegarde
SAVE_FOLDER = "saves"
SAVE_FILE = os.path.join(SAVE_FOLDER, "game_save.json")

# Points de vie par défaut pour le joueur
DEFAULT_HEALTH = 100


def ensure_save_folder_exists():
    """Vérifie que le dossier de sauvegarde existe, sinon le crée"""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)


def save_game(game):
    """Sauvegarde l'état du jeu dans un fichier JSON"""
    ensure_save_folder_exists()

    # Créer un dictionnaire avec les données à sauvegarder
    save_data = {
        "map": game.maps_manager.cmap,
        "position": game.player.position,
        "items": game.player.items,
        "health": getattr(game.player, "health", DEFAULT_HEALTH),
        "can_db_jump": game.player.can_db_jump
    }

    # Sauvegarder dans le fichier
    with open(SAVE_FILE, 'w') as file:
        json.dump(save_data, file, indent=4)

    return True


def load_game(game):
    """Charge l'état du jeu depuis un fichier JSON"""
    if not os.path.exists(SAVE_FILE):
        print("Aucune sauvegarde trouvée.")
        return False

    try:
        with open(SAVE_FILE, 'r') as file:
            save_data = json.load(file)

        # Charger la map
        if save_data["map"] in game.maps_manager.maps:
            # Changer de carte
            game.maps_manager.change_map(save_data["map"])

            # Écraser la position par celle sauvegardée
            game.player.position = save_data["position"]
            game.player.previous_position = save_data["position"].copy()
            game.player.rect.topleft = (int(game.player.position[0]), int(game.player.position[1]))

            # Réinitialiser les vecteurs et états
            game.player.vector = [0.0, 0.0]
            game.player.jumping = False
            game.player.colidlist = [0, 0, 0, 0]

            # Mise à jour des rectangles de collision
            game.player.update_colid_rect()

            # Charger les items
            game.player.items = save_data["items"]

            # Charger les points de vie si présents
            if not hasattr(game.player, "health"):
                game.player.health = save_data.get("health", DEFAULT_HEALTH)
            else:
                game.player.health = save_data.get("health", DEFAULT_HEALTH)

            # Charger la capacité de double saut
            game.player.can_db_jump = save_data.get("can_db_jump", False)

            return True
        else:
            print(f"Erreur: La carte {save_data['map']} n'existe pas.")
            return False

    except Exception as e:
        print(f"Erreur lors du chargement de la sauvegarde: {e}")
        return False


def delete_save():
    """Supprime le fichier de sauvegarde s'il existe"""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        print("Sauvegarde supprimée.")
        return True
    return False


def save_exists():
    """Vérifie si une sauvegarde existe"""
    return os.path.exists(SAVE_FILE)