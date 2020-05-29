import pygame as pg

from .. import prepare

class Gun(object):
    def __init__(self, crosshair, max_bullets):
        self.fire_sound = prepare.SFX["fire"]
        self.click_sound = prepare.SFX["outofammo"]
        self.reload_sound = prepare.SFX["load"]

        self.bullets = self.max_bullets = max_bullets
        self.crosshair = crosshair
        self.kill_counter = {"duck": 0, "bullseye": 0,
                                   "colored bullseye": 0, "orange duck": 0}

    def get_event(self, event, targets, rows, all_sprites):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.crosshair.rect.center = event.pos
                self.shoot(targets, rows, all_sprites)
            else:
                self.reload()
        elif event.type == pg.MOUSEMOTION:
            if event.pos[0] < 16 or event.pos[0] > prepare.SCREEN_SIZE[0] - 16 or event.pos[1] < 16 or event.pos[1] > prepare.SCREEN_SIZE[1] - 16:
                self.reload()

    def reload(self):
        if self.bullets < self.max_bullets:
            self.bullets = self.max_bullets
            self.reload_sound.play()

    def shoot(self, targets, rows, all_sprites):
        cr = self.crosshair.rect
        if cr.left < 64 or cr.right > prepare.SCREEN_SIZE[0] - 64 or cr.top < 16 or cr.bottom > prepare.SCREEN_SIZE[1] - 16:
            self.reload()
        else:
            if self.bullets > 0:
                self.fire_sound.play()
                self.bullets -= 1
                self.check_collisions(targets, rows, all_sprites)
            else:
                self.click_sound.play()

    def check_collisions(self, targets, rows, all_sprites):
        for row in rows:
            if row.bg.rect.collidepoint(self.crosshair.rect.center):
                mask = pg.mask.from_surface(row.bg.image)
                x = self.crosshair.rect.centerx - row.bg.rect.left
                y = self.crosshair.rect.centery - row.bg.rect.top
                if mask.get_at((x, y)):
                    return

            for target in row.targets:
                if target.rect.collidepoint(self.crosshair.rect.center):
                    dx = self.crosshair.rect.centerx - target.rect.left
                    dy = self.crosshair.rect.centery - target.rect.top
                    try:
                        if target.target_mask.get_at((dx, dy)):
                            target.score(all_sprites)
                            self.kill_counter[target.target_type] += 1
                            return
                    except IndexError:
                        pass
