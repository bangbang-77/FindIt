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

# 主循环
running = True
start_page = True
dragging = False
offset_x = 0

while running:
    if start_page:
        # 绘制开始页面
        screen.blit(background_startimage, background_startposition)
        pygame.draw.circle(screen, button_color, button_position, button_radius)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 处理背景图拖动
            elif event.type == pygame.MOUSEBUTTONDOWN:
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