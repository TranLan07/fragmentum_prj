import pygame
import os


class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen

        # Load fonts
        self.font_title = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 40)
        self.font_menu = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 20)
        self.font_instr = pygame.font.Font("assets/fonts/Press_Start_2P/PressStart2P-Regular.ttf", 16)

        # Colors
        self.border_color = (0, 255, 180)  # Phosphorescent green
        self.bg_color = (10, 10, 10)  # Black
        self.selected_color = (0, 150, 100)
        self.text_color = (255, 255, 255)

        # Load background
        self.background = pygame.image.load("assets/map/background/background.png")
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        # Load current configuration
        self.load_config()

        # Preset resolution options (width, height)
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1500, 900),
            (1920, 1080)
        ]

        # FPS options
        self.fps_options = [30, 60, 90, 120]

        # Configurable keys
        self.controls = {
            "Jump": " ",
            "Forward": "d",
            "Backward": "q",
            "Sneak": "s",
            "Boost": "shift"
        }

        # Key display name mappings
        self.key_display_names = {
            " ": "ESPACE",
            "shift": "SHIFT",
            "ctrl": "CTRL",
            "alt": "ALT"
        }

    def load_config(self):
        """Load current configurations from config.txt"""
        try:
            with open('config.txt', 'r') as f:
                config_lines = f.readlines()

            # Clean lines
            config_lines = [line.strip() for line in config_lines]

            # Extract resolution and FPS
            self.current_resolution = (800, 800)  # Default value
            self.current_fps = 60  # Default value

            for line in config_lines:
                if line.startswith('screen_resolution'):
                    parts = line.split('#')
                    if len(parts) >= 3:
                        try:
                            self.current_resolution = (int(parts[1]), int(parts[2]))
                        except ValueError:
                            pass
                elif line.startswith('fps'):
                    parts = line.split('#')
                    if len(parts) >= 2:
                        try:
                            self.current_fps = int(parts[1])
                        except ValueError:
                            pass

            # Load keys from config.py
            from config import Jump, Forward, Backward, Sneak, Boost
            self.controls = {
                "Jump": Jump,
                "Forward": Forward,
                "Backward": Backward,
                "Sneak": Sneak,
                "Boost": Boost
            }

        except Exception as e:
            # Default values
            self.current_resolution = (800, 800)
            self.current_fps = 60

    def save_config(self):
        """Save configurations to config.txt"""
        try:
            # Read existing file to keep unmodified lines
            with open('config.txt', 'r') as f:
                lines = f.readlines()

            # Prepare new content
            new_lines = []
            resolution_updated = False
            fps_updated = False

            for line in lines:
                if line.startswith('screen_resolution'):
                    new_lines.append(f"screen_resolution#{self.current_resolution[0]}#{self.current_resolution[1]}\n")
                    resolution_updated = True
                elif line.startswith('fps'):
                    new_lines.append(f"fps#{self.current_fps}\n")
                    fps_updated = True
                else:
                    new_lines.append(line)

            # Add missing lines if necessary
            if not resolution_updated:
                new_lines.append(f"screen_resolution#{self.current_resolution[0]}#{self.current_resolution[1]}\n")
            if not fps_updated:
                new_lines.append(f"fps#{self.current_fps}\n")

            # Write new content
            with open('config.txt', 'w') as f:
                f.writelines(new_lines)

            # Update keys in config.py
            self.save_keybinds()

            return True
        except Exception as e:
            return False

    def save_keybinds(self):
        """Save keys in config.py"""
        try:
            with open('config.py', 'r') as f:
                lines = f.readlines()

            # Find key lines and replace them
            new_lines = []
            in_keybinds_section = False

            for line in lines:
                if line.startswith('Jump = '):
                    new_lines.append(f"Jump = '{self.controls['Jump']}'\n")
                elif line.startswith('Forward = '):
                    new_lines.append(f"Forward = '{self.controls['Forward']}'\n")
                elif line.startswith('Backward = '):
                    new_lines.append(f"Backward = '{self.controls['Backward']}'\n")
                elif line.startswith('Sneak = '):
                    new_lines.append(f"Sneak = '{self.controls['Sneak']}'\n")
                elif line.startswith('Boost = '):
                    new_lines.append(f"Boost = '{self.controls['Boost']}'\n")
                else:
                    new_lines.append(line)

            with open('config.py', 'w') as f:
                f.writelines(new_lines)

            return True
        except Exception as e:
            return False

    def get_key_display_name(self, key):
        """Get display name of a key"""
        return self.key_display_names.get(key, key.upper())

    def show(self):
        """Display settings menu"""
        # Texts
        title_text = self.font_title.render("PARAMETRES", True, self.border_color)

        # Instructions
        instr_text1 = self.font_instr.render("↑/↓: Naviguer dans les options", True, self.border_color)
        instr_text2 = self.font_instr.render("←/→: Changer les valeurs", True, self.border_color)
        instr_text3 = self.font_instr.render("ENTRÉE: Sélectionner/Confirmer", True, self.border_color)
        instr_text4 = self.font_instr.render("ÉCHAP: Retour/Annuler", True, self.border_color)

        # Dimensions and positions
        menu_width = 800
        menu_height = 600
        menu_x = (self.screen.get_width() - menu_width) // 2
        menu_y = (self.screen.get_height() - menu_height) // 2

        # Menu sections
        sections = ["Résolution", "FPS", "Touches", "Appliquer", "Retour"]

        # Menu state
        current_section = 0
        controls_selected_index = 0  # Index for navigating through keys
        waiting_for_key = False
        is_in_controls_submenu = False  # To manage controls submenu

        # Find index of current resolution
        resolution_index = 0
        for i, res in enumerate(self.resolutions):
            if res == self.current_resolution:
                resolution_index = i
                break

        # Find index of current FPS
        fps_index = 0
        for i, fps in enumerate(self.fps_options):
            if fps == self.current_fps:
                fps_index = i
                break

        # Menu loop
        settings_menu_active = True
        clock = pygame.time.Clock()
        result = None

        while settings_menu_active:
            self.screen.blit(self.background, (0, 0))

            # Draw menu frame
            pygame.draw.rect(self.screen, self.border_color, (menu_x, menu_y, menu_width, menu_height))
            pygame.draw.rect(self.screen, self.bg_color, (menu_x + 4, menu_y + 4, menu_width - 8, menu_height - 8))

            # Title
            self.screen.blit(title_text, ((self.screen.get_width() - title_text.get_width()) // 2, menu_y + 20))

            # Instructions
            instructions_y = menu_y + menu_height - 120
            self.screen.blit(instr_text1, (menu_x + 20, instructions_y))
            self.screen.blit(instr_text2, (menu_x + 20, instructions_y + 25))
            self.screen.blit(instr_text3, (menu_x + 20, instructions_y + 50))
            self.screen.blit(instr_text4, (menu_x + 20, instructions_y + 75))

            # Key assignment waiting message
            if waiting_for_key:
                current_key_setting = list(self.controls.keys())[controls_selected_index]
                message = self.font_menu.render(f"Appuyez sur une touche pour: {current_key_setting}", True,
                                                (255, 255, 0))
                pygame.draw.rect(self.screen, self.border_color, (menu_x + 100, menu_y + 200, menu_width - 200, 60))
                pygame.draw.rect(self.screen, self.bg_color, (menu_x + 104, menu_y + 204, menu_width - 208, 52))
                self.screen.blit(message, (menu_x + 150, menu_y + 220))
            else:
                # Display main menu sections if not in controls submenu
                if not is_in_controls_submenu:
                    for i, section in enumerate(sections):
                        text_color = self.text_color
                        bg_color = None

                        # Selection of current section
                        if i == current_section:
                            bg_color = self.selected_color

                        # For resolution
                        if i == 0:
                            section_text = f"{section}: {self.current_resolution[0]}x{self.current_resolution[1]}"
                        # For FPS
                        elif i == 1:
                            section_text = f"{section}: {self.current_fps}"
                        else:
                            section_text = section

                        text = self.font_menu.render(section_text, True, text_color)

                        # Draw background if selected
                        if bg_color:
                            text_rect = pygame.Rect(menu_x + 50, menu_y + 100 + i * 50, text.get_width() + 20, 40)
                            pygame.draw.rect(self.screen, bg_color, text_rect)

                        self.screen.blit(text, (menu_x + 60, menu_y + 110 + i * 50))
                else:
                    # Display "Touches" title at top of submenu
                    section_text = "Touches"
                    text = self.font_menu.render(section_text, True, self.text_color)
                    text_rect = pygame.Rect(menu_x + 50, menu_y + 100, text.get_width() + 20, 40)
                    pygame.draw.rect(self.screen, self.border_color, text_rect)
                    self.screen.blit(text, (menu_x + 60, menu_y + 110))

                    # Display configurable keys in submenu
                    keys_list = list(self.controls.keys())
                    for j, action in enumerate(keys_list):
                        key = self.controls[action]
                        key_text = f"{action}: {self.get_key_display_name(key)}"

                        # Background for selected item
                        if j == controls_selected_index:
                            key_rect = pygame.Rect(menu_x + 100, menu_y + 180 + j * 40, 300, 30)
                            pygame.draw.rect(self.screen, self.selected_color, key_rect)

                        text = self.font_instr.render(key_text, True, self.text_color)
                        self.screen.blit(text, (menu_x + 110, menu_y + 185 + j * 40))

                    # Add "Back" button at bottom of controls submenu
                    back_text = "Retour"
                    back_btn = self.font_instr.render(back_text, True, self.text_color)
                    back_rect = pygame.Rect(menu_x + 100, menu_y + 380, 100, 30)

                    # Highlight if it's the selected index (after last key)
                    if controls_selected_index == len(keys_list):
                        pygame.draw.rect(self.screen, self.selected_color, back_rect)

                    self.screen.blit(back_btn, (menu_x + 110, menu_y + 385))

            pygame.display.flip()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if waiting_for_key:
                        # Capture any key for assignment
                        if event.key == pygame.K_ESCAPE:
                            waiting_for_key = False  # Cancel assignment
                        else:
                            # Convert key to usable string
                            if event.key == pygame.K_SPACE:
                                key_str = " "
                            elif event.key == pygame.K_LSHIFT:
                                key_str = "shift"
                            elif event.key == pygame.K_LCTRL:
                                key_str = "ctrl"
                            elif event.key == pygame.K_LALT:
                                key_str = "alt"
                            else:
                                try:
                                    key_str = chr(event.key).lower()
                                except:
                                    key_str = "a"  # Default key if not representable

                            # Assign key
                            current_key = list(self.controls.keys())[controls_selected_index]
                            self.controls[current_key] = key_str
                            waiting_for_key = False

                    else:
                        if event.key == pygame.K_ESCAPE:
                            if is_in_controls_submenu:
                                # Return to main menu from controls submenu
                                is_in_controls_submenu = False
                            else:
                                # Exit settings menu and return current values
                                settings_menu_active = False
                                result = (self.current_resolution, self.current_fps)

                        elif event.key == pygame.K_UP:
                            if is_in_controls_submenu:
                                # Navigation in controls submenu (includes "Back" button)
                                controls_selected_index = (controls_selected_index - 1) % (len(self.controls) + 1)
                            else:
                                # Navigation in main menu
                                current_section = (current_section - 1) % len(sections)

                        elif event.key == pygame.K_DOWN:
                            if is_in_controls_submenu:
                                # Navigation in controls submenu (includes "Back" button)
                                controls_selected_index = (controls_selected_index + 1) % (len(self.controls) + 1)
                            else:
                                # Navigation in main menu
                                current_section = (current_section + 1) % len(sections)

                        elif event.key == pygame.K_LEFT:
                            if not is_in_controls_submenu:
                                if current_section == 0:  # Resolution
                                    resolution_index = (resolution_index - 1) % len(self.resolutions)
                                    self.current_resolution = self.resolutions[resolution_index]
                                elif current_section == 1:  # FPS
                                    fps_index = (fps_index - 1) % len(self.fps_options)
                                    self.current_fps = self.fps_options[fps_index]

                        elif event.key == pygame.K_RIGHT:
                            if not is_in_controls_submenu:
                                if current_section == 0:  # Resolution
                                    resolution_index = (resolution_index + 1) % len(self.resolutions)
                                    self.current_resolution = self.resolutions[resolution_index]
                                elif current_section == 1:  # FPS
                                    fps_index = (fps_index + 1) % len(self.fps_options)
                                    self.current_fps = self.fps_options[fps_index]

                        elif event.key == pygame.K_RETURN:
                            if is_in_controls_submenu:
                                if controls_selected_index == len(self.controls):
                                    # "Back" button selected
                                    is_in_controls_submenu = False
                                else:
                                    # Start key assignment
                                    waiting_for_key = True
                            else:
                                if current_section == 2:  # Keys
                                    # Enter controls submenu
                                    is_in_controls_submenu = True
                                    controls_selected_index = 0
                                elif current_section == 3:  # Apply
                                    if self.save_config():
                                        # Display confirmation message
                                        message = self.font_menu.render("Configuration sauvegardée !", True,
                                                                        (255, 255, 0))
                                        self.screen.blit(message, (menu_x + 250, menu_y + 400))
                                        pygame.display.flip()
                                        pygame.time.delay(1000)  # Wait 1 second
                                    else:
                                        # Display error message
                                        message = self.font_menu.render("Erreur de sauvegarde !", True, (255, 0, 0))
                                        self.screen.blit(message, (menu_x + 250, menu_y + 400))
                                        pygame.display.flip()
                                        pygame.time.delay(1000)  # Wait 1 second
                                elif current_section == 4:  # Back
                                    settings_menu_active = False
                                    result = (self.current_resolution, self.current_fps)

            clock.tick(30)

        return result or (self.current_resolution, self.current_fps)  # Return current values