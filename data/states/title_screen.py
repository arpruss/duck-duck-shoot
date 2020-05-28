import os
import json

import pygame as pg

from .. import tools, prepare
from ..components.labels import Label
from ..components.animation import Animation, Task
from ..components.crosshair import Crosshair
from ..components.player import Player


def make_label(text, name):
    a = Label(text, {"midbottom": prepare.SCREEN_RECT.center},
                  font_path=prepare.FONTS["duality"], font_size=48,
                  text_color=(33, 107, 38))
    pg.image.save(a.image, "{}.png".format(name))



class Icon(pg.sprite.Sprite):
    def __init__(self, image, center, *groups):
        super(Icon, self).__init__(*groups)
        self.image = pg.Surface(image.get_size())
        self.image.fill((60, 158, 215))
        self.image.set_colorkey((60, 158, 215))
        self.image.blit(image, (0, 0))
        self.rect = self.image.get_rect(center=center)
        self.alpha = 255

    def draw(self, surface):
        surface.blit(self.image, self.rect)



class TitleScreen(tools._State):
    def __init__(self):
        super(TitleScreen, self).__init__()
        self.animations = pg.sprite.Group()
        self.icons = pg.sprite.Group()
        self.title = Icon(prepare.GFX["title"], (prepare.SCREEN_RECT.centerx, 300))
        self.title.alpha = 0
        self.make_bg()
        self.make_icons()
        self.title_pieces = ["Duck, ", "Duck, ", "Shoot"][::-1]
        self.caption = ""
        pg.mouse.set_visible(True)
        pg.mouse.set_cursor((8,8),(0,0),(0,)*8,(0,)*8)
        pg.event.set_grab(True)
        self.elapsed = 0
        task = Task(self.fade_in_title, 4000)
        task2 = Task(self.fade_out_icons, 3500)
        self.animations.add(task, task2)
        self.crosshair = Crosshair(prepare.GFX["crosshair_white_large"])
        self.persist["crosshair"] = self.crosshair
        self.load_player()
        self.persist["player"] = self.player

    def load_player(self):
        p = os.path.join("resources", "player.json")

        try:
            with open(p, "r") as f:
                player_info = json.load(f)
                self.player = Player(player_info)
        except IOError:
            self.player = Player()

    def fade_in_title(self):
        ani = Animation(alpha=255, duration=1500)
        ani.start(self.title)
        self.animations.add(ani)

    def fade_out_icons(self):
        for icon in self.icons:
            ani = Animation(alpha=0, duration=2500)
            ani.start(icon)
            ani.callback = icon.kill
            self.animations.add(ani)

    def make_bg(self):
        bg_tile = prepare.GFX["bg_blue"]
        self.bg = pg.Surface(prepare.SCREEN_SIZE)
        for x in range(0, prepare.SCREEN_SIZE[0], bg_tile.get_width()):
            for y in range(0, prepare.SCREEN_SIZE[1], bg_tile.get_height()):
                self.bg.blit(bg_tile, (x, y))

    def make_icons(self):
        self.idle_icons = [
            (Icon(prepare.GFX["duck_yellow"], (320, 300)),
                    1000, prepare.SFX["outofammo"]),
            (Icon(prepare.GFX["duck_yellow"], (640, 300)),
                    2000, prepare.SFX["load"]),
            (Icon(prepare.GFX["target_red2"], (960, 300)),
                    3000, prepare.SFX["fire"])]

    def startup(self, persistent):
        self.persist = persistent

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_e:
                self.done = True
                self.next = "EDITOR"
            else:
                self.done = True
                self.next = "MENU"
        elif event.type == pg.MOUSEBUTTONUP:
            self.done = True
            self.next = "MENU"

    def update(self, dt):
        self.animations.update(dt)
        self.elapsed += dt
        self.crosshair.update()
        for idler in self.idle_icons:
            icon, timestamp, sound = idler
            if self.elapsed >= timestamp:
                self.icons.add(icon)
                self.idle_icons.remove(idler)
                sound.play()
                if self.title_pieces:
                    self.caption += self.title_pieces.pop()
                    pg.display.set_caption(self.caption)
        for icon in self.icons:
            icon.image.set_alpha(icon.alpha)
        self.title.image.set_alpha(self.title.alpha)

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        self.title.draw(surface)
        self.icons.draw(surface)
        self.crosshair.draw(surface)
