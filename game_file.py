from temp_player import *
from maps import Maps
from dialogs import *
from save import save_game, load_game, save_exists
from music_menu import MusicMenu
from settings_menu import SettingsMenu
from config_reload import reload_config


pygame.font.init()
pygame.mixer.init()

# Charger la musique par défaut
default_music = get_music_files()[3]
pygame.mixer.music.load(default_music)
pygame.mixer.music.play(-1)

game_gravity = 80

class Game:
    def __init__(self):
        # Variables du monde
        self.run_time = 0
        self.gravity = game_gravity
        # Fenêtre
        self.screen = pygame.display.set_mode(screen_re())
        pygame.display.set_caption("PrjTransverse")

        # Créer le joueur et initialiser la carte
        self.player = Player(100, 100)
        self.player.set_screen(self.screen)
        self.maps_manager = Maps(self.screen, self.player)

        # Positionnement initial du joueur
        self.spawn = self.maps_manager.spawn
        if self.spawn:
            self.player.restart(self.spawn[0], self.spawn[1])

        # Créer les gestionnaires de musique et paramètres
        self.music_menu = MusicMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen)

        # Initialiser les notifications
        self.notifications = []
        self.font = pygame.font.Font(None, 24)
        self.save_key_pressed = False

        # Boîte de dialogue
        self.dBox = DialogBox()
        self.player.add_item('start_orb')

    def add_notification(self, text, color=(255, 255, 255), duration=2.0):
        """Ajouter une notification à l'écran"""
        surface = self.font.render(text, True, color)
        self.notifications.append({
            "surface": surface,
            "duration": duration,
            "creation_time": pygame.time.get_ticks() / 1000.0
        })

    def update_notifications(self):
        """Mettre à jour les notifications (supprimer celles qui ont expiré)"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.notifications = [n for n in self.notifications
                              if current_time - n["creation_time"] < n["duration"]]

    def draw_notifications(self):
        """Dessiner les notifications à l'écran"""
        screen_width, screen_height = self.screen.get_size()
        padding = 20

        y_offset = padding
        for notification in self.notifications:
            surface = notification["surface"]
            x = (screen_width - surface.get_width()) // 2
            self.screen.blit(surface, (x, y_offset))
            y_offset += surface.get_height() + 5

    def handle_input(self):
        keys_pressed = pygame.key.get_pressed()

        # Gestion des mouvements
        if keys_pressed[forward_key()]:
            if not self.dBox.reading:
                self.player.vector[0] += 0.5
        elif keys_pressed[backward_key()]:
            if not self.dBox.reading:
                self.player.vector[0] -= 0.5
        else:
            # Appliquer une friction plus douce
            self.player.vector[0] *= 0.9

        # Limiter la vitesse
        self.player.vector[0] = max(-6, min(6, self.player.vector[0]))

        # Saut
        if keys_pressed[jump_key()]:
            if self.dBox.reading:
                if not self.dBox.press:
                    self.dBox.next()
                self.dBox.press = True
            else:
                self.player.mvu()
        else:
            self.dBox.press = False

        if keys_pressed[double_jump_key()]:
            if not self.dBox.reading:
                self.player.double_jump()

        # Boost
        if keys_pressed[boost_key()]:
            self.player.run()
        else:
            self.player.norun()

        # Sauvegarde (touche S)
        if keys_pressed[Save_key()]:
            if not self.save_key_pressed:
                if save_game(self):
                    self.add_notification("Partie sauvegardée !", color=(0, 255, 0), duration=2.0)
                self.save_key_pressed = True
        else:
            self.save_key_pressed = False

        self.maps_manager.update(keys_pressed)
        self.player.handle_shooting_input(keys_pressed)

    def item_traitement(self):
        dialog_data = dialogs_data()

        if "parchemin" in self.player.items:
            self.player.items.remove("parchemin")
            if "parchemin" in dialog_data:
                Discussion(self.dBox, dialog_data["parchemin"]).read()

        elif "immortal_orb" in self.player.items:
            if "mort" in dialog_data:
                Discussion(self.dBox, dialog_data["mort"]).read()
            self.player.items.remove("immortal_orb")

        elif "start_orb" in self.player.items:
            if "start" in dialog_data:
                Discussion(self.dBox, dialog_data["start"]).read()
            self.player.items.remove("start_orb")

        elif "brizio_orb" in self.player.items:
            if "brizio" in dialog_data:
                Discussion(self.dBox, dialog_data["brizio"]).read()
            self.player.items.remove("brizio_orb")

        elif "aqua_orb" in self.player.items:
            if "aqua" in dialog_data:
                Discussion(self.dBox, dialog_data["aqua"]).read()
            self.player.items.remove("aqua_orb")

        elif "sky_orb" in self.player.items:
            if "sky" in dialog_data:
                Discussion(self.dBox, dialog_data["sky"]).read()
            self.player.items.remove("sky_orb")

        elif "magma_orb" in self.player.items:
            if "magma" in dialog_data:
                Discussion(self.dBox, dialog_data["magma"]).read()
            self.player.items.remove("magma_orb")

    def show_start_screen(self):
        # Image de fond
        background = pygame.image.load("assets/map/background/background.png")
        background = pygame.transform.scale(background, self.screen.get_size())

        # Polices rétro
        font_title = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 60)
        font_instr = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 30)
        font_menu = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 24)

        # Textes
        title_text = font_title.render("PRJ TRANSVERSE", True, (0, 255, 180))
        start_text = font_instr.render("COMMENCER", True, (0, 255, 180))
        continue_text = font_instr.render("CONTINUER", True, (0, 255, 180))
        music_text = font_instr.render("MUSIQUE", True, (0, 255, 180))
        settings_text = font_instr.render("PARAMETRES", True, (0, 255, 180))

        # Vérifier si une sauvegarde existe
        has_save = save_exists()

        # Design des boutons
        button_width = 400
        button_height = 80
        button_x = (self.screen.get_width() - button_width) // 2

        # Ajuster les positions des boutons
        start_button_y = 380
        continue_button_y = 480 if has_save else None
        music_button_y = 580 if has_save else 480
        settings_button_y = 680 if has_save else 580

        start_button = pygame.Rect(button_x, start_button_y, button_width, button_height)
        continue_button = pygame.Rect(button_x, continue_button_y, button_width, button_height) if has_save else None
        music_button = pygame.Rect(button_x, music_button_y, button_width, button_height)
        settings_button = pygame.Rect(button_x, settings_button_y, button_width, button_height)

        # Calcul du nombre de boutons
        button_count = 4 if has_save else 3
        selected_button = 0

        # Boucle du menu principal
        menu_active = True
        clock = pygame.time.Clock()

        while menu_active:
            # Dessiner les éléments
            self.screen.blit(background, (0, 0))

            # Titre
            self.screen.blit(title_text, ((self.screen.get_width() - title_text.get_width()) // 2, 150))

            # Bouton Commencer
            border_color = (255, 255, 100) if selected_button == 0 else (0, 255, 180)
            pygame.draw.rect(self.screen, border_color, start_button)
            pygame.draw.rect(self.screen, (10, 10, 10), start_button.inflate(-6, -6))
            start_x = button_x + (button_width - start_text.get_width()) // 2
            start_y = start_button_y + (button_height - start_text.get_height()) // 2
            self.screen.blit(start_text, (start_x, start_y))

            # Bouton Continuer (si une sauvegarde existe)
            if has_save:
                border_color = (255, 255, 100) if selected_button == 1 else (0, 255, 180)
                pygame.draw.rect(self.screen, border_color, continue_button)
                pygame.draw.rect(self.screen, (10, 10, 10), continue_button.inflate(-6, -6))
                continue_x = button_x + (button_width - continue_text.get_width()) // 2
                continue_y = continue_button_y + (button_height - continue_text.get_height()) // 2
                self.screen.blit(continue_text, (continue_x, continue_y))

            # Bouton Musique
            music_button_index = 2 if has_save else 1
            border_color = (255, 255, 100) if selected_button == music_button_index else (0, 255, 180)
            pygame.draw.rect(self.screen, border_color, music_button)
            pygame.draw.rect(self.screen, (10, 10, 10), music_button.inflate(-6, -6))
            music_x = button_x + (button_width - music_text.get_width()) // 2
            music_y = music_button_y + (button_height - music_text.get_height()) // 2
            self.screen.blit(music_text, (music_x, music_y))

            # Bouton Paramètres
            settings_button_index = 3 if has_save else 2
            border_color = (255, 255, 100) if selected_button == settings_button_index else (0, 255, 180)
            pygame.draw.rect(self.screen, border_color, settings_button)
            pygame.draw.rect(self.screen, (10, 10, 10), settings_button.inflate(-6, -6))
            settings_x = button_x + (button_width - settings_text.get_width()) // 2
            settings_y = settings_button_y + (button_height - settings_text.get_height()) // 2
            self.screen.blit(settings_text, (settings_x, settings_y))

            pygame.display.flip()

            # Traiter les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_button = (selected_button - 1) % button_count
                    elif event.key == pygame.K_DOWN:
                        selected_button = (selected_button + 1) % button_count
                    elif event.key == pygame.K_RETURN:
                        if selected_button == 0:  # Commencer
                            menu_active = False
                        elif selected_button == 1 and has_save:  # Continuer
                            if load_game(self):
                                menu_active = False
                        elif selected_button == (2 if has_save else 1):  # Musique
                            self.music_menu.show()
                        elif selected_button == (3 if has_save else 2):  # Paramètres
                            # Afficher le menu des paramètres
                            new_resolution, new_fps = self.settings_menu.show()

                            # Si la résolution ou les FPS ont changé, actualiser les paramètres
                            from config import screen_re, fps_re
                            if new_resolution != screen_re() or new_fps != fps_re():
                                # Recharger la configuration
                                reload_config()
                                from config import screen_re, fps_re

                                # Réinitialiser l'écran si nécessaire
                                if new_resolution != screen_re():
                                    self.screen = pygame.display.set_mode(screen_re())
                                    background = pygame.transform.scale(background, self.screen.get_size())

                                # Recalculer les positions des boutons
                                button_x = (screen_re()[0] - button_width) // 2
                                start_button = pygame.Rect(button_x, start_button_y, button_width, button_height)
                                if has_save:
                                    continue_button = pygame.Rect(button_x, continue_button_y, button_width,
                                                                  button_height)
                                music_button = pygame.Rect(button_x, music_button_y, button_width, button_height)
                                settings_button = pygame.Rect(button_x, settings_button_y, button_width, button_height)

            clock.tick(30)  # Limiter à 30 FPS pour le menu

        return True

    def update(self):
        self.gravity = game_gravity
        # Mise à jour des collisions et des éléments de jeu
        self.maps_manager.check_item_collisions()
        self.maps_manager.collisions_update()
        self.maps_manager.way_collisions()

        # État des touches pour les stèles
        keys_pressed = pygame.key.get_pressed()
        self.maps_manager.update(keys_pressed)

        self.player.player_update()
        self.update_notifications()

        # Mise à jour des projectiles
        from Projectiles import projectiles_update
        projectiles_update(
            self.maps_manager.get_walls(),
            self.maps_manager.getCurrentMap().entities,
            self.maps_manager.get_damages()
        )

        # Mise à jour des entités
        for mob in self.maps_manager.getCurrentMap().entities[:]:
            mob.update()

        self.item_traitement()

    def restart(self):
        if self.maps_manager.spawn:
            self.player.restart(self.maps_manager.spawn[0], self.maps_manager.spawn[1])
        self.run_time = 0

    def run(self):
        self.show_start_screen()
        # Boucle de jeu
        clock = pygame.time.Clock()
        run = True
        while run:
            # Input
            self.handle_input()

            # Update
            self.update()

            # Draw
            self.maps_manager.draw()
            self.draw_notifications()
            self.dBox.render(self.screen)
            pygame.display.flip()

            self.run_time += 1 / fps_re()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            clock.tick(fps_re())