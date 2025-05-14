from dataclasses import dataclass
import pygame
import pytmx
import pyscroll
from Entities import *

l_map = [
    "tuto",
    "Cave_Hub",
    "blue_lagun",
    "Bouillémissaire",
    "Cave_Hub",
    "crocoditlheure_room",
    "Eagle_Fury",
    "Feujita",
    "mangroove_cave",
    "skyCity",
    "Volcarien"
]
map_path = "assets/map/"


@dataclass
class Map:
    # id
    name: str
    # entités
    entities: list
    npc:list
    # collisions
    walls: list[pygame.Rect]
    death: list[pygame.Rect]
    dead: list[pygame.Rect]
    # items
    items: list[pygame.Rect]
    item_sprites: list
    item_indices: dict
    item_names: dict
    # steles
    steles: list[pygame.Rect]  # Rectangles de collision des stèles
    stele_names: dict  # Noms des stèles
    stele_lit: dict  # État d'allumage des stèles (True/False)
    flames: list  # Liste des objets flammes
    flame_map: dict  # Mapping des flammes aux stèles
    # data map
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.util_pygame.load_pygame
    map_data: pyscroll.data.TiledMapData
    map_layer: pyscroll.orthographic.BufferedRenderer
    map_ways: list
    map_spawns: dict


class Maps:
    def __init__(self, screen, player):
        self.maps = dict()
        self.wRect = []
        self.cmap = "tuto"
        self.screen = screen
        self.player = player
        # Nouvel attribut pour suivre la stèle à proximité
        self.nearby_stele = None
        # Font pour le texte d'interaction
        self.font = pygame.font.Font(None, 30)  # Vous pouvez ajuster la taille (30)
        for m in l_map:
            self.register_map(m)
        player_spawn_pos = self.getCurrentMap().tmx_data.get_object_by_name("default")
        self.spawn = [player_spawn_pos.x - 32, player_spawn_pos.y - 64]
        self.is_dead = False
        self.damages = []

    def register_map(self, name):
        # load map
        tmx_file = f"{name}.tmx"
        tmx_data = pytmx.util_pygame.load_pygame(map_path + tmx_file)
        '''try:
            tmx_data = pytmx.util_pygame.load_pygame(map_path + tmx_file)
        except:
            print(f"ERREUR: Fichier {tmx_file} non trouvé")
            return'''
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 4
        # affichage map
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)
        group.add(self.player)
        # systeme de collisions
        items = []
        item_names = {}  # Dictionnaire pour associer les rectangles aux noms d'items
        item_indices = {}  # Dictionnaire pour associer les indices aux rectangles
        entities = []
        walls = []
        death = []
        dead = []
        steles = []
        stele_names = {}
        stele_lit = {}
        flames = []
        flame_map = {}
        way = []
        spawn = {}
        npc=[]
        for obj in tmx_data.objects:
            if obj.type == 'collision':
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'death':
                death.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'dead':
                dead.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'way':
                way.append((pygame.Rect(obj.x, obj.y, obj.width, obj.height), obj.name))
            elif obj.type == 'flame':  # Gestion des flammes
                # Récupérer la flamme associée à une stèle
                flame_name = obj.name if hasattr(obj, 'name') and obj.name else "flame_default"
                # Extraire le type de la flamme (ex: "flame_feu" -> "feu")
                flame_type = flame_name.split('_')[1] if '_' in flame_name else "default"
                # Stocker l'objet flamme avec sa position et sa visibilité
                flames.append({
                    'obj': obj,  # L'objet flamme entier
                    'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                    'type': flame_type,
                    'visible': False,  # Par défaut, les flammes sont invisibles
                    'name': flame_name
                })
                # Créer une association entre le type de flamme et l'indice dans la liste des flammes
                stele_type = f"stele_{flame_type}"
                flame_map[stele_type] = len(flames) - 1
            elif obj.type == 'spawn':
                spawn[obj.name] = [obj.x, obj.y]
            elif obj.type == 'entity':
                new_entity = entity_type[obj.name](obj.x, obj.y)
                # Si l'entité est un fantôme, lui donner une référence au joueur
                if obj.name == "fantome" and hasattr(new_entity, 'set_player'):
                    new_entity.set_player(self.player)
                    # Donner également une référence à l'écran
                    if hasattr(new_entity, 'screen'):
                        new_entity.screen = self.screen
                entities.append(new_entity)
            elif obj.type == 'npc':
                npc.append((obj.name,pygame.Rect(obj.x, obj.y, obj.width, obj.height)))
            elif obj.type == 'stele':  # Gestion des stèles
                stele_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                steles.append(stele_rect)
                # Utiliser un tuple de coordonnées comme clé
                key = (stele_rect.x, stele_rect.y, stele_rect.width, stele_rect.height)
                # Stocker le nom de la stèle
                if hasattr(obj, 'name') and obj.name:
                    stele_names[key] = obj.name
                else:
                    stele_names[key] = "stele_default"
                # Initialiser l'état d'allumage à False
                stele_lit[key] = False
            elif obj.type == 'items':
                item_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                item_index = len(items)
                items.append(item_rect)
                # Utiliser un tuple de coordonnées comme clé au lieu du rect
                key = (item_rect.x, item_rect.y, item_rect.width, item_rect.height)
                item_indices[key] = item_index  # Associer l'index au rectangle

                # Stocker le nom de l'item s'il existe
                if hasattr(obj, 'name') and obj.name:
                    item_names[key] = obj.name
                else:
                    item_names[key] = f"item_{item_index}"  # Nom par défaut

        # Affichage items
        item_sprites = []
        for obj in tmx_data.objects:
            if obj.type == 'items' and hasattr(obj, 'gid') and obj.gid:
                image = tmx_data.get_tile_image_by_gid(obj.gid)
                if image:
                    # Stocker l'image et sa position
                    item_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    # Le zoom du calque de la carte est appliqué aux sprites
                    item_name = obj.name if hasattr(obj, 'name') and obj.name else f"item_{len(item_sprites)}"
                    item_sprites.append({
                        'image': image,
                        'world_pos': (obj.x, obj.y),
                        'rect': item_rect,
                        'collected': False,  # Statut de collection
                        'name': item_name  # Ajouter le nom de l'item
                    })
        self.maps[name] = Map(name,
                              entities,
                              npc,
                              walls,
                              death,
                              dead,
                              items,
                              item_sprites,
                              item_indices,
                              item_names,
                              steles,
                              stele_names,
                              stele_lit,
                              flames,
                              flame_map,
                              group,
                              tmx_data,
                              map_data,
                              map_layer,
                              way,
                              spawn)
        print(f"{name} a été chargé avec succès")
        self.update_way_rects()

    def change_map(self, name):
        target_map = self.getMap(name)

        if self.cmap in target_map.map_spawns:
            spawn_pos = target_map.map_spawns[self.cmap]
        elif "default" in target_map.map_spawns:
            # Utiliser le spawn par défaut
            spawn_pos = target_map.map_spawns["default"]
        else:
            # Aucun spawn défini, utiliser un point arbitraire
            print("Erreur, spawn introuvable")
            spawn_pos = [100, 100]

        self.spawn = [spawn_pos[0] - 32, spawn_pos[1] - 64]
        self.cmap = name
        # reset vecteur de déplacement du joueur
        self.player.vector = [0, 0]
        self.player.jumping = False

        # Positionnement exact avec des floats pour éviter des erreurs d'arrondi
        self.player.position = [self.spawn[0], self.spawn[1]]
        self.player.previous_position = self.player.position.copy()  # Mettre à jour previous_position
        self.player.onground = pygame.Rect(0, 0, 0, 0)

        # Mettre à jour le rectangle du joueur immédiatement
        self.player.rect.topleft = (int(self.player.position[0]), int(self.player.position[1]))

        # Réinitialiser les états de collision
        self.player.colidlist = [0, 0, 0, 0]

        # Réinitialisation de la stèle à proximité lors du changement de carte
        self.nearby_stele = None

        self.update_way_rects()
        self.collisions_update()

    # Transition de coordonnées (relatives / absolues)

    def screen_to_world(self, screen_pos):
        # Conversion des coordonnées écran vers monde
        map_offset = self.get_group().get_center()
        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        # Calculer la position dans le monde
        world_x = screen_pos[0] + map_offset[0] - screen_center[0]
        world_y = screen_pos[1] + map_offset[1] - screen_center[1]
        return world_x, world_y

    # Ajouter cette méthode à la classe Maps
    def get_solid_blocks(self):
        """Récupère tous les blocs solides de la carte actuelle"""
        return self.get_walls()

    def world_to_screen(self, world_pos):
        """Conversion des coordonnées monde vers écran en tenant compte des limites de la carte"""
        # Obtenir la taille du monde (carte)
        map_width = self.getCurrentMap().tmx_data.width * self.getCurrentMap().tmx_data.tilewidth
        map_height = self.getCurrentMap().tmx_data.height * self.getCurrentMap().tmx_data.tileheight

        # Appliquer le zoom de la carte
        map_width *= self.get_map_layer().zoom
        map_height *= self.get_map_layer().zoom

        # Déterminer le centre de la caméra (en respectant les limites de la carte)
        screen_width, screen_height = self.screen.get_size()
        camera_x = self.player.rect.centerx
        camera_y = self.player.rect.centery

        # Limiter la caméra pour qu'elle ne dépasse pas les bords
        half_screen_width = screen_width / (2 * self.get_map_layer().zoom)
        half_screen_height = screen_height / (2 * self.get_map_layer().zoom)

        # Limites de la caméra (en coordonnées monde)
        left_limit = half_screen_width
        right_limit = map_width / self.get_map_layer().zoom - half_screen_width
        top_limit = half_screen_height
        bottom_limit = map_height / self.get_map_layer().zoom - half_screen_height

        # Appliquer les limites à la caméra
        if left_limit < right_limit:  # Seulement si la carte est plus large que l'écran
            camera_x = max(left_limit, min(camera_x, right_limit))
        if top_limit < bottom_limit:  # Seulement si la carte est plus haute que l'écran
            camera_y = max(top_limit, min(camera_y, bottom_limit))

        # Calculer la position à l'écran par rapport à la caméra
        screen_center_x = screen_width / 2
        screen_center_y = screen_height / 2

        # Calculer la position à l'écran
        screen_x = screen_center_x + (world_pos[0] - camera_x) * self.get_map_layer().zoom
        screen_y = screen_center_y + (world_pos[1] - camera_y) * self.get_map_layer().zoom

        return screen_x, screen_y

    # Trouver une map :

    def getMap(self, name):
        return self.maps[name]

    def get_map_spawn(self, name):
        return self.getMap(name).map_spawns

    # data de Cmap :

    def getCurrentMap(self):
        return self.getMap(self.cmap)

    def get_group(self):
        return self.getCurrentMap().group

    def get_walls(self):
        return self.getCurrentMap().walls

    def get_death(self):
        return self.getCurrentMap().death

    def get_dead(self):
        return self.getCurrentMap().dead

    def get_ways(self):
        return self.getCurrentMap().map_ways

    def get_items(self):
        return self.getCurrentMap().items

    def get_item_sprites(self):
        return self.getCurrentMap().item_sprites

    def get_item_names(self):
        return self.getCurrentMap().item_names

    def get_steles(self):
        return self.getCurrentMap().steles

    def get_stele_names(self):
        return self.getCurrentMap().stele_names

    def get_stele_lit(self):
        return self.getCurrentMap().stele_lit

    def get_flames(self):
        return self.getCurrentMap().flames

    def get_flame_map(self):
        return self.getCurrentMap().flame_map

    def get_item_indices(self):
        return self.getCurrentMap().item_indices

    def get_map_layer(self):
        return self.getCurrentMap().map_layer

    def get_damages(self):
        """Renvoie une référence à la liste des dommages"""
        return self.damages

    # ------------- Draw :

    def draw(self):
        self.get_group().remove(self.player)
        self.get_group().draw(self.screen)
        self.get_group().add(self.player)
        self.draw_flames()
        self.draw_items()
        self.draw_entities()
        self.draw_projectiles()
        self.draw_player()
        # Dessiner le message d'interaction si le joueur est près d'une stèle
        self.draw_interaction_message()
        self.get_group().center(self.player.rect.center)

    def draw_projectiles(self):
        """Dessine tous les projectiles actifs"""
        from Projectiles import damage

        if not damage:
            return

        for proj in damage:
            try:
                # Convertir les coordonnées monde en coordonnées écran
                screen_pos = self.world_to_screen((proj.x, proj.y))

                # Dessiner le projectile à la position convertie
                proj.draw(screen_pos[0], screen_pos[1])

            except Exception as e:
                print(f"Erreur lors de l'affichage d'un projectile: {e}")

    def draw_interaction_message(self):
        # Si le joueur est près d'une stèle non allumée avec la bonne torche
        if self.nearby_stele:
            rect_key, stele_name = self.nearby_stele

            # Extraire le type de la stèle
            stele_type = stele_name.split('_')[1] if '_' in stele_name else "default"
            torch_name = f"torche_{stele_type}"

            # Vérifier si le joueur a la bonne torche et que la stèle n'est pas déjà allumée
            if torch_name in self.player.items and not self.get_stele_lit()[rect_key]:
                # Créer le texte d'interaction
                text_surface = self.font.render("F pour allumer la flamme", True, (255, 255, 255))

                # Positionner le texte au-dessus du joueur
                screen_pos = self.world_to_screen((self.player.position[0] + self.player.rect.width / 2,
                                                   self.player.position[1] - 20))

                # Dessiner le texte
                text_rect = text_surface.get_rect(center=(screen_pos[0], screen_pos[1]))
                self.screen.blit(text_surface, text_rect)

    def draw_flames(self):
        # Dessiner les flammes qui sont marquées comme visibles
        for flame in self.get_flames():
            if flame['visible']:
                try:
                    # Si l'objet a un gid (donc une image)
                    if hasattr(flame['obj'], 'gid') and flame['obj'].gid:
                        # Récupérer l'image de la flamme
                        image = self.getCurrentMap().tmx_data.get_tile_image_by_gid(flame['obj'].gid)
                        if image:
                            # Convertir les coordonnées monde en coordonnées écran
                            screen_pos = self.world_to_screen((flame['obj'].x, flame['obj'].y))

                            # Appliquer le zoom à l'image
                            zoomed_width = int(image.get_width() * self.get_map_layer().zoom)
                            zoomed_height = int(image.get_height() * self.get_map_layer().zoom)
                            zoomed_image = pygame.transform.scale(image, (zoomed_width, zoomed_height))

                            # Dessiner l'image à la position convertie
                            self.screen.blit(zoomed_image, (int(screen_pos[0]), int(screen_pos[1])))
                except Exception as e:
                    print(f"Erreur lors de l'affichage d'une flamme: {e}")

    # --------------------------------------/ Items :
    def draw_items(self):
        # Dessine tous les items sur l'écran qui n'ont pas été collectés
        for item in self.get_item_sprites():
            if not item['collected']:  # Ne dessiner que les items non collectés
                try:
                    # Convertir les coordonnées monde en coordonnées écran
                    screen_pos = self.world_to_screen(item['world_pos'])

                    # Appliquer le zoom à l'image
                    zoomed_width = int(item['image'].get_width() * self.get_map_layer().zoom)
                    zoomed_height = int(item['image'].get_height() * self.get_map_layer().zoom)
                    zoomed_image = pygame.transform.scale(item['image'], (zoomed_width, zoomed_height))

                    # Dessiner l'image à la position convertie
                    self.screen.blit(zoomed_image, (int(screen_pos[0]), int(screen_pos[1])))

                except Exception as e:
                    print(f"Erreur lors de l'affichage d'un item: {e}")

    def draw_player(self):
        # Dessine tous les items sur l'écran qui n'ont pas été collectés
        try:
            # Convertir les coordonnées monde en coordonnées écran
            screen_pos = self.world_to_screen(self.player.position)

            # Appliquer le zoom à l'image
            zoomed_width = int(self.player.image.get_width() * self.get_map_layer().zoom)
            zoomed_height = int(self.player.image.get_height() * self.get_map_layer().zoom)
            zoomed_image = pygame.transform.scale(self.player.image, (zoomed_width, zoomed_height))

            # Dessiner l'image à la position convertie
            self.screen.blit(zoomed_image, (int(screen_pos[0]), int(screen_pos[1])))

        except Exception as e:
            print(f"Erreur lors de l'affichage d'un item: {e}")

    def check_item_collisions(self):
        # Vérifie si le joueur touche un item
        for i, item_rect in enumerate(
                self.get_items().copy()):  # Utilisation d'une copie pour éviter les problèmes lors de la suppression
            if self.player.rect.colliderect(item_rect):
                # Le joueur a touché un item
                rect_key = (item_rect.x, item_rect.y, item_rect.width, item_rect.height)
                item_name = self.get_item_names().get(rect_key, f"item_{i}")
                print(f"Item collecté: {item_name}")

                # Ajouter le nom de l'item à l'inventaire du joueur
                self.player.add_item(item_name)

                # Marquer l'item comme collecté dans item_sprites
                for sprite in self.get_item_sprites():
                    if sprite['rect'] == item_rect and not sprite['collected']:
                        sprite['collected'] = True
                        break

                # Supprimer le rectangle de collision
                self.get_items().remove(item_rect)

                # Suppression des entrées correspondantes dans les dictionnaires
                if rect_key in self.get_item_indices():
                    del self.get_item_indices()[rect_key]
                if rect_key in self.get_item_names():
                    del self.get_item_names()[rect_key]
                break

    def check_stele_collisions(self):
        # Réinitialiser la stèle à proximité
        self.nearby_stele = None

        # Vérifie si le joueur touche une stèle
        for stele_rect in self.get_steles():
            if self.player.rect.colliderect(stele_rect):
                # Le joueur a touché une stèle
                rect_key = (stele_rect.x, stele_rect.y, stele_rect.width, stele_rect.height)
                stele_name = self.get_stele_names().get(rect_key, "stele_default")

                # Enregistrer la stèle à proximité pour afficher le message d'interaction
                self.nearby_stele = (rect_key, stele_name)
                break

    def check_entity_collisions(self):
        """Vérifie si le joueur est en collision avec des entités ennemies"""
        for entity in self.getCurrentMap().entities:
            if entity.name == "slime" and self.player.rect.colliderect(entity.damageRect):
                print("Collision avec un slime - mort du joueur")
                self.restart()  # Réinitialiser le joueur à son point de départ
                return True
        return False

    def check_projectile_collisions(self):
        """Vérifie les collisions entre les projectiles et les entités"""
        from Projectiles import damage

        # Vérifier les collisions entre les projectiles et le joueur
        for proj in damage[:]:  # Utiliser une copie de la liste pour éviter les problèmes lors de la suppression
            if not proj.friendly:  # Si c'est un projectile ennemi
                if self.player.rect.collidepoint(proj.x, proj.y):
                    print("Joueur touché par un projectile ennemi")
                    # Supprimer le projectile
                    if proj in damage:
                        damage.remove(proj)
                    # Tuer le joueur
                    self.restart()
                    return True
            else:  # Si c'est un projectile allié
                # Vérifier les collisions avec les entités ennemies
                for entity in self.getCurrentMap().entities:
                    if hasattr(entity, 'rect') and entity.rect.collidepoint(proj.x, proj.y):
                        # Supprimer le projectile
                        if proj in damage:
                            damage.remove(proj)
                        # Ici, vous pourriez ajouter une logique pour endommager l'entité
                        # Par exemple, si l'entité a un attribut health
                        # entity.health -= 10
                        break

        return False

    def light_stele(self, keys_pressed):
        # Vérifier si le joueur appuie sur la touche F et est près d'une stèle
        if self.nearby_stele and keys_pressed[pygame.K_f]:
            rect_key, stele_name = self.nearby_stele

            # Vérifier si la stèle est déjà allumée
            if not self.get_stele_lit().get(rect_key, False):
                # Extraire le type de la stèle
                stele_type = stele_name.split('_')[1] if '_' in stele_name else "default"

                # Construire le nom de la torche correspondante
                torch_name = f"torche_{stele_type}"

                # Vérifier si le joueur possède la torche correspondante
                if torch_name in self.player.items:
                    print(f"Stèle allumée: {stele_name}")

                    # Marquer la stèle comme allumée
                    self.get_stele_lit()[rect_key] = True

                    # Rendre visible la flamme correspondante si elle existe
                    if stele_name in self.get_flame_map():
                        flame_index = self.get_flame_map()[stele_name]
                        if flame_index < len(self.get_flames()):
                            self.get_flames()[flame_index]['visible'] = True
                            if stele_name == "stele_ciel":
                                self.player.add_item("sky_orb")
                            elif stele_name == "stele_aqua":
                                self.player.add_item("aqua_orb")
                            elif stele_name == "stele_lava":
                                self.player.add_item("magma_orb")
                            print(f"Flamme allumée: {self.get_flames()[flame_index]['name']}")

    # --------------------------------------/ Collisions :

    def death_colid(self):
        # Vérifier les collisions avec les zones de mort
        if self.player.rect.collidelist(self.get_death()) > -1:
            self.restart()

    def dead_colid(self):
        # Si collision avec zones dead mort déclenché à la prochaine collision
        if self.player.rect.collidelist(self.get_dead()) > -1:
            self.is_dead = True

    def entities_collisions(self):
        # Réinitialiser la liste des dommages pour éviter les rectangles fantômes
        self.damages = []

        all_entities = self.getCurrentMap().entities.copy()
        all_entities.append(self.player)

        for mob in all_entities:
            # Gestion des rectangles de dommage spécifiques à certaines entités
            if mob.name == "slime" and hasattr(mob, 'damageRect'):
                drect = (mob.damageRect, "slime")
                self.damages.append(drect)
            elif mob.name == "fantome" and hasattr(mob, 'damageRect'):
                # Ajout pour le fantôme
                drect = (mob.damageRect, "fantome")
                self.damages.append(drect)

            # Collisions avec le sol et les murs - commun à toutes les entités
            ground_rect_index = mob.rect_down.collidelist(self.get_walls())
            if ground_rect_index > -1:
                mob.colidlist[0] = 1
                mob.onground = self.get_walls()[ground_rect_index]
                if mob.name == "player" and mob.is_dead:
                    mob.restart()
                    mob.is_dead = False
            else:
                mob.colidlist[0] = 0
                mob.onground = pygame.Rect(0, 0, 0, 0)

            # Test collision plafond
            if mob.rect_up.collidelist(self.get_walls()) > -1:
                mob.colidlist[1] = 1
            else:
                mob.colidlist[1] = 0

            # Test collision gauche
            if mob.rect_left.collidelist(self.get_walls()) > -1:
                mob.colidlist[2] = 1
            else:
                mob.colidlist[2] = 0

            # Test collision droite
            if mob.rect_right.collidelist(self.get_walls()) > -1:
                mob.colidlist[3] = 1
            else:
                mob.colidlist[3] = 0

            # Gestion des collisions avec les dégâts
            drect_all = []
            for i in range(len(self.damages)):
                drect_all.append(self.damages[i][0])
            dmg_rect = mob.rect.collidelist(drect_all)
            if dmg_rect > -1:
                if mob.name == "player" and mob.name != self.damages[dmg_rect][1]:
                    self.restart()  # Réinitialiser le joueur à son point de départ
                    return True
                elif mob.name != self.damages[dmg_rect][1]:
                    self.getCurrentMap().entities.remove(mob)

            # Détecteurs pour les entités qui se déplacent (comme Slime)
            if hasattr(mob, 'detecRectDownRight') and hasattr(mob, 'detecRectDownLeft'):
                if mob.detecRectDownRight.collidelist(self.get_walls()) > -1:
                    mob.downRightColid = True
                else:
                    mob.downRightColid = False
                if mob.detecRectDownLeft.collidelist(self.get_walls()) > -1:
                    mob.downLeftColid = True
                else:
                    mob.downLeftColid = False

            if mob.name =="player":
                npc=[]
                for elem in self.getCurrentMap().npc:
                    npc.append(elem[1])
                npc_index = mob.rect.collidelist(npc)
                if npc_index > -1 :
                    if self.getCurrentMap().npc[npc_index][0] == "brizio":
                        if not mob.can_db_jump:
                            mob.add_item("brizio_orb")
                            mob.can_db_jump = True

    def way_collisions(self):
        if len(self.wRect) > 0:
            way_id = self.player.rect.collidelist(self.wRect)
            if way_id > -1:
                way = self.get_ways()[way_id][1]
                if way in self.maps:
                    self.change_map(way)
                else:
                    print("Map Introuvable")

    # ------------------------------------------------------

    def draw_entities(self):
        for mob in self.getCurrentMap().entities:
            try:
                # Convertir les coordonnées monde en coordonnées écran
                screen_pos = self.world_to_screen(mob.position)

                # Appliquer le zoom à l'image
                zoomed_width = int(mob.image.get_width() * self.get_map_layer().zoom)
                zoomed_height = int(mob.image.get_height() * self.get_map_layer().zoom)
                zoomed_image = pygame.transform.scale(mob.image, (zoomed_width, zoomed_height))

                self.screen.blit(zoomed_image, (int(screen_pos[0]), int(screen_pos[1])))

            except Exception as e:
                print(f"Erreur lors de l'affichage d'un item: {e}")

    def collisions_update(self):
        self.death_colid()
        self.dead_colid()
        self.entities_collisions()
        self.check_stele_collisions()
        self.check_item_collisions()
        # Ajouter ces lignes pour vérifier les collisions avec les entités et les projectiles
        self.check_entity_collisions()
        self.check_projectile_collisions()

    def update(self, keys_pressed=None):
        self.get_group().update()
        self.collisions_update()

        for entity in self.getCurrentMap().entities:
            if entity.name == "fantome" and hasattr(entity, 'set_player') and not entity.player:
                entity.set_player(self.player)
                print(f"Réassociation du joueur au fantôme à {entity.position}")

        # Vérifier si le joueur appuie sur F pour allumer une stèle
        if keys_pressed:
            self.light_stele(keys_pressed)

    def update_way_rects(self):
        self.wRect = []
        for elem in self.get_ways():
            self.wRect.append(elem[0])

    def restart(self):
        self.player.restart(self.spawn[0], self.spawn[1])
        if "immortal_orb" not in self.player.items:
            self.player.add_item("immortal_orb")