import pygame as pg

from .. import tools, prepare
from ..components.hud import NumberLabel


class Icon(pg.sprite.Sprite):
    def __init__(self, image_name, center, *groups):
        super(Icon, self).__init__(*groups)
        image = prepare.GFX[image_name]
        self.image = pg.Surface(image.get_size())
        self.image.fill((60, 158, 215))
        self.image.set_colorkey((60, 158, 215))
        self.image.blit(image, (0, 0))
        self.rect = self.image.get_rect(center=center)
        self.alpha = 255

    def draw(self, surface):
        surface.blit(self.image, self.rect)



class HelpScreen(tools._State):
    def __init__(self):
        super(HelpScreen, self).__init__()
        self.animations = pg.sprite.Group()
        self.icons = pg.sprite.Group()
        self.make_bg()
        self.make_icons()

    def make_icons(self):
        cx = prepare.SCREEN_RECT.centerx
        target_title = Icon("text_target_values", (0 , -5), self.icons)
        target_title.rect.midtop = (cx, 0)
        controls_title = Icon("text_controls", (0, 0), self.icons)
        controls_title.rect.midtop = (330, 320)
        unlocks_title = Icon("text_unlocks", (0, 0), self.icons)
        unlocks_title.rect.midtop = (1020, 320)


        img_names = ["duck_yellow", "target_red2", "target_colored", "duck_l'orange"]
        points = [1, 5, 25, 50]
        cx, cy = 340, 150
        for name, point in zip(img_names, points):
            icon = Icon(name, (cx, cy), self.icons)
            label = NumberLabel(point, (0, 0), self.icons)
            label.rect.center = (icon.rect.centerx, 250)
            cx += 200

        mouse_cx = 120
        cy1 = 500
        cy2 = 650
        Icon("mouse", (mouse_cx, cy1), self.icons)
        Icon("mouse_arrows", (mouse_cx, cy1), self.icons)
        Icon("mouse_click", (mouse_cx, cy2), self.icons)
        Icon("text_aim", (mouse_cx + 150, cy1 - 5), self.icons)
        Icon("text_shoot2", (mouse_cx + 150, cy2 - 5), self.icons)
        keys_cx = 430
        kcy1 = 457
        kcy2 = 557
        kcy3 = 657
        Icon("button_esc", (keys_cx, kcy1), self.icons)
        Icon("button_r", (keys_cx, kcy2), self.icons)
        Icon("button_f1", (keys_cx, kcy3), self.icons)

        text = Icon("text_quit", (0, kcy1), self.icons)
        text2 = Icon("text_restart", (keys_cx + 120, kcy2), self.icons)
        text3 = Icon("text_fullscreen", (keys_cx + 120, kcy3), self.icons)

        text.rect.left = keys_cx + 80
        text2.rect.left = keys_cx + 80
        text3.rect.left = keys_cx + 80

        cx = 900
        left = 1050
        icon1 = Icon("mini_stars", (cx, 510), self.icons)
        icon2 = Icon("mini_stars", (cx, 440), self.icons)
        w, h = icon1.rect.size
        image = icon1.image.subsurface(0, 0, int(w*.8), h)
        icon2.image = image
        lev = Icon("text_next_level", (0, 440), self.icons)
        ammo = Icon("text_ammo", (0, 510), self.icons)
        lev.rect.left = left
        ammo.rect.left = left

    def make_bg(self):
        bg_tile = prepare.GFX["bg_blue"]
        self.bg = pg.Surface(prepare.SCREEN_SIZE)
        for x in range(0, prepare.SCREEN_SIZE[0], bg_tile.get_width()):
            for y in range(0, prepare.SCREEN_SIZE[1], bg_tile.get_height()):
                self.bg.blit(bg_tile, (x, y))


    def startup(self, persistent):
        self.persist = persistent
        self.crosshair = self.persist["crosshair"]

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            else:
                self.done = True
                self.next = "MENU"
        elif event.type == pg.MOUSEBUTTONUP:
            self.done = True
            self.next = "MENU"

    def update(self, dt):
        self.animations.update(dt)
        self.crosshair.update()


    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        self.icons.draw(surface)
        self.crosshair.draw(surface)
