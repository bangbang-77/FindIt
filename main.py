import pygame

# 初始化pygame
pygame.init()

# 设置窗口大小和标题
screen_width = 1300
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("独具慧眼")

# 加载背景图像
background_image = pygame.image.load('img/bg_game.png')
background_width, background_height = background_image.get_size()
background_position = [0, 0]

# 主循环
running = True
dragging = False
offset_x = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 处理背景图拖动
        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
            offset_x = event.pos[0] - background_position[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            # 释放左键后
            if event.button == 1:
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                background_position[0] = event.pos[0] - offset_x
                # 限制背景图像的移动范围
                if background_position[0] >0:
                    background_position[0] = 0
                elif background_position[0] < screen_width - background_width:
                    background_position[0] = screen_width - background_width
    # 绘制背景图像
    screen.blit(background_image, background_position)
    # 更新屏幕
    pygame.display.flip()