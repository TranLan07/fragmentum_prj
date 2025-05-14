import pygame, os
from config import *

screen_size = screen_re()
deltaT = delta_t_re()

# Charger les animations du joueur
walkright_filename = os.listdir(r"Assets/entity/player/Walkright")
walkleft_filename = os.listdir(r"Assets/entity/player/Walkleft")
walkRight = [pygame.image.load(rf"Assets/entity/player/Walkright/{x}") for x in walkright_filename]
walkLeft = [pygame.image.load(rf"Assets/entity/player/Walkleft/{x}") for x in walkleft_filename]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.name = "player"
        self.image = pygame.image.load("assets/entity/player/default.png")
        self.rect = self.image.get_rect()
        self.position = [int(x), int(y)]
        self.gravity = 0.2
        self.jump_speed = -4
        self.speed = 60

        # Rectangles de collision
        self.rect_up = pygame.Rect(0, 0, 14, 1)
        self.rect_down = pygame.Rect(0, 0, 14, 1)
        self.rect_left = pygame.Rect(0, 0, 1, 30)
        self.rect_right = pygame.Rect(0, 0, 1, 30)
        self.rect_ground = pygame.Rect(0, 0, 14, 1)
        self.onground = pygame.Rect(0, 0, 0, 0)

        self.running = 0
        self.jumping = False
        self.colidlist = [0, 0, 0, 0]
        self.vector = [0.0, 0.0]
        self.effets = dict()
        self.items = []
        self.ground_buffer = 2
        self.previous_position = []

        # Animation
        self.player_time = 0
        self.phase = 0
        self.last_phase_time = 0
        self.sens_vision = 1
        self.is_dead = False

        # Double saut
        self.double_jump_available = True
        self.can_db_jump = False

        # Tir
        self.can_shoot = True
        self.shoot_cooldown = 0
        self.shoot_delay = 20
        self.screen = None

    def player_update(self):
        # Sauvegarde de la position précédente
        self.previous_position = self.position.copy()
        self.rect.topleft = (int(self.position[0]), int(self.position[1]))

        # Physique et mouvement
        self.applyGravity()
        self.vector_traitement()
        self.update_colid_rect()
        self.update_shoot_cooldown()
        self.handle_ground_collision()
        self.handle_lateral_collisions()

        # Limiter la vitesse horizontale
        self.vector[0] = max(-8, min(8, self.vector[0]))

        # Animation
        self.player_clock()
        self.changement_phase()

    def add_item(self, item_name):
        self.items.append(item_name)

    def mvu(self):
        if not self.jumping and self.colidlist[1] == 0:
            self.vector[1] = self.jump_speed
            self.double_jump_available = True

        if self.colidlist[1] == 1 and self.vector[1] < 0:
            self.vector[1] = 0

        self.position[1] += self.vector[1]

        if self.vector[1] >= 0:
            self.jumping = True

    def double_jump(self):
        if self.can_db_jump and (self.jumping and self.double_jump_available):
            self.vector[1] = self.jump_speed

        if self.colidlist[1] == 1 and self.vector[1] < 0:
            self.vector[1] = 0
        self.position[1] += self.vector[1]

        self.double_jump_available = False

    def handle_ground_collision(self):
        if self.colidlist[0] == 1 and self.onground.center != (0, 0):
            self.position[1] = self.onground.top - self.rect.height + self.ground_buffer
            self.rect.topleft = (int(self.position[0]), int(self.position[1]))
            self.vector[1] = 0
            self.jumping = False

    def handle_lateral_collisions(self):
        if self.colidlist[2] == 1:  # Collision à gauche
            if self.vector[0] < 0:
                self.vector[0] = 0
            if self.rect.left < self.previous_position[0]:
                self.position[0] = self.previous_position[0]
                self.rect.topleft = (int(self.position[0]), int(self.position[1]))

        if self.colidlist[3] == 1:  # Collision à droite
            if self.vector[0] > 0:
                self.vector[0] = 0
            if self.rect.right > self.previous_position[0] + self.rect.width:
                self.position[0] = self.previous_position[0]
                self.rect.topleft = (int(self.position[0]), int(self.position[1]))

    def vector_traitement(self):
        if self.vector[0] > 0:  # Force vers la droite
            if self.colidlist[3] == 0:  # Pas de collision à droite
                self.position[0] += (self.speed * self.vector[0] + self.running) * deltaT
        elif self.vector[0] < 0:  # Force vers la gauche
            if self.colidlist[2] == 0:  # Pas de collision à gauche
                self.position[0] += (self.speed * self.vector[0] - self.running) * deltaT

        # Friction naturelle
        if (self.vector[0] > 0 and self.colidlist[3] == 0) or (self.vector[0] < 0 and self.colidlist[2] == 0):
            self.vector[0] *= 0.8  # Friction pour ralentir

        # Si la vitesse est très faible, la mettre à zéro
        if abs(self.vector[0]) < 0.1:
            self.vector[0] = 0

    def applyGravity(self):
        if self.colidlist[0] == 0:
            self.vector[1] += self.gravity
            self.jumping = True
            self.position[1] += self.vector[1]
        else:
            self.jumping = False

    def update_colid_rect(self):
        speed_size = abs(self.vector[0]) + 1
        jump_size = abs(self.vector[1]) + 1

        # Mettre à jour les rectangles de collision
        self.rect_left = pygame.Rect(0, 0, min(speed_size, 2), 30)
        self.rect_right = pygame.Rect(0, 0, min(speed_size, 2), 30)
        self.rect_up = pygame.Rect(0, 0, 14, min(jump_size, 2))
        self.rect_down = pygame.Rect(0, 0, 14, min(jump_size, 2))

        # Positionnement des rectangles
        self.rect_up.center = (self.rect.center[0], self.rect.top - 1)
        self.rect_down.center = (self.rect.center[0], self.rect.bottom + 1)
        self.rect_left.center = (self.rect.left, self.rect.center[1])
        self.rect_left.left = self.rect.left - 2
        self.rect_right.center = (self.rect.right, self.rect.center[1])
        self.rect_right.right = self.rect.right + 2
        self.rect_ground.center = (self.rect.center[0], self.rect.bottom + 3)
        self.rect_ground.width = 14

    def run(self):
        self.running = 50

    def norun(self):
        self.running = 0

    def player_clock(self):
        self.player_time += deltaT

    def changement_sens_vision(self):
        if self.vector[0] < 0:
            self.sens_vision = -1
        elif self.vector[0] > 0:
            self.sens_vision = 1

    def changement_phase(self):
        if self.player_time - self.last_phase_time > 2 * deltaT:
            if abs(self.vector[0]) > 0.1 and abs(self.vector[1]) < 0.1:
                self.phase += 1
            self.last_phase_time = self.player_time
        self.phase %= 7
        self.changement_sens_vision()
        if self.sens_vision == -1:
            self.image = walkLeft[self.phase]
        elif self.sens_vision == 1:
            self.image = walkRight[self.phase]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.position[0], self.position[1])

    def restart(self, x, y):
        self.position = [int(x), int(y)]
        self.previous_position = [int(x), int(y)]
        self.rect.topleft = (int(x), int(y))
        self.vector = [0.0, 0.0]
        self.jumping = False
        self.colidlist = [0, 0, 0, 0]
        self.update_colid_rect()

    def set_screen(self, screen):
        """Définir une référence à l'écran de jeu"""
        self.screen = screen

    def shoot_straight(self, direction):
        """Tirer un projectile droit (type 1)"""
        if not self.can_shoot or not self.screen:
            return

        from Projectiles import Projectiles, damage

        # Position de départ du projectile
        if direction > 0:  # Tir vers la droite
            start_x = self.rect.right + 5
        else:  # Tir vers la gauche
            start_x = self.rect.left - 5

        start_y = self.rect.centery

        # Créer le projectile
        damage.append(Projectiles(self.screen, start_x, start_y, 1, direction, True))

        # Activer le cooldown
        self.can_shoot = False
        self.shoot_cooldown = self.shoot_delay

    def shoot_arc(self):
        """Tirer un projectile en cloche (type 2)"""
        if not self.can_shoot or not self.screen:
            return

        from Projectiles import Projectiles, damage

        # Utiliser la direction actuelle du joueur
        direction = self.sens_vision

        # Position de départ du projectile
        if direction > 0:  # Tir vers la droite
            start_x = self.rect.right + 5
        else:  # Tir vers la gauche
            start_x = self.rect.left - 5

        start_y = self.rect.centery - 10  # Légèrement plus haut pour le tir en cloche

        # Créer le projectile
        damage.append(Projectiles(self.screen, start_x, start_y, 2, direction, True))

        # Activer le cooldown
        self.can_shoot = False
        self.shoot_cooldown = self.shoot_delay

    def update_shoot_cooldown(self):
        """Mettre à jour le cooldown de tir"""
        if not self.can_shoot:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.can_shoot = True

    def handle_shooting_input(self, keys_pressed):
        """Gérer les entrées de tir"""
        if keys_pressed[pygame.K_RIGHT]:
            self.shoot_straight(1)  # Tirer vers la droite
        elif keys_pressed[pygame.K_LEFT]:
            self.shoot_straight(-1)  # Tirer vers la gauche
        elif keys_pressed[pygame.K_UP]:
            self.shoot_arc()  # Tirer en cloche