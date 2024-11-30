import time
import pygame
import math
import random

# 初始化pygame
pygame.init()

class Button:
    def __init__(self, color, position, radius):
        self.color = color
        self.position = position
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def is_clicked(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        return math.sqrt((mouse_x - self.position[0]) ** 2 + (mouse_y - self.position[1]) ** 2) <= self.radius

class StartPage:
    def __init__(self, screen, background_image, button):
        self.screen = screen
        self.background_image = background_image
        self.button = button

    def draw(self):
        self.screen.blit(self.background_image, (self.screen.get_width() - self.background_image.get_width(), 0))
        self.button.draw(self.screen)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.button.is_clicked(event.pos)
        return False

class Item:
    def __init__(self, name, images):
        self.name = name
        self.images = images

class GameGrid:
    def __init__(self, screen, images, grid_size, cell_width, cell_height, horizontal_padding=10, vertical_padding=10):
        self.screen = screen
        self.images = images
        self.grid_size = grid_size  # (rows, cols)
        self.cell_width = cell_width  # 单元格宽度
        self.cell_height = cell_height  # 单元格高度
        self.horizontal_padding = horizontal_padding  # 横向间距
        self.vertical_padding = vertical_padding  # 纵向间距
        self.grid = self.create_grid()
        self.offset_x = 0

    def create_grid(self):
        grid = [[None for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]
        image_index = 0
        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                if image_index < len(self.images):
                    grid[row][col] = self.images[image_index]
                    image_index += 1
        return grid

    def draw(self, offset_x):
        self.offset_x = -offset_x
        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                image = self.grid[row][col]
                if image:
                    image_rect = image.get_rect(
                        topleft=(
                            col * (self.cell_width + self.horizontal_padding) - self.offset_x + 25,
                            row * (self.cell_height + self.vertical_padding) + 60
                        )
                    )
                    self.screen.blit(image, image_rect)

class GameBackground:
    def __init__(self, screen, background_image):
        self.screen = screen
        self.background_image = background_image
        self.position = [0, 0]
        self.dragging = False
        self.offset_x = 0

    def draw(self):
        self.screen.blit(self.background_image, self.position)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True
            self.offset_x = event.pos[0] - self.position[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.position[0] = event.pos[0] - self.offset_x
                self.limit_position()

    def limit_position(self):
        screen_width = self.screen.get_width()
        background_width = self.background_image.get_width()
        if self.position[0] > 0:
            self.position[0] = 0
        elif self.position[0] < screen_width - background_width:
            self.position[0] = screen_width - background_width

class Popup:
    def __init__(self, screen, width, height, text):
        self.screen = screen
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.fill((255, 255, 255))  # 白色背景
        self.rect = self.surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

        # 绘制游戏结束文本
        font = pygame.font.SysFont('simhei', 48)
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(width // 2, height // 2 - 30))
        self.surface.blit(text_surface, text_rect)

    def update_score(self, score):
        # 绘制总积分
        score_text = f"总积分: {score}"
        score_font = pygame.font.SysFont('simhei', 36)
        score_surface = score_font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(center=(self.width // 2, self.height // 2 + 30))
        self.surface.blit(score_surface, score_rect)

    def draw(self):
        self.screen.blit(self.surface, self.rect)

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = time.time()

    def get_remaining_time(self):
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, self.duration - elapsed_time)
        return remaining_time

    def is_finished(self):
        return self.get_remaining_time() <= 0

class Game:
    def __init__(self):
        # 设置窗口大小和标题
        self.screen_width = 1300
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("独具慧眼")

        # 加载开始页面背景图像
        self.background_startimage = pygame.image.load('img/bg_game.png')

        # 设置跳转按钮
        self.button_color = (0, 255, 0)
        self.button_radius = 50
        self.button_position = (self.screen_width - self.button_radius - 20, self.screen_height - self.button_radius - 20)
        self.button = Button(self.button_color, self.button_position, self.button_radius)

        # 加载游戏背景图像
        self.background_gameimage = pygame.image.load('img/bg_game.png')

        # 初始化页面和背景
        self.start_page = StartPage(self.screen, self.background_startimage, self.button)
        self.game_background = GameBackground(self.screen, self.background_gameimage)

        # 初始化弹窗
        self.popup = Popup(self.screen, 300, 200, "游戏结束")

        # 初始化计时器
        self.timer = Timer(10)  # 设置倒计时为120秒

        # 初始化物品
        self.items = self.load_images()
        # 创建一个所有图片的平铺列表
        self.all_images = [image for item in self.items for image in item.images]
        # 初始化游戏网格
        self.game_grid = GameGrid(self.screen, self.all_images, (4, 12), cell_width=130, cell_height=130,
                                  horizontal_padding=40, vertical_padding=20)

        # 主循环控制变量
        self.running = True
        self.start_page_active = True
        self.game_over = False

        # 初始化任务
        self.current_task, self.current_task_count = self.generate_task()

        # 初始化积分
        self.score = 0

    def load_images(self):
        # 加载物品图片
        item_images = {
            '风筝': [pygame.image.load(f'img/test/fengzheng ({i}).png') for i in range(1, 5)],
            '勺子': [pygame.image.load(f'img/test/shaozi ({i}).png') for i in range(1, 38)],
            '筷子': [pygame.image.load(f'img/test/kuaizi ({i}).png') for i in range(1, 12)],
            '花瓶': [pygame.image.load(f'img/test/huapin ({i}).png') for i in range(1, 15)],
            # 添加更多物品
        }
        items = []
        for name, image_list in item_images.items():
            scaled_images = [pygame.transform.scale(image, (130, 130)) for image in image_list]
            item = Item(name, scaled_images)
            items.append(item)
        return items

    def generate_task(self):
        # 随机生成任务
        item = random.choice(self.items)
        count = random.randint(1, 5)
        return item, count

    def draw_task(self):
        # 绘制任务提示
        task_text = f"{self.current_task.name} × {self.current_task_count}"
        task_font = pygame.font.SysFont('simhei', 20)
        task_surface = task_font.render(task_text, True, (255, 255, 255))
        self.screen.blit(task_surface, (580, 10))

    def draw_score(self):
        # 绘制积分
        score_text = f"得分：{self.score}"
        score_font = pygame.font.SysFont('simhei', 20)
        score_surface = score_font.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (580, 35))

    def handle_click(self, mouse_pos):
        if not self.game_over:
            # 获得背景偏移量
            offset_x = self.game_background.position[0]
            # 将鼠标位置转换到背景的坐标系中
            adjusted_mouse_pos = (mouse_pos[0] - offset_x, mouse_pos[1])
            # 遍历网格中的图片，检查调整后的鼠标位置是否在图片矩形内
            for row in range(self.game_grid.grid_size[0]):
                for col in range(self.game_grid.grid_size[1]):
                    image = self.game_grid.grid[row][col]
                    if image:
                        image_rect = image.get_rect(
                            topleft=(col * (self.game_grid.cell_width + self.game_grid.horizontal_padding) + 25,
                                     row * (self.game_grid.cell_height + self.game_grid.vertical_padding) + 60)
                        )
                        if image_rect.collidepoint(adjusted_mouse_pos):
                            if image in self.current_task.images:
                                self.generate_new_image(row, col)
                                self.current_task_count -= 1
                                self.score += 10
                                if self.current_task_count <= 0:
                                    self.current_task, self.current_task_count = self.generate_task()
                                return

    def generate_new_image(self, row, col):
        # 随机生成新的图片
        item = random.choice(self.items)
        new_image = random.choice(item.images)
        self.game_grid.grid[row][col] = new_image

    def reset_game(self):
        # 重置游戏状态
        self.game_over = False
        self.score = 0
        self.current_task, self.current_task_count = self.generate_task()
        self.game_grid.grid = self.game_grid.create_grid()
        self.timer = Timer(120)

    def run(self):
        while self.running:
            if self.start_page_active:
                self.start_page.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif self.start_page.handle_events(event):
                        self.start_page_active = False
                        self.timer.start_time = time.time()
            else:
                self.game_background.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.game_background.handle_events(event)

                    # 处理点击事件
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.handle_click(event.pos)

                    # 处理游戏结束弹窗的点击事件
                    if self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.start_page_active = True
                            self.reset_game()

                # 倒计时
                if not self.game_over:
                    remaining_time = self.timer.get_remaining_time()
                    minutes = int(remaining_time // 60)
                    seconds = int(remaining_time % 60)
                    time_text = f"{minutes:02}:{seconds:02}"
                    time_font = pygame.font.Font(None, 36)
                    time_surface = time_font.render(time_text, True, (255, 255, 255))
                    self.screen.blit(time_surface, (self.screen_width - 100, 10))

                    # 检查倒计时是否结束
                    if self.timer.is_finished():
                        self.game_over = True
                        self.popup.update_score(self.score)  # 更新弹窗的积分

                # 绘制任务提示
                self.draw_task()
                # 绘制积分
                self.draw_score()
                # 绘制游戏网格
                self.game_grid.draw(self.game_background.position[0])
                # 绘制游戏结束弹窗
                if self.game_over:
                    self.popup.draw()

            # 更新屏幕
            pygame.display.flip()

# 创建游戏对象并运行
game = Game()
game.run()