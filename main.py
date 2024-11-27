import time
import pygame
import math
# 初始化pygame
pygame.init()

# 设置窗口大小和标题
screen_width = 1300
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("独具慧眼")

# 加载开始页面背景图像
background_startimage = pygame.image.load('img/bg_game.png')
background_startwidth, background_startheight = background_startimage.get_size()
background_startposition = [screen_width - background_startwidth, 0]
# 设置跳转按钮
button_color = (0, 255, 0)
button_radius = 50
button_position = (screen_width - button_radius - 20, screen_height - button_radius - 20)
# 加载游戏背景图像
background_gameimage = pygame.image.load('img/bg_game.png')
background_gamewidth, background_gameheight = background_gameimage.get_size()
background_gameposition = [0, 0]
# 创建一个较小的窗口
popup_width = 300
popup_height = 200
popup_surface = pygame.Surface((popup_width, popup_height))
popup_surface.fill((255, 255, 255))  # 白色背景
popup_rect = popup_surface.get_rect(center=(screen_width // 2, screen_height // 2))

# 绘制游戏结束文本
font_path = pygame.font.match_font('simhei')  # 查找系统中存在的黑体字体文件
popup_font = pygame.font.Font(font_path, 48)
popup_text = popup_font.render("游戏结束", True, (0, 0, 0))
popup_text_rect = popup_text.get_rect(center=(popup_width // 2, popup_height // 2))
popup_surface.blit(popup_text, popup_text_rect)
# 主循环
running = True
start_page = True
dragging = False
offset_x = 0
game_over = False
start_time = 0

while running:
    if start_page:
        # 绘制开始页面
        screen.blit(background_startimage, background_startposition)
        pygame.draw.circle(screen, button_color, button_position, button_radius)
    else:
        # 绘制游戏页面
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 处理背景图拖动
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if game_over:
                        start_page = True
                        game_over = False
                    else:
                        dragging = True
                        offset_x = event.pos[0] - background_gameposition[0]
            elif event.type == pygame.MOUSEBUTTONUP:
                # 释放左键后
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    background_gameposition[0] = event.pos[0] - offset_x
                    # 限制背景图像的移动范围
                    if background_gameposition[0] >0:
                        background_gameposition[0] = 0
                    elif background_gameposition[0] < screen_width - background_gamewidth:
                        background_gameposition[0] = screen_width - background_gamewidth
        # 绘制游戏背景图像
        screen.blit(background_gameimage, background_gameposition)

        # 倒计时
        if not game_over:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, 5 - elapsed_time) #现在我设置的是120s
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            time_text = f"{minutes:02}:{seconds:02}"
            time_font = pygame.font.Font(None, 36)
            time_surface = time_font.render(time_text, True, (255, 255, 255))
            screen.blit(time_surface, (screen_width - 100, 10))

            # 检查倒计时是否结束
            if remaining_time <= 0:
                game_over = True
        # 绘制游戏结束弹窗
        if game_over:


            # 绘制弹窗
            screen.blit(popup_surface, popup_rect)
    # 更新屏幕
    pygame.display.flip()

    # 开始页面的跳转
    if start_page:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    # 检查是否点击了按钮
                    if math.sqrt((mouse_x - button_position[0]) ** 2 + (mouse_y - button_position[1]) ** 2) <= button_radius:
                        start_page = False
                        start_time = time.time()