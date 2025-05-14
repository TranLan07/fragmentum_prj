from config import *
from Projectiles import damage

screen_size = screen_re()
deltaT = delta_t_re()


class Entity(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.name = name

        # Base image
        self.image = pygame.image.load(f"assets/entity/{name}/default.png")
        self.rect = self.image.get_rect()
        self.position = [int(x), int(y)]

        # Physics properties
        self.gravity = 0.2
        self.jump_speed = -4
        self.speed = 60

        # Collision rectangles
        self.rect_up = pygame.Rect(0, 0, 14, 1)
        self.rect_down = pygame.Rect(0, 0, 14, 1)
        self.rect_left = pygame.Rect(0, 0, 1, 30)
        self.rect_right = pygame.Rect(0, 0, 1, 30)
        self.rect_ground = pygame.Rect(0, 0, 14, 1)
        self.onground = pygame.Rect(0, 0, 0, 0)

        # States and vectors
        self.jumping = False
        self.colidlist = [0, 0, 0, 0]
        self.vector = [0.0, 0.0]
        self.ground_buffer = 2
        self.previous_position = []

        # Animation
        self.entity_time = 0
        self.phase = 0
        self.last_phase_time = 0
        self.sens_vision = 1
        self.walkRight = [self.image]
        self.walkLeft = [self.image]

        self.load_animations()

    def load_animations(self):
        # Load entity animations if folders exist
        try:
            walkright_path = f"Assets/entity/{self.name}/Walkright"
            if os.path.exists(walkright_path):
                walkright_filename = os.listdir(walkright_path)
                if walkright_filename:
                    self.walkRight = [pygame.image.load(f"{walkright_path}/{x}") for x in walkright_filename]
                else:
                    self.walkRight = [self.image]
            else:
                self.walkRight = [self.image]

            walkleft_path = f"Assets/entity/{self.name}/Walkleft"
            if os.path.exists(walkleft_path):
                walkleft_filename = os.listdir(walkleft_path)
                if walkleft_filename:
                    self.walkLeft = [pygame.image.load(f"{walkleft_path}/{x}") for x in walkleft_filename]
                else:
                    self.walkLeft = [self.image]
            else:
                self.walkLeft = [self.image]
        except Exception as e:
            self.walkRight = [self.image]
            self.walkLeft = [self.image]

    def entity_update(self):
        self.previous_position = self.position.copy()
        self.rect.topleft = (int(self.position[0]), int(self.position[1]))
        self.applyGravity()
        self.vector_traitement()
        self.update_colid_rect()
        self.handle_ground_collision()
        self.handle_lateral_collisions()
        self.vector[0] = max(-8, min(8, self.vector[0]))
        self.entity_clock()
        self.changement_phase()

    def mvu(self):
        if not self.jumping and self.colidlist[1] == 0:
            self.vector[1] = self.jump_speed

        if self.colidlist[1] == 1 and self.vector[1] < 0:
            self.vector[1] = 0

        self.position[1] += self.vector[1]

        if self.vector[1] >= 0:
            self.jumping = True

    def handle_ground_collision(self):
        if self.colidlist[0] == 1 and self.onground.center != (0, 0):
            self.position[1] = self.onground.top - self.rect.height + self.ground_buffer
            self.rect.topleft = (int(self.position[0]), int(self.position[1]))
            self.vector[1] = 0
            self.jumping = False

    def handle_lateral_collisions(self):
        if self.colidlist[2] == 1:  # Left collision
            if self.vector[0] < 0:
                self.vector[0] = 0
            if self.rect.left < self.previous_position[0]:
                self.position[0] = self.previous_position[0]
                self.rect.topleft = (int(self.position[0]), int(self.position[1]))

        if self.colidlist[3] == 1:  # Right collision
            if self.vector[0] > 0:
                self.vector[0] = 0
            if self.rect.right > self.previous_position[0] + self.rect.width:
                self.position[0] = self.previous_position[0]
                self.rect.topleft = (int(self.position[0]), int(self.position[1]))

    def vector_traitement(self):
        if self.vector[0] > 0:  # Right force
            if self.colidlist[3] == 0:  # No right collision
                self.position[0] += (self.speed * self.vector[0]) * deltaT
        elif self.vector[0] < 0:  # Left force
            if self.colidlist[2] == 0:  # No left collision
                self.position[0] += (self.speed * self.vector[0]) * deltaT

        # Apply natural friction
        if (self.vector[0] > 0 and self.colidlist[3] == 0) or (self.vector[0] < 0 and self.colidlist[2] == 0):
            self.vector[0] *= 0.8

        # Clean up very small values
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

        self.rect_left = pygame.Rect(0, 0, min(speed_size, 2), 30)
        self.rect_right = pygame.Rect(0, 0, min(speed_size, 2), 30)
        self.rect_up = pygame.Rect(0, 0, 14, min(jump_size, 2))
        self.rect_down = pygame.Rect(0, 0, 14, min(jump_size, 2))

        self.rect_up.center = (self.rect.center[0], self.rect.top - 1)
        self.rect_down.center = (self.rect.center[0], self.rect.bottom + 1)
        self.rect_left.center = (self.rect.left, self.rect.center[1])
        self.rect_left.left = self.rect.left - 2
        self.rect_right.center = (self.rect.right, self.rect.center[1])
        self.rect_right.right = self.rect.right + 2
        self.rect_ground.center = (self.rect.center[0], self.rect.bottom + 3)
        self.rect_ground.width = 14

    def entity_clock(self):
        self.entity_time += deltaT

    def changement_sens_vision(self):
        if self.vector[0] < 0:
            self.sens_vision = -1
        elif self.vector[0] > 0:
            self.sens_vision = 1

    def changement_phase(self):
        if self.entity_time - self.last_phase_time > 2 * deltaT:
            if abs(self.vector[0]) > 0.1 and abs(self.vector[1]) < 0.1:
                self.phase += 1
            self.last_phase_time = self.entity_time

        self.changement_sens_vision()
        animation_frames = self.walkLeft if self.sens_vision == -1 else self.walkRight

        if not animation_frames:
            animation_frames = [self.image]

        if self.phase >= len(animation_frames):
            self.phase = 0

        self.image = animation_frames[self.phase]
        current_pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = current_pos

    def restart(self, x, y):
        self.position = [int(x), int(y)]
        self.previous_position = [int(x), int(y)]
        self.rect.topleft = (int(x), int(y))
        self.vector = [0.0, 0.0]
        self.jumping = False
        self.colidlist = [0, 0, 0, 0]
        self.update_colid_rect()

    def update(self):
        self.entity_update()


# First enemy: the Slime
class Slime(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, "slime", x, y)
        self.detecRectDownRight = pygame.Rect(0, 0, 16, 16)
        self.downRightColid = False
        self.detecRectDownLeft = pygame.Rect(0, 0, 16, 16)
        self.downLeftColid = False
        self.maxRange = 100
        self.range = 0
        self.direction = 1
        self.damageRect = pygame.Rect(0, 0, 17, 17)

        # Adjust collision rects for slime
        self.rect_up = pygame.Rect(0, 0, 14, 1)
        self.rect_down = pygame.Rect(0, 0, 14, 1)
        self.rect_left = pygame.Rect(0, 0, 1, 5)
        self.rect_right = pygame.Rect(0, 0, 1, 5)

    def update_colid_rect(self):
        speed_size = abs(self.vector[0]) + 1
        jump_size = abs(self.vector[1]) + 1

        self.rect_left = pygame.Rect(0, 0, min(speed_size, 2), 5)
        self.rect_right = pygame.Rect(0, 0, min(speed_size, 2), 5)
        self.rect_up = pygame.Rect(0, 0, 14, min(jump_size, 2))
        self.rect_down = pygame.Rect(0, 0, 14, min(jump_size, 2))

        self.rect_up.center = (self.rect.center[0], self.rect.top - 1)
        self.rect_down.center = (self.rect.center[0], self.rect.bottom + 1)
        self.rect_left.center = (self.rect.left, self.rect.center[1])
        self.rect_left.left = self.rect.left - 2
        self.rect_right.center = (self.rect.right, self.rect.center[1])
        self.rect_right.right = self.rect.right + 2
        self.rect_ground.center = (self.rect.center[0], self.rect.bottom + 3)
        self.rect_ground.width = 14

    def detector_downright(self):
        self.detecRectDownRight.left = self.rect.right + 5
        self.detecRectDownRight.top = self.rect.bottom

    def detector_downleft(self):
        self.detecRectDownLeft.right = self.rect.left - 5
        self.detecRectDownLeft.top = self.rect.bottom

    def damageRect_pos(self):
        self.damageRect.center = self.rect.center

    def update_detector(self):
        self.detector_downright()
        self.detector_downleft()
        self.damageRect_pos()

    def detector_R(self):
        if self.colidlist[3] or not (self.downRightColid):
            return False
        else:
            return True

    def detector_L(self):
        if self.colidlist[2] or not (self.downLeftColid):
            return False
        else:
            return True

    def move(self):
        # Moving logic for slime - patrols back and forth
        if self.direction == 1:
            if self.range <= self.maxRange and self.detector_R():
                self.range += 0.1
                self.position[0] += 1
                self.vector[0] = 1
            else:
                self.vector[0] = 0
                self.direction = 0
        else:
            if self.range >= (-1 * self.maxRange) and self.detector_L():
                self.range -= 0.1
                self.position[0] -= 1
                self.vector[0] = -1
            else:
                self.vector[0] = 0
                self.direction = 1

    def update(self):
        self.update_detector()
        self.move()
        self.entity_update()


def create_slime(x, y):
    return Slime(x, y)


# Second enemy: the Ghost
class Fantome(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, "fantome", x, y)
        self.detection_range = 300
        self.detection_zone = pygame.Rect(0, 0, self.detection_range, 200)

        self.detecRectDownRight = pygame.Rect(0, 0, 16, 16)
        self.downRightColid = False
        self.detecRectDownLeft = pygame.Rect(0, 0, 16, 16)
        self.downLeftColid = False
        self.damageRect = pygame.Rect(0, 0, 17, 17)

        self.state = "idle"
        self.player_detected = False
        self.player = None
        self.attack_cooldown = 0
        self.attack_delay = 60

        self.animation_frame = 0
        self.is_attacking = False

        self.speed = 0
        self.animation_slowdown = 4

        self.can_shoot = True
        self.shoot_cooldown = 0
        self.shoot_delay = 120

        self.load_fantome_animations()
        self.load_projectile_images()

    def set_player(self, player):
        # Set player reference for detection
        self.player = player

    def load_fantome_animations(self):
        # Load ghost-specific animations
        try:
            idle_path = "assets/entity/fantome/idle"
            if os.path.exists(idle_path):
                idle_filename = os.listdir(idle_path)
                if idle_filename:
                    self.idle_frames = [pygame.image.load(f"{idle_path}/{x}") for x in idle_filename]
                else:
                    self.idle_frames = [self.image]
            else:
                self.idle_frames = [self.image]

            attackleft_path = "assets/entity/fantome/Attackleft"
            if os.path.exists(attackleft_path):
                attackleft_filename = sorted(os.listdir(attackleft_path))
                if attackleft_filename:
                    self.attack_left = [pygame.image.load(f"{attackleft_path}/{x}") for x in attackleft_filename]
                else:
                    self.attack_left = [self.image]
            else:
                self.attack_left = [self.image]

            attackright_path = "assets/entity/fantome/Attackright"
            if os.path.exists(attackright_path):
                attackright_filename = sorted(os.listdir(attackright_path))
                if attackright_filename:
                    self.attack_right = [pygame.image.load(f"{attackright_path}/{x}") for x in attackright_filename]
                else:
                    self.attack_right = [self.image]
            else:
                self.attack_right = [self.image]

        except Exception as e:
            self.idle_frames = [self.image]
            self.attack_left = [self.image]
            self.attack_right = [self.image]

    def load_projectile_images(self):
        # Load ghost projectile images
        try:
            projectile_left_path = "assets/entity/fantome/Projectileleft"
            if os.path.exists(projectile_left_path):
                projectile_left_filename = os.listdir(projectile_left_path)
                if projectile_left_filename:
                    file_path = f"{projectile_left_path}/{projectile_left_filename[0]}"
                    self.projectile_left = pygame.image.load(file_path)
                else:
                    self.projectile_left = pygame.Surface((20, 20))
                    self.projectile_left.fill((255, 0, 0))
            else:
                self.projectile_left = pygame.Surface((20, 20))
                self.projectile_left.fill((255, 0, 0))

            projectile_right_path = "assets/entity/fantome/Projectileright"
            if os.path.exists(projectile_right_path):
                projectile_right_filename = os.listdir(projectile_right_path)
                if projectile_right_filename:
                    file_path = f"{projectile_right_path}/{projectile_right_filename[0]}"
                    self.projectile_right = pygame.image.load(file_path)
                else:
                    self.projectile_right = pygame.Surface((20, 20))
                    self.projectile_right.fill((255, 0, 0))
            else:
                # Default image if folder doesn't exist
                self.projectile_right = pygame.Surface((20, 20))
                self.projectile_right.fill((255, 0, 0))

        except Exception as e:
            # Default images in case of error
            self.projectile_left = pygame.Surface((20, 20))
            self.projectile_left.fill((255, 0, 0))
            self.projectile_right = pygame.Surface((20, 20))
            self.projectile_right.fill((255, 0, 0))

    def update_detection_zone(self):
        # Update detection zone around the ghost
        self.detection_zone = pygame.Rect(
            self.rect.centerx - self.detection_range // 2,
            self.rect.centery - 100,
            self.detection_range,
            200
        )

    def update_detector(self):
        # Update detection rectangles
        self.detector_downright()
        self.detector_downleft()
        self.damageRect_pos()

    def detector_downright(self):
        self.detecRectDownRight.left = self.rect.right + 5
        self.detecRectDownRight.top = self.rect.bottom

    def detector_downleft(self):
        self.detecRectDownLeft.right = self.rect.left - 5
        self.detecRectDownLeft.top = self.rect.bottom

    def damageRect_pos(self):
        self.damageRect.center = self.rect.center

    def changement_phase(self):
        # Animation method using ghost states
        if self.entity_time - self.last_phase_time > 2 * deltaT * self.animation_slowdown:
            if self.is_attacking:
                self.animation_frame += 1
                frames = self.attack_left if self.state == "attack_left" else self.attack_right
                if self.animation_frame >= len(frames):
                    if self.can_shoot:
                        if hasattr(self.player, 'screen'):
                            screen = self.player.screen
                        else:
                            import pygame
                            screen = pygame.display.get_surface()

                        self.shoot(screen)

                    # Reset animation and go to cooldown
                    self.animation_frame = 0
                    self.is_attacking = False
                    self.attack_cooldown = self.attack_delay
            else:
                self.phase += 1

            self.last_phase_time = self.entity_time

        # Determine which animation to use based on state
        if self.is_attacking:
            if self.state == "attack_left":
                frames = self.attack_left
                self.sens_vision = -1
            else:
                frames = self.attack_right
                self.sens_vision = 1

            if self.animation_frame >= len(frames):
                self.animation_frame = 0

            self.image = frames[self.animation_frame]
        else:
            # Normal animation based on state
            if self.state == "idle":
                # Make sure frames list isn't empty
                if not hasattr(self, 'idle_frames') or not self.idle_frames:
                    self.idle_frames = [self.image]

                if self.phase >= len(self.idle_frames):
                    self.phase = 0

                self.image = self.idle_frames[self.phase]
            elif self.state == "attack_left" or self.state == "attack_right":
                # Start a new attack sequence if cooldown is done
                if not self.is_attacking and self.attack_cooldown == 0 and self.can_shoot:
                    self.is_attacking = True
                    self.animation_frame = 0

                # Set vision direction based on current state
                self.sens_vision = -1 if self.state == "attack_left" else 1

                # If not attacking (not yet or in cooldown), use idle image
                if not self.is_attacking:
                    self.image = self.idle_frames[
                        self.phase % len(self.idle_frames)] if self.idle_frames else self.image

        current_pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = current_pos

    def detect_player(self):
        # Detect if player is in detection zone
        if not self.player:
            return False

        if self.detection_zone.colliderect(self.player.rect):
            # Determine if player is to the left or right
            if self.player.rect.centerx < self.rect.centerx:
                self.state = "attack_left"
            else:
                self.state = "attack_right"
            return True
        else:
            self.state = "idle"
            return False

    def shoot(self, screen):
        # Shoot a projectile toward the player
        if not self.can_shoot:
            return
        direction = -1 if self.state == "attack_left" else 1

        from Projectiles import FantomeProjectile, damage
        try:
            projectile_x = self.rect.centerx + (direction * 20)
            projectile_y = self.rect.centery

            if direction == -1:
                projectile_img = self.projectile_left
            else:
                projectile_img = self.projectile_right

            # Add projectile to the projectiles list
            proj = FantomeProjectile(screen, projectile_x, projectile_y, projectile_img, direction)
            damage.append(proj)

            # Set cooldown
            self.can_shoot = False
            self.shoot_cooldown = self.shoot_delay

        except Exception as e:
            import traceback
            traceback.print_exc()

    def update(self):
        # Override update method for ghost-specific behavior
        # Update detection zone
        self.update_detection_zone()

        # Update detectors to avoid errors
        self.update_detector()

        # Detect if player is in the zone
        self.player_detected = self.detect_player()

        # Decrement attack cooldown counter if active
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Decrement shooting cooldown if active
        if not self.can_shoot:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.can_shoot = True

        # Call base update method for physics and animation
        self.entity_update()


# Function to create a ghost
def create_fantome(x, y):
    return Fantome(x, y)


# Dictionary of available entity types for Tiled
entity_type = {
    "slime": create_slime,
    "fantome": create_fantome
}