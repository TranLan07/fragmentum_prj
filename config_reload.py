"""
Module pour faciliter le rechargement des paramètres du jeu.
Permet d'actualiser les paramètres sans redémarrer le jeu.
"""

import importlib
import config

def reload_config():
    """
    Recharge le module de configuration pour actualiser les paramètres.
    Renvoie le module rechargé.
    """
    return importlib.reload(config)