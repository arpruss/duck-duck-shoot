import pygame as pg

from .. import tools, prepare
from ..components.animation import Animation, Task
from ..components.hud import Icon, NumberLabel, MaskedButton


class CountUp(tools._State):
    def __init__(self):
        super(CountUp, self).__init__()

    def startup(self, persistent):
        self.persist = persistent
        self.level = self.persist["level"]
        self.curtains = self.persist["curtains"]
        self.hud = self.persist["hud"]
        self.player = self.persist["player"]
        self.animations = pg.sprite.Group()

        self.hud.start_count_up()
        self.curtains.close()
        self.make_score_icon()

        self.replay_button = MaskedButton(prepare.GFX["replay_button"],
                                                        (460, 560), self.replay, [])
        self.play_button = MaskedButton(prepare.GFX["forward_button"],
                                                      (820, 560), self.next_level, [])
        self.replay_button.visible = False
        self.play_button.visible = False

    def to_level_start(self):
        self.player.save()
        self.done = True
        self.next = "LEVEL_START"

    def replay(self):
        ani = Task(self.to_level_start, 250)
        self.animations.add(ani)

    def next_level(self):
        self.player.info["level"] += 1
        task = Task(self.to_level_start, 250)
        self.animations.add(task)

    def make_score_icon(self):
        cx = prepare.SCREEN_RECT.centerx
        self.score_icon = Icon(prepare.GFX["text_score"], (0, 0))
        self.score_icon.rect.center = cx, -700
        self.score_label = NumberLabel(self.hud.score, (0, 0))
        self.score_label.rect.center = cx, -620
        self.score_centerx, self.score_centery = self.score_label.rect.center
        delay = 1000
        ani = Animation(centery=100, duration=2000, delay=delay,
                               round_values=True, transition="out_bounce")
        ani.start(self.score_icon.rect)
        ani2 = Animation(score_centery=180, duration=2000, delay=delay,
                                 round_values=True, transition="out_bounce")
        ani2.start(self)
        self.animations.add(ani, ani2)

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.replay_button.get_event(event)
        self.play_button.get_event(event)

    def update(self, dt):
        self.animations.update(dt)
        self.level.update(dt)
        self.curtains.update(dt)
        self.hud.update(dt, self.level.gun)
        center = self.score_label.rect.center
        self.score_label = NumberLabel(self.hud.score, (0, 0))
        self.score_label.rect.center = self.score_centerx, self.score_centery
        self.replay_button.update(dt, (self.level.crosshair.rect.center))
        self.play_button.update(dt, (self.level.crosshair.rect.center))
        if self.hud.replay_ready:
            self.replay_button.visible = True
            if self.hud.player_advance:
                self.play_button.visible = True

    def draw(self, surface):
        self.level.draw(surface)
        self.curtains.draw(surface)
        self.hud.draw(surface)
        self.score_icon.draw(surface)
        self.score_label.draw(surface)
        self.replay_button.draw(surface)
        self.play_button.draw(surface)
        self.level.crosshair.draw(surface)