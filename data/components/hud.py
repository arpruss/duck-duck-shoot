import pygame as pg

from .. import prepare
from ..components.animation import Task, Animation
from ..components.target import POINT_VALUES


class BulletBar(object):
    def __init__(self, topright, max_bullets):
        self.empty_img = prepare.GFX["icon_bullet_empty_long"]
        self.full_img = prepare.GFX["icon_bullet_silver_long"]
        self.max_bullets = max_bullets
        self.make_images()
        self.image = self.images[self.max_bullets]
        self.rect = self.image.get_rect(topright=topright)

    def make_images(self):
        gap = 4
        vert_gap = 2
        self.images = {}
        w, h = self.full_img.get_size()
        num = min(self.max_bullets, 5)
        total_w = num * w
        total_w += (num - 1) * gap
        num_rows, rem = divmod(self.max_bullets, 5)
        if rem:
            num_rows += 1
        total_h = num_rows * (h + vert_gap)
        base_img = pg.Surface((total_w, total_h)) #.convert_alpha()
        base_img.set_colorkey(pg.Color("black"))
        #base_img.fill((0,0,0,0))
        left = 0
        top = 0
        for x in range(self.max_bullets):
            base_img.blit(self.empty_img, (left, top))
            left += gap + w
            if left > total_w - w:
                left = 0
                top += h + vert_gap
        self.images[0] = base_img.copy()
        
        left2 = 0
        top2 = 0
        for x in range(self.max_bullets):
            base_img.blit(self.full_img, (left2, top2))
            self.images[x + 1] = base_img.copy()
            left2 += w + gap
            if left2 > total_w - w:
                left2 = 0
                top2 += h + vert_gap

    def update(self, gun):
        self.image = self.images[gun.bullets]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Icon(pg.sprite.Sprite):
    def __init__(self, image, topleft, *groups):
        super(Icon, self).__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=topleft)

    def update(self, dt):
        pass
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class BlinkingIcon(Icon):
    def __init__(self, image, topleft, frequency, *groups):
        super(BlinkingIcon, self).__init__(image, topleft, *groups)
        self.base = self.image.copy()
        self.blank = self.image.copy()
        self.blank.fill((0,0,0,0))
        self.frequency = frequency
        self.timer = 0
        self.visible = True
        self.active = False
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.frequency:
            self.timer -= self.frequency
            self.visible = not self.visible
        if self.visible and self.active:
            self.image = self.base
        else:
            self.image = self.blank
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

        
class MaskedButton(pg.sprite.Sprite):
    inflate_time = 120
    deflate_time = 120
    
    def __init__(self, image, centerpoint, size, callback, *groups):
        super(MaskedButton, self).__init__(*groups)
        self.base_image = pg.Surface((size, size)).convert_alpha()
        self.base_rect = self.base_image.get_rect(center=centerpoint)
        img = image
        img_rect = img.get_rect(center=(size//2, size//2))
        self.base_image.fill((0,0,0,0))
        self.base_image.blit(img, img_rect)
        self.size = self.initial_size = size
        self.make_images()
        self.hovered = False
        self.animations = pg.sprite.Group()
        self.held = False
        self.units_per_click = 1
        self.clicked = False
        self.call = callback
        self.visible = True
        
    def mask_point_collide(self, pos):
        dx = pos[0] - self.rect.left
        dy = pos[1] - self.rect.top
        try:
            return self.mask.get_at((dx, dy))
        except IndexError:
            return False
            
    def make_images(self):
        self.images, self.rects, self.masks = {}, {}, {}
        self.low = int(self.size * .95)
        self.high = int(self.size * 1.1)
        for x in range(int(self.low * .4), int(self.high * 1.6)):
            img = pg.transform.smoothscale(self.base_image, (x, x))
            rect = img.get_rect(center=self.base_rect.center)
            mask = pg.mask.from_surface(img, 0)
            self.images[x] = img
            self.rects[x] = rect
            self.masks[x] = mask

    def get_event(self, event):
        if not self.visible:
            return
        if event.type == pg.MOUSEBUTTONDOWN:
            pass
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1 and self.hovered:
                self.clicked = True

    def update(self, dt, mouse_pos):
        self.animations.update(dt)
        hover = self.hovered
        size = int(self.size)
        self.image = self.images[size]
        self.mask = self.masks[size]
        self.rect = self.rects[size]
        self.hovered = self.mask_point_collide(mouse_pos)
        held = pg.mouse.get_pressed()[0]
        if not held and self.held:
            self.held = False
            if self.hovered:
                self.inflate(self.high)
            else:
                self.inflate(self.initial_size)
        elif self.hovered and held and not self.held:
            self.inflate(self.low)
            self.held = True
        elif not hover and self.hovered:
            self.inflate(self.high)
        elif hover and not self.hovered:
            self.inflate(self.initial_size)
        elif not self.hovered and self.held:
            self.held = False
            self.inflate(self.initial_size)
        if self.clicked:
            self.call()
        self.clicked = False
        
    def inflate(self, target):
        self.animations.empty()
        dur = self.inflate_time
        ani = Animation(size=target, duration=dur, transition="out_elastic")
        ani.start(self)
        self.animations.add(ani)
        
    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect)

        
class ReloadNotification(pg.sprite.Sprite):
    def __init__(self, *groups):
        super(ReloadNotification, self).__init__(*groups)
        self.icons = pg.sprite.Group()
        img = prepare.GFX["arrow"]
        w = img.get_width()
        space = 5
        vert_offset = 30
        left = Icon(prepare.GFX["reload"], (39, 256), self.icons)
        BlinkingIcon(img, (left.rect.x - (w + space), left.rect.top + vert_offset), 500, self.icons)
        right = Icon(prepare.GFX["reload"], (1200, 256), self.icons)
        BlinkingIcon(pg.transform.flip(img, True, False),
                         (right.rect.right + space, right.rect.top + vert_offset), 500, self.icons)
        
    def update(self, dt, bullets):
        self.icons.update(dt)
        self.active = not bullets
        for icon in self.icons:
            icon.active = self.active
        
    def draw(self, surface):
        if self.active:
            self.icons.draw(surface)
        

class Counter(pg.sprite.Sprite):
    def __init__(self, icon_img, topleft, value, *groups):
        super(Counter, self).__init__(*groups)
        self.value = None
        self.icon = Icon(icon_img, topleft)
        self.update(value)
        self.num_left, self.num_top = self.icon.rect.right + 5, self.icon.rect.top + 8
        self.done = False

    def get_width(self):
        return self.number_label.rect.right - self.icon.rect.left

    def update(self, value):
        self.num_left, self.num_top = self.icon.rect.right + 5, self.icon.rect.top + 8
        if self.value != value:
            self.value = value
            if self.value < 0:
                self.value = 0
            self.number_label = NumberLabel(self.value, (self.num_left, self.num_top))
        self.number_label.rect.topleft = self.num_left, self.num_top

    def draw(self, surface):
        if self.done:
            return
        self.icon.draw(surface)
        self.number_label.draw(surface)


class NumberLabel(pg.sprite.Sprite):
    def __init__(self, num, topleft, *groups):
        super(NumberLabel, self).__init__(*groups)
        tiles = []
        for c in str(num):
            tiles.append(prepare.GFX["text_{}".format(c)])
        total_w = sum((t.get_width() for t in tiles))
        h = tiles[0].get_height()
        self.image = pg.Surface((total_w, h)).convert_alpha()
        self.image.fill((0,0,0,0))
        x = 0
        for t in tiles:
            self.image.blit(t, (x, 0))
            x += t.get_width()
        self.rect = self.image.get_rect(topleft=topleft)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        
class StarStrip(pg.sprite.Sprite):
    bg_color = (222, 102, 23)
    def __init__(self, center, *groups):
        super(StarStrip, self).__init__(*groups)
        self.star_img = prepare.GFX["star"].copy()
        self.star_img.blit(prepare.GFX["star_outline"], (0, 0))
        self.empty_img = prepare.GFX["star_empty"].copy()
        self.empty_img.blit(prepare.GFX["star_outline_empty"], (0, 0))
        self.gap = 16
        
        self.make_base_image()
        self.make_image(0)
        self.rect = self.image.get_rect(center=center)
        self.active = False
        self.alpha = 0

    def make_base_image(self):
        w, h =  self.star_img.get_size()
        total_w = (w * 5) + (self.gap * 4)
        strip = pg.Surface((total_w, h))
        strip.fill(self.bg_color)
        strip.set_colorkey(self.bg_color)
        for x in range(5):
            strip.blit(self.empty_img, (x * (w + self.gap), 0))
        self.base_image = strip

    def make_image(self, num_stars):
        self.image = self.base_image.copy()
        for x in range(num_stars):
            self.image.blit(self.star_img, (x * (self.star_img.get_width() + self.gap), 0))
    
    def update(self):
        self.image.set_alpha(self.alpha)
        
    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


class HUD(object):
    def __init__(self, level):
        self.level = level
        self.animations = pg.sprite.Group()
        self.bullet_bar = BulletBar(prepare.SCREEN_RECT.topright, level.gun.max_bullets)
        self.counters = pg.sprite.Group()
        self.duck_counter = Counter(prepare.GFX["duck_counter"], (0, -5), 0, self.counters)
        self.bullseye_counter = Counter(prepare.GFX["bullseye_counter"], (0, 64), 0, self.counters)
        self.colored_bull_counter = Counter(prepare.GFX["colored_bull_counter"], (0, 143), 0, self.counters)
        self.orange_duck_counter = Counter(prepare.GFX["orange_duck_counter"], (0, 212), 0, self.counters)
        self.star_strip = StarStrip((prepare.SCREEN_RECT.centerx, 320))
        self.reload_notification = ReloadNotification()
        self.replay_ready = False
        self.score = 0

    def start_count_up(self):
        delay = 3000
        send_time = 600
        counters = (self.duck_counter, self.bullseye_counter, self.colored_bull_counter, self.orange_duck_counter)
        target_types = ("duck", "bullseye", "colored bullseye", "orange duck")
        for counter, target_type in zip(counters, target_types):
            t = Task(self.send_counter, args=(counter, send_time, delay))
            delay += send_time + 250
            num = self.level.gun.kill_counter[target_type]
            count_delay = 100
            for x in range(num):
                t2 = Task(self.count_target, delay, args=(target_type,))
                delay += count_delay
                count_delay -= 4
                if count_delay < 15:
                    count_delay = 15
                self.animations.add(t2)
            t3 = Task(self.kill_counter, delay, args=(counter,))
            self.animations.add(t, t3)

    def send_counter(self, counter, duration, delay):
        w = counter.get_width()
        new_left = prepare.SCREEN_RECT.centerx - (w//2)
        new_top = prepare.SCREEN_RECT.centery - 64
        ani = Animation(left=new_left, top=new_top, duration=duration, delay=delay, round_values=True) #, transition="out_quart")
        ani.start(counter.icon.rect)
        self.animations.add(ani)
        
    def count_targets(self, target_type, delay, count_delay=150):
        num = self.level.gun.kill_counter[target_type]        
        t = Task(self.count_target, delay + count_delay, num, args=(target_type,))
        self.animations.add(t)
    
    def count_target(self, target_type):
        if self.level.gun.kill_counter[target_type] > 0:
            self.level.gun.kill_counter[target_type] -= 1
            self.score += POINT_VALUES[target_type]
            prepare.SFX["switch24"].play()

    def kill_counter(self, counter):
        counter.done = True
        
    def calc_stars(self):
        percent = self.score / float(self.level.max_score)
        num_stars = percent / .2
        return  percent, num_stars

    def replay(self):
        self.replay_ready = True
        
    def fill_stars(self):
        delay = 500
        freq = 750
        ani = Animation(alpha=255, duration=250)
        ani.start(self.star_strip)
        self.animations.add(ani)
        score, num_stars = self.calc_stars()
        if score > 1:
            print "MARKSMANSHIP"
            score = 1
        if num_stars > 5:
            num_stars = 5
        for x in range(1, int(num_stars) + 1):
            t = Task(self.star_strip.make_image, delay, args=(x,))
            t2 = Task(prepare.SFX["bb-hit2"].play, delay)
            delay += freq - (100 * x)
            self.animations.add(t, t2)
        replay = Task(self.replay, delay + 500)
        level = self.level.player.info["level"]
        if level in self.level.player.info["stars"]:
            if self.level.player.info["stars"][level] < num_stars:
                self.level.player.info["stars"][level] = num_stars
                if num_stars == 5:
                    self.pre_add_bullet(delay)
        else:
            self.level.player.info["stars"][level] = num_stars
            if num_stars == 5:
                self.pre_add_bullet(delay)
        self.animations.add(replay)        

    def pre_add_bullet(self, delay):
        ani = Animation(alpha=0, duration=5000, delay=delay)
        ani.start(self.star_strip)
        ani.callback = self.add_bullet
        self.animations.add(ani)
        
    def add_bullet(self):
        self.level.player.info["max bullets"] += 1
        self.level.gun.max_bullets += 1
        self.level.gun.bullets = self.level.gun.max_bullets
        self.bullet_bar = BulletBar(prepare.SCREEN_RECT.topright, self.level.gun.max_bullets)      
        
    def update(self, dt, gun):
        self.animations.update(dt)
        self.bullet_bar.update(gun)
        kills = gun.kill_counter
        self.duck_counter.update(kills["duck"])
        self.bullseye_counter.update(kills["bullseye"])
        self.colored_bull_counter.update(kills["colored bullseye"])
        self.orange_duck_counter.update(kills["orange duck"])
        self.star_strip.update()
        self.reload_notification.update(dt, gun.bullets)
        if not self.star_strip.active:
            if all((counter.done for counter in self.counters)):
                self.star_strip.active = True
                self.fill_stars()
        
    def draw(self, surface):
        self.bullet_bar.draw(surface)
        self.duck_counter.draw(surface)
        self.bullseye_counter.draw(surface)
        self.colored_bull_counter.draw(surface)
        self.orange_duck_counter.draw(surface)
        self.reload_notification.draw(surface)
        self.star_strip.draw(surface)

