import pygame, math

damage = []

class Projectiles(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, type, sens, friendly):
        super().__init__()
        self.screen = screen
        self.x = x
        self.y = y
        self.friendly = friendly  # True if allied, False otherwise

        self.type = type
        if self.type == 1:  # Direct fire (straight shot)
            self.y += 6  # Y-offset downward
            self.rayon = 5
            self.couleur = (255, 0, 0)
            self.image = pygame.transform.scale(pygame.image.load("assets/entity/fire_bullet/fire_ball2.png"), (50, 50))
            self.rect = self.image.get_rect()
            self.vitesse = 4
            self.sens = sens
            self.lifetime = 300  # Lifespan in frames (5 seconds at 60 FPS)

        elif self.type == 2:  # Curved shot
            self.rayon = 5
            self.couleur = (255, 0, 0)
            self.image = pygame.transform.scale(pygame.image.load("assets/entity/fire_bullet/fire_ball2.png"), (50, 50))
            self.rect = self.image.get_rect()
            self.vect_y = -6  # Initial vertical velocity (upward)
            self.vitesse = 3  # Horizontal velocity
            self.sens = sens
            self.gravity = 0.2  # Gravity applied to projectile
            self.lifetime = 300  # Lifespan in frames

        elif self.type == 3:  # Meteor
            self.rayon = 5
            self.couleur = (255, 0, 0)
            self.angle = 45
            self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("assets/entity/fire_bullet/fire_ball.png"), (50, 50)), self.angle)
            self.rect = self.image.get_rect()
            self.vitesse = 3
            self.sens = 1
            self.y += -150
            self.lifetime = 300  # Lifespan in frames

        # Initial position of the rectangle
        self.rect.center = (x, y)

    def draw(self, screen_x, screen_y):
        self.rect.centerx = screen_x
        self.rect.centery = screen_y
        self.screen.blit(self.image, self.rect)


class FantomeProjectile(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, image, sens):
        super().__init__()
        self.screen = screen
        self.x = x
        self.y = y
        self.friendly = False  # Enemy projectile
        self.type = 4  # Ghost projectile specific type

        # Use provided image
        self.image = image

        # Make sure image is valid
        if self.image is None or not hasattr(self.image, 'get_rect'):
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 0, 0))

        # Resize image to be more visible
        self.image = pygame.transform.scale(self.image, (40, 40))

        self.rect = self.image.get_rect()

        # Projectile properties
        self.rayon = 10  # Increase radius for better detection
        self.couleur = (128, 0, 255)
        self.vitesse = 1.5  # Reduce speed for better visibility
        self.sens = sens
        self.lifetime = 600  # Lifespan in frames (10 seconds at 60 FPS)

        # Center rectangle at initial position
        self.rect.center = (x, y)

    def draw(self, screen_x, screen_y):
        # Draw the projectile on screen
        try:
            # Update rectangle position
            self.rect.centerx = int(screen_x)
            self.rect.centery = int(screen_y)

            # Draw projectile image
            self.screen.blit(self.image, self.rect)

            # Draw outline for debugging
            pygame.draw.rect(self.screen, self.couleur, self.rect, 1)
            pygame.draw.circle(self.screen, (255, 0, 0), (int(screen_x), int(screen_y)), 3)
        except Exception as e:
            pass


def projectiles_update(collidable_blocks=None, entities=None, damages_list=None):
    # Updates position of all projectiles and checks collisions
    if collidable_blocks is None:
        collidable_blocks = []

    if entities is None:
        entities = []

    if damages_list is None:
        damages_list = []

    for proj in damage[:]:  # Use a copy of the list to avoid deletion problems
        try:
            # Check if projectile has a lifetime
            if hasattr(proj, 'lifetime'):
                proj.lifetime -= 1
                if proj.lifetime <= 0:
                    damage.remove(proj)
                    continue

            # Save old position for collision checking
            old_x, old_y = proj.x, proj.y

            # Update positions based on type
            if proj.type == 1:  # Straight shot (type 1)
                proj.x += proj.vitesse * proj.sens

                # Check if projectile is off-screen
                if abs(proj.x) > 2000:  # Large enough value
                    damage.remove(proj)
                    continue

            elif proj.type == 2:  # Arcing shot (type 2)
                # Parabolic movement equation
                proj.vect_y += proj.gravity  # Apply gravity
                proj.y += proj.vect_y
                proj.x += proj.vitesse * proj.sens

                # Check if projectile is off-screen
                if abs(proj.x) > 2000 or abs(proj.y) > 2000:
                    damage.remove(proj)
                    continue

            elif proj.type == 3:  # Meteor
                proj.y += proj.vitesse * proj.sens
                proj.x += proj.vitesse * proj.sens * math.cos(proj.angle)

                # Check if projectile is off-screen
                if abs(proj.y) > 2000 or abs(proj.x) > 2000:
                    damage.remove(proj)
                    continue

            elif proj.type == 4:  # Ghost projectile
                proj.x += proj.vitesse * proj.sens

                # Check if projectile is off-screen
                if abs(proj.x) > 2000:
                    damage.remove(proj)
                    continue

            # Check collisions with entities (only for player projectiles)
            if proj.friendly and entities:
                proj_rect = pygame.Rect(proj.x - proj.rayon, proj.y - proj.rayon,
                                        proj.rayon * 2, proj.rayon * 2)

                entity_hit = False
                for entity in entities[:]:  # Use a copy to avoid problems during deletion
                    if entity.rect.colliderect(proj_rect):
                        # Entity hit by player projectile
                        # Remove damage rectangles associated with this entity
                        for dmg_info in damages_list[:]:
                            dmg_rect, entity_name = dmg_info
                            if entity_name == entity.name and hasattr(entity, 'damageRect'):
                                if dmg_rect == entity.damageRect:
                                    damages_list.remove(dmg_info)

                        # Remove entity from entities list
                        entities.remove(entity)

                        # Remove projectile
                        if proj in damage:
                            damage.remove(proj)

                        entity_hit = True
                        break

                if entity_hit:
                    continue  # Move to next projectile if an entity was hit

            # Check collisions with solid blocks
            if collidable_blocks:
                # Create rectangle for collision detection
                proj_rect = pygame.Rect(proj.x - proj.rayon, proj.y - proj.rayon,
                                        proj.rayon * 2, proj.rayon * 2)

                # Check collisions with all blocks
                for block in collidable_blocks:
                    if proj_rect.colliderect(block):
                        # If collision, remove projectile
                        if proj in damage:
                            damage.remove(proj)
                        break

        except Exception as e:
            if proj in damage:
                damage.remove(proj)