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
    def __init__(self, screen, background_image, button, last_score=0):
        self.screen = screen
        self.background_image = background_image
        self.button = button
        self.last_score = last_score
        self.rule_image = pygame.image.load('img/museumgamemainview.png')

    def draw(self):
        font = pygame.font.SysFont('simhei', 20)
        rule_text = "找到指定物品，越多得分越高"
        rule_surface = font.render(rule_text, True, ('#05668D'))
        example_text = "例如  勺子 × 2"
        example_surface = font.render(example_text, True, ('#05668D'))
        extra_rule_text1 = "规定时间内找到指定的物品越多，积分越高。"
        extra_rule_text2 = "提示：找到正确物品可加时，找到错误物品则会扣时哦。"
        extra_rule_surface1 = font.render(extra_rule_text1, True, (255,255,255))
        extra_rule_surface2 = font.render(extra_rule_text2, True, (255,255,255))
        last_score_text = f"上局得分：{self.last_score}"
        last_score_surface = font.render(last_score_text, True, (255, 255, 255))

        rule_image_rect = self.rule_image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(self.background_image, (self.screen.get_width() - self.background_image.get_width(), 0))
        self.screen.blit(self.rule_image, rule_image_rect)
        self.screen.blit(rule_surface, (500, 210))
        self.screen.blit(example_surface, (550, 250))
        self.screen.blit(extra_rule_surface1, (10, 650))
        self.screen.blit(extra_rule_surface2, (10, 680))
        self.screen.blit(last_score_surface, (50, 50))
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
    def __init__(self, screen, images_with_names, grid_size, cell_width, cell_height, horizontal_padding=10, vertical_padding=10):
        self.screen = screen
        self.images_with_names = images_with_names
        self.grid_size = grid_size
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.horizontal_padding = horizontal_padding
        self.vertical_padding = vertical_padding
        self.grid = self.create_grid()
        self.offset_x = 0

    def create_grid(self):
        grid = [[None for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]
        random.shuffle(self.images_with_names)
        image_index = 0
        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                if image_index < len(self.images_with_names):
                    grid[row][col] = self.images_with_names[image_index]
                    image_index += 1
        return grid

    def count_items(self):
        item_counts = {}
        for row in self.grid:
            for image, item_name in row:
                if item_name in item_counts:
                    item_counts[item_name] += 1
                else:
                    item_counts[item_name] = 1
        return item_counts

    def draw(self, offset_x):
        self.offset_x = -offset_x
        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                image_tuple = self.grid[row][col]
                if image_tuple:
                    image_surface, item_name = image_tuple
                    image_rect = image_surface.get_rect(
                        topleft=(
                            col * (self.cell_width + self.horizontal_padding) - self.offset_x + 25,
                            row * (self.cell_height + self.vertical_padding) + 60
                        )
                    )
                    self.screen.blit(image_surface, image_rect)

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
        # 初始化积分
        self.last_score = 0
        self.score = 0
        # 初始化页面和背景
        self.start_page = StartPage(self.screen, self.background_startimage, self.button, self.last_score)
        self.game_background = GameBackground(self.screen, self.background_gameimage)

        # 初始化弹窗
        self.popup = Popup(self.screen, 300, 200, "游戏结束")

        # 初始化计时器
        self.timer_duration = 120  # 基础倒计时
        self.timer_extra = 0  # 额外增加或减少的时间
        self.start_time = None  # 设置倒计时为120秒

        # 初始化物品
        self.items = self.load_images()
        # 创建一个所有图片的平铺列表，包含图片和物品名称
        self.all_images_with_names = [(image, item.name) for item in self.items for image in item.images]
        # 初始化游戏网格
        self.game_grid = GameGrid(self.screen, self.all_images_with_names, (4, 12), cell_width=130, cell_height=130,
                                  horizontal_padding=40, vertical_padding=20)

        # 主循环控制变量
        self.running = True
        self.start_page_active = True
        self.game_over = False

        # 初始化任务
        self.current_task, self.current_task_count = self.generate_task()



    def load_images(self):
        # 加载物品图片
        item_images = {
            '包子': [pygame.image.load(f'img/test/baozi ({i}).png') for i in range(1, 3)],
            '笔': [pygame.image.load(f'img/test/bi ({i}).png') for i in range(1, 6)],
            '布艺沙发': [pygame.image.load(f'img/test/buyishafa ({i}).png') for i in range(1, 2)],
            '博古架': [pygame.image.load(f'img/test/bogujia ({i}).png') for i in range(1, 5)],
            '车': [pygame.image.load(f'img/test/che ({i}).png') for i in range(1, 3)],
            '床': [pygame.image.load(f'img/test/chuang ({i}).png') for i in range(1, 5)],
            '窗棂': [pygame.image.load(f'img/test/chuangling ({i}).png') for i in range(1, 4)],
            '刀剑': [pygame.image.load(f'img/test/daojian ({i}).png') for i in range(1, 3)],
            '凳子': [pygame.image.load(f'img/test/dengzi ({i}).png') for i in range(1, 4)],
            '吊坠': [pygame.image.load(f'img/test/diaozhui ({i}).png') for i in range(1, 3)],
            '地毯': [pygame.image.load(f'img/test/ditan ({i}).png') for i in range(1, 4)],
            '地图': [pygame.image.load(f'img/test/ditu ({i}).png') for i in range(1, 3)],
            '风筝': [pygame.image.load(f'img/test/fengzheng ({i}).png') for i in range(1, 5)],
            '福袋': [pygame.image.load(f'img/test/fudai ({i}).png') for i in range(1, 5)],
            '鼓': [pygame.image.load(f'img/test/gu ({i}).png') for i in range(1, 4)],
            '柜子': [pygame.image.load(f'img/test/guizi ({i}).png') for i in range(1, 3)],
            '锅灶': [pygame.image.load(f'img/test/guozao ({i}).png') for i in range(1, 5)],
            '荷花灯': [pygame.image.load(f'img/test/hehuadeng ({i}).png') for i in range(1, 4)],
            '花': [pygame.image.load(f'img/test/hua ({i}).png') for i in range(1, 8)],
            '花架子': [pygame.image.load(f'img/test/huajiazi ({i}).png') for i in range(1, 2)],
            '花瓶': [pygame.image.load(f'img/test/huaping ({i}).png') for i in range(1, 7)],
            '话筒': [pygame.image.load(f'img/test/huatong ({i}).png') for i in range(1, 2)],
            '徽章': [pygame.image.load(f'img/test/huizhang ({i}).png') for i in range(1, 9)],
            '货币': [pygame.image.load(f'img/test/huobi ({i}).png') for i in range(1, 4)],
            '火锅': [pygame.image.load(f'img/test/huoguo ({i}).png') for i in range(1, 3)],
            '坚果': [pygame.image.load(f'img/test/jianguo ({i}).png') for i in range(1, 11)],
            '箭筒': [pygame.image.load(f'img/test/jiantong ({i}).png') for i in range(1, 5)],
            '轿辇': [pygame.image.load(f'img/test/jiaonian ({i}).png') for i in range(1, 2)],
            '戒指': [pygame.image.load(f'img/test/jiezhi ({i}).png') for i in range(1, 2)],
            '镜子': [pygame.image.load(f'img/test/jingzi ({i}).png') for i in range(1, 3)],
            '锦囊': [pygame.image.load(f'img/test/jinnang ({i}).png') for i in range(1, 5)],
            '酒': [pygame.image.load(f'img/test/jiu ({i}).png') for i in range(1, 6)],
            '酒杯': [pygame.image.load(f'img/test/jiubei ({i}).png') for i in range(1, 9)],
            '酒壶': [pygame.image.load(f'img/test/jiuhu ({i}).png') for i in range(1, 4)],
            '卷轴': [pygame.image.load(f'img/test/juanzhou ({i}).png') for i in range(1, 5)],
            '筷子': [pygame.image.load(f'img/test/kuaizi ({i}).png') for i in range(1, 8)],
            '令牌': [pygame.image.load(f'img/test/lingpai ({i}).png') for i in range(1, 3)],
            '马': [pygame.image.load(f'img/test/ma ({i}).png') for i in range(1, 3)],
            '猫': [pygame.image.load(f'img/test/mao ({i}).png') for i in range(1, 6)],
            '门票': [pygame.image.load(f'img/test/menpiao ({i}).png') for i in range(1, 6)],
            '墨块': [pygame.image.load(f'img/test/mokuai ({i}).png') for i in range(1, 2)],
            '木盒': [pygame.image.load(f'img/test/muhe ({i}).png') for i in range(1, 5)],
            '木椅': [pygame.image.load(f'img/test/muyi ({i}).png') for i in range(1, 5)],
            '木桌': [pygame.image.load(f'img/test/muzhuo ({i}).png') for i in range(1, 4)],
            '鸟': [pygame.image.load(f'img/test/niao ({i}).png') for i in range(1, 8)],
            '盆栽': [pygame.image.load(f'img/test/penzai ({i}).png') for i in range(1, 6)],
            '屏风': [pygame.image.load(f'img/test/pingfeng ({i}).png') for i in range(1, 6)],
            '桥': [pygame.image.load(f'img/test/qiao ({i}).png') for i in range(1, 3)],
            '琴': [pygame.image.load(f'img/test/qin ({i}).png') for i in range(1, 8)],
            '棋盘': [pygame.image.load(f'img/test/qipan ({i}).png') for i in range(1, 3)],
            '棋子': [pygame.image.load(f'img/test/qizi ({i}).png') for i in range(1, 3)],
            '伞': [pygame.image.load(f'img/test/san ({i}).png') for i in range(1, 2)],
            '珊瑚': [pygame.image.load(f'img/test/shanhu ({i}).png') for i in range(1, 3)],
            '扇子': [pygame.image.load(f'img/test/shanzi ({i}).png') for i in range(1, 3)],
            '勺子': [pygame.image.load(f'img/test/shaozi ({i}).png') for i in range(1, 14)],
            '食盒': [pygame.image.load(f'img/test/shihe ({i}).png') for i in range(1, 5)],
            '手环': [pygame.image.load(f'img/test/shouhuan ({i}).png') for i in range(1, 2)],
            '首饰': [pygame.image.load(f'img/test/shoushi ({i}).png') for i in range(1, 7)],
            '树': [pygame.image.load(f'img/test/shu ({i}).png') for i in range(1, 4)],
            '书本': [pygame.image.load(f'img/test/shuben ({i}).png') for i in range(1, 7)],
            '梳子': [pygame.image.load(f'img/test/shuzi ({i}).png') for i in range(1, 4)],
            '躺椅': [pygame.image.load(f'img/test/tangyi ({i}).png') for i in range(1, 5)],
            '天鹅': [pygame.image.load(f'img/test/tiane ({i}).png') for i in range(1, 5)],
            '调料': [pygame.image.load(f'img/test/tiaoliao ({i}).png') for i in range(1, 2)],
            '提灯': [pygame.image.load(f'img/test/tideng ({i}).png') for i in range(1, 4)],
            '碗': [pygame.image.load(f'img/test/wan ({i}).png') for i in range(1, 5)],
            '香炉': [pygame.image.load(f'img/test/xianglu ({i}).png') for i in range(1, 4)],
            '鞋': [pygame.image.load(f'img/test/xie ({i}).png') for i in range(1, 3)],
            '砚台': [pygame.image.load(f'img/test/yantai ({i}).png') for i in range(1, 3)],
            '药': [pygame.image.load(f'img/test/yao ({i}).png') for i in range(1, 2)],
            '药材': [pygame.image.load(f'img/test/yaocai ({i}).png') for i in range(1, 6)],
            '邀请函': [pygame.image.load(f'img/test/yaoqinghan ({i}).png') for i in range(1, 6)],
            '衣服': [pygame.image.load(f'img/test/yifu ({i}).png') for i in range(1, 3)],
            '印章': [pygame.image.load(f'img/test/yinzhang ({i}).png') for i in range(1, 2)],
            '衣物架': [pygame.image.load(f'img/test/yiwujia ({i}).png') for i in range(1, 4)],
            '鱼': [pygame.image.load(f'img/test/yu ({i}).png') for i in range(1, 8)],
            '浴池子': [pygame.image.load(f'img/test/yuchizi ({i}).png') for i in range(1, 9)],
            '月饼': [pygame.image.load(f'img/test/yuebing ({i}).png') for i in range(1, 5)],
            '针线': [pygame.image.load(f'img/test/zhenxian ({i}).png') for i in range(1, 3)],
            '镇纸': [pygame.image.load(f'img/test/zhenzhi ({i}).png') for i in range(1, 3)],
            '字画': [pygame.image.load(f'img/test/zihua ({i}).png') for i in range(1, 3)],
            '坐垫': [pygame.image.load(f'img/test/zuodian ({i}).png') for i in range(1, 6)]
        }
        items = []
        for name, image_list in item_images.items():
            scaled_images = [pygame.transform.scale(image, (130, 130)) for image in image_list]
            item = Item(name, scaled_images)
            items.append(item)
        return items

    def generate_task(self):
        item_counts = self.game_grid.count_items()
        items_in_grid = [item for item, count in item_counts.items() if count > 0]
        if not items_in_grid:
            return None, 0
        selected_item_name = random.choice(items_in_grid)
        selected_item = self.get_item_by_name(selected_item_name)
        count = random.randint(1, item_counts[selected_item_name])
        return selected_item, count

    def get_item_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def draw_task(self):
        task_text = f"{self.current_task.name} × {self.current_task_count}"
        tip_text = "可左右拖动"
        t_font = pygame.font.SysFont('simhei', 20)
        task_surface = t_font.render(task_text, True, (255, 255, 255))
        tip_surface = t_font.render(tip_text, True, (255, 255, 255))
        self.screen.blit(task_surface, (580, 10))
        self.screen.blit(tip_surface,(580,680))

    def draw_score(self):
        score_text = f"得分：{self.score}"
        score_font = pygame.font.SysFont('simhei', 20)
        score_surface = score_font.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (580, 35))

    def handle_click(self, mouse_pos):
        if not self.game_over:
            offset_x = self.game_background.position[0]
            adjusted_mouse_pos = (mouse_pos[0] - offset_x, mouse_pos[1])
            for row in range(self.game_grid.grid_size[0]):
                for col in range(self.game_grid.grid_size[1]):
                    image_tuple = self.game_grid.grid[row][col]
                    if image_tuple:
                        image_surface, item_name = image_tuple
                        image_rect = image_surface.get_rect(
                            topleft=(col * (self.game_grid.cell_width + self.game_grid.horizontal_padding) + 25,
                                     row * (self.game_grid.cell_height + self.game_grid.vertical_padding) + 60)
                        )
                        if image_rect.collidepoint(adjusted_mouse_pos):
                            if item_name == self.current_task.name:
                                self.generate_new_image(row, col)
                                self.current_task_count -= 1
                                self.score += 10
                                self.timer_extra += 1  # 增加1秒
                                if self.current_task_count <= 0:
                                    self.current_task, self.current_task_count = self.generate_task()
                                return
                            else:
                                self.timer_extra -= 1  # 减少1秒
                                return

    def generate_new_image(self, row, col):
        selected_item = random.choice(self.items)
        new_image = random.choice(selected_item.images)
        self.game_grid.grid[row][col] = (new_image, selected_item.name)

    def update_timer(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            remaining_time = self.timer_duration + self.timer_extra - elapsed_time
            if remaining_time <= 0:
                self.game_over = True
                self.popup.update_score(self.score)
            else:
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                time_text = f"{minutes:02}:{seconds:02}"
                time_font = pygame.font.Font(None, 36)
                time_surface = time_font.render(time_text, True, (255, 255, 255))
                self.screen.blit(time_surface, (self.screen_width - 100, 10))

    def reset_game(self):
        self.last_score = self.score  # 保存上一局的积分
        self.game_over = False

        self.score = 0  # 重置当前积分
        self.game_grid.grid = self.game_grid.create_grid()  # 重新生成网格
        self.current_task, self.current_task_count = self.generate_task()  # 生成新任务
        self.timer_duration = 120
        self.timer_extra = 0
        self.start_time = time.time()
        self.popup = Popup(self.screen, 300, 200, "游戏结束")

    def run(self):
        while self.running:
            if self.start_page_active:
                self.start_page = StartPage(self.screen, self.background_startimage, self.button, self.last_score)
                self.start_page.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif self.start_page.handle_events(event):
                        self.start_page_active = False
                        self.reset_game()
            else:
                self.game_background.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.game_background.handle_events(event)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.handle_click(event.pos)

                    if self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.start_page_active = True
                            self.reset_game()

                if not self.game_over:
                    self.update_timer()

                self.draw_task()
                self.draw_score()
                self.game_grid.draw(self.game_background.position[0])
                if self.game_over:
                    self.popup.draw()

            pygame.display.flip()

# 创建游戏对象并运行
game = Game()
game.run()