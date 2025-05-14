import pygame
import os
from config import get_music_files


class MusicMenu:
    def __init__(self, screen):
        self.screen = screen
        self.music_list = get_music_files()

        # Chargement des polices
        self.font_title = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 40)
        self.font_menu = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 20)
        self.font_instr = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 16)

        # Couleurs
        self.border_color = (0, 255, 180)  # Vert phosphorescent
        self.bg_color = (10, 10, 10)  # Noir
        self.selected_color = (0, 150, 100)

        # Charger le fond d'écran
        self.background = pygame.image.load("assets/map/background/background.png")
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

    def show(self):
        """Affiche le menu de sélection de musique"""
        # Textes
        title_text = self.font_title.render("SÉLECTION DE MUSIQUE", True, self.border_color)

        # Instructions
        instr_text1 = self.font_instr.render("↑/↓: Changer de musique", True, self.border_color)
        instr_text2 = self.font_instr.render("ESPACE: Écouter la musique", True, self.border_color)
        instr_text3 = self.font_instr.render("ENTRÉE: Confirmer", True, self.border_color)
        instr_text4 = self.font_instr.render("ÉCHAP: Retour", True, self.border_color)

        # Dimensions et positions
        menu_width = 800
        menu_height = 500
        menu_x = (self.screen.get_width() - menu_width) // 2
        menu_y = 150

        # Variables pour la sélection
        current_selection = 0
        if self.music_list:  # S'assurer qu'il y a au moins une musique
            current_music_file = self.music_list[current_selection]
        else:
            self.music_list = ["Aucune musique trouvée"]
            current_music_file = self.music_list[0]

        # Sauvegarder l'état de lecture actuel avant de le pauser
        music_was_playing = pygame.mixer.music.get_busy()
        pygame.mixer.music.pause()  # Pause de la musique actuelle

        # Boucle du menu
        music_menu_active = True
        clock = pygame.time.Clock()
        music_playing = False

        while music_menu_active:
            self.screen.blit(self.background, (0, 0))

            # Dessiner le cadre du menu
            pygame.draw.rect(self.screen, self.border_color, (menu_x, menu_y, menu_width, menu_height))
            pygame.draw.rect(self.screen, self.bg_color, (menu_x + 4, menu_y + 4, menu_width - 8, menu_height - 8))

            # Titre
            self.screen.blit(title_text, ((self.screen.get_width() - title_text.get_width()) // 2, menu_y + 20))

            # Instructions
            self.screen.blit(instr_text1, (menu_x + 20, menu_y + menu_height - 100))
            self.screen.blit(instr_text2, (menu_x + 20, menu_y + menu_height - 75))
            self.screen.blit(instr_text3, (menu_x + 20, menu_y + menu_height - 50))
            self.screen.blit(instr_text4, (menu_x + 20, menu_y + menu_height - 25))

            # Afficher les choix de musique (max 5 visibles à la fois)
            visible_start = max(0, current_selection - 2)
            visible_end = min(len(self.music_list), visible_start + 5)

            for i in range(visible_start, visible_end):
                # Obtenir juste le nom du fichier sans le chemin complet
                music_name = os.path.basename(self.music_list[i])
                # Limiter la longueur du nom affiché
                if len(music_name) > 30:
                    music_name = music_name[:27] + "..."

                text_color = self.border_color
                if i == current_selection:
                    # Dessiner un rectangle de sélection
                    select_rect = pygame.Rect(menu_x + 40, menu_y + 100 + (i - visible_start) * 50, menu_width - 80, 40)
                    pygame.draw.rect(self.screen, self.selected_color, select_rect)
                    text_color = (255, 255, 255)  # Texte blanc pour l'élément sélectionné

                text = self.font_menu.render(music_name, True, text_color)
                self.screen.blit(text, (menu_x + 50, menu_y + 110 + (i - visible_start) * 50))

            pygame.display.flip()

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        music_menu_active = False
                    elif event.key == pygame.K_UP:
                        current_selection = (current_selection - 1) % len(self.music_list)
                        current_music_file = self.music_list[current_selection]
                        if music_playing:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(current_music_file)
                            pygame.mixer.music.play()
                    elif event.key == pygame.K_DOWN:
                        current_selection = (current_selection + 1) % len(self.music_list)
                        current_music_file = self.music_list[current_selection]
                        if music_playing:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(current_music_file)
                            pygame.mixer.music.play()
                    elif event.key == pygame.K_SPACE:
                        # Écouter la sélection actuelle
                        if music_playing:
                            pygame.mixer.music.stop()
                            music_playing = False
                        else:
                            try:
                                pygame.mixer.music.load(current_music_file)
                                pygame.mixer.music.play()
                                music_playing = True
                            except pygame.error:
                                print(f"Impossible de lire le fichier: {current_music_file}")
                    elif event.key == pygame.K_RETURN:
                        # Confirmer la sélection et quitter
                        try:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(current_music_file)
                            pygame.mixer.music.play(-1)  # -1 pour jouer en boucle
                            music_menu_active = False
                        except pygame.error:
                            print(f"Impossible de charger le fichier: {current_music_file}")

            clock.tick(30)

        # Si on sort du menu sans avoir sélectionné une nouvelle musique
        # et que la musique était en train de jouer avant d'entrer dans le menu,
        # on reprend la lecture
        if music_playing:
            # Si on prévisualisait une musique quand on a quitté, on ne fait rien
            # car on a déjà chargé une nouvelle musique
            pass
        elif music_was_playing and event.key == pygame.K_ESCAPE:
            # Si la musique jouait avant et qu'on a appuyé sur ÉCHAP,
            # on reprend la lecture de la musique précédente
            pygame.mixer.music.unpause()