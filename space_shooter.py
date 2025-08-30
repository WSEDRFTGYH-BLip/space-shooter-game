import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 设置游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空射击游戏")
clock = pygame.time.Clock()

# 设置字体，优先使用系统中文字体
def get_system_font():
    """获取系统可用的中文字体"""
    # 尝试常用中文字体
    preferred_fonts = ["SimHei", "Microsoft YaHei", "Heiti TC", "Arial Unicode MS"]
    available_fonts = pygame.font.get_fonts()
    
    # 检查是否有首选字体
    for font in preferred_fonts:
        if any(font.lower() in available.lower() for available in available_fonts):
            return font
    # 如果没有找到中文字体，使用默认字体
    return None

# 获取适合的字体
system_font = get_system_font()

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets):
        super().__init__()
        # 保存精灵组引用
        self.all_sprites = all_sprites
        self.bullets = bullets
        
        # 创建玩家飞船（三角形）
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 40), (50, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # 左右移动控制
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        # 射击逻辑，使用实例中保存的精灵组引用
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 创建敌人（矩形）
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 4)
        self.speed_x = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        # 超出屏幕后重新出现
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 4)

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        # 超出屏幕后删除
        if self.rect.bottom < 0:
            self.kill()

# 游戏主函数
def main():
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    # 创建玩家，并传递精灵组引用
    player = Player(all_sprites, bullets)
    all_sprites.add(player)

    # 创建敌人
    for i in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    # 使用系统字体，确保中文显示正常
    if system_font:
        font = pygame.font.SysFont(system_font, 36)
    else:
        font = pygame.font.Font(None, 36)  # 回退到默认字体
    running = True

    # 游戏主循环
    while running:
        clock.tick(FPS)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        # 更新精灵
        all_sprites.update()

        # 碰撞检测：子弹击中敌人
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        # 碰撞检测：敌人击中玩家
        hits = pygame.sprite.spritecollide(player, enemies, True)
        if hits:
            # 显示游戏结束画面
            screen.fill(BLACK)
            game_over_text = font.render("游戏结束!", True, RED)
            score_text = font.render(f"最终得分: {score}", True, WHITE)
            restart_text = font.render("按R键重新开始，按ESC退出", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 50))
            screen.blit(score_text, (WIDTH//2 - 80, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - 180, HEIGHT//2 + 50))
            
            pygame.display.flip()
            
            # 等待玩家输入
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()  # 重新开始游戏
                            return
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            waiting = False

        # 绘制
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # 显示分数
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# 启动游戏
if __name__ == "__main__":
    main()
    