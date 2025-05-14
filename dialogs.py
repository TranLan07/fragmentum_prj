from config import *
from dialog_parser import dialogs_data, DialogPart

class DialogBox:
    def __init__(self):
        self.dBox = pygame.image.load('assets/overlay/dialogs/dbox.png')
        resolution = screen_re()
        self.position = [50, resolution[1] - 250]  # Position en bas de l'écran
        self.speaker = ""
        self.texts = []  # Liste des segments de dialogue
        self.txt_index = 0
        self.letter_index = 0
        self.font = pygame.font.Font('assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf', 24)
        self.reading = False
        self.press = False
        self.line_height = 30
        self.max_width = 700
        self.speaker_font = pygame.font.Font('assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf', 26)
        self.text_color = (255, 255, 255)
        self.speaker_color = (255, 235, 0)

    def render(self, screen):
        if self.reading:
            # Afficher la boîte de dialogue
            screen.blit(self.dBox, (self.position[0], self.position[1]))

            # Afficher le nom du personnage qui parle
            if self.speaker:
                speaker_text = self.speaker_font.render(self.speaker, True, self.speaker_color)
                screen.blit(speaker_text, (self.position[0] + 70, self.position[1] + 40))

            # Gérer l'animation lettre par lettre
            self.letter_index += 1

            # Limiter l'index de lettre à la longueur du texte actuel
            if self.letter_index > len(self.texts[self.txt_index]):
                self.letter_index = len(self.texts[self.txt_index])

            # Obtenir le texte à afficher jusqu'à l'index de lettre actuel
            current_text = self.texts[self.txt_index][:self.letter_index]

            # Remplacer les \n par de vrais retours à la ligne
            lines = current_text.split('\\n')

            # Afficher chaque ligne
            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, self.text_color)
                screen.blit(text_surface, (self.position[0] + 70, self.position[1] + 80 + i * self.line_height))

    def next(self):
        if self.reading:
            # Si on n'a pas fini d'afficher le texte courant, l'afficher complètement
            if self.letter_index < len(self.texts[self.txt_index]):
                self.letter_index = len(self.texts[self.txt_index])
            else:
                # Sinon, passer au texte suivant
                self.txt_index += 1
                self.letter_index = 0

                # Si on a affiché tous les textes, fermer la boîte de dialogue
                if self.txt_index >= len(self.texts):
                    self.reading = False

    def execute(self, data_txt):
        self.reading = True
        self.txt_index = 0
        self.letter_index = 0
        self.speaker = data_txt.caster

        # Diviser le texte en segments (séparés par /n)
        self.texts = data_txt.dialogs.split('/n')


class Discussion:
    def __init__(self, dBox, dialog_parts):
        self.dBox = dBox
        self.dialog_parts = dialog_parts
        self.current_index = 0

    def read(self):
        if self.current_index < len(self.dialog_parts):
            current_part = self.dialog_parts[self.current_index]
            self.dBox.execute(current_part)
            self.current_index += 1
            return True
        return False

    def read_next(self):
        if self.dBox.reading:
            self.dBox.next()
        else:
            return self.read()