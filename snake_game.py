"""贪吃蛇小游戏 - 使用 Python 内置 turtle 库，无需额外安装依赖。"""

import turtle
import time
import random

# ---------- 游戏配置 ----------
SPEED = 0.12          # 蛇移动间隔（秒），越小越快
CELL = 20             # 每格大小
GRID_W = 30           # 横向格子数
GRID_H = 20           # 纵向格子数
WIDTH = CELL * GRID_W
HEIGHT = CELL * GRID_H

# ---------- 初始化窗口 ----------
screen = turtle.Screen()
screen.title("贪吃蛇小游戏")
screen.setup(WIDTH + 40, HEIGHT + 40)
screen.tracer(0)          # 关闭自动刷新，手动控制动画
screen.bgcolor("black")

# ---------- 画笔：用于绘制蛇身 ----------
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.penup()

# ---------- 状态 ----------
snake = [(0, 0), (-CELL, 0), (-2 * CELL, 0)]   # 蛇身坐标（头在第一个）
direction = "right"
next_direction = "right"
food = None
score = 0
high_score = 0
running = True


def draw_square(x, y, color):
    """在指定格子绘制一个方块。"""
    drawer.goto(x, y)
    drawer.color(color)
    drawer.begin_fill()
    for _ in range(4):
        drawer.forward(CELL)
        drawer.left(90)
    drawer.end_fill()


def draw_circle(cx, cy, radius, color):
    """在指定圆心绘制一个实心圆。"""
    drawer.penup()
    drawer.goto(cx, cy)
    drawer.dot(int(radius * 2), color)


def draw_head(x, y):
    """绘制蛇头：白色主体 + 红色眼睛 + 蓝色舌头。"""
    cx = x + CELL / 2
    cy = y + CELL / 2

    # 蛇头主体
    draw_square(x, y, "white")

    # 当前朝向的单位向量
    dx, dy = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }[direction]
    # 与朝向垂直的向量，用于左右偏移
    px, py = -dy, dx

    # 红色眼睛：位于头部前方两侧
    eye_offset = CELL * 0.3
    eye_radius = CELL * 0.12
    for side in (-1, 1):
        ex = cx + dx * eye_offset + px * side * eye_offset
        ey = cy + dy * eye_offset + py * side * eye_offset
        draw_circle(ex, ey, eye_radius, "red")

    # 蓝色舌头：从头部前方伸出并分叉
    tx = cx + dx * (CELL / 2)
    ty = cy + dy * (CELL / 2)
    tongue_len = CELL * 0.7
    fork_len = CELL * 0.3
    tip_x = tx + dx * tongue_len
    tip_y = ty + dy * tongue_len

    drawer.pensize(2)
    drawer.color("blue")
    drawer.penup()
    drawer.goto(tx, ty)
    drawer.pendown()
    drawer.goto(tip_x, tip_y)
    for side in (-1, 1):
        fx = tip_x + dx * fork_len + px * side * fork_len * 0.5
        fy = tip_y + dy * fork_len + py * side * fork_len * 0.5
        drawer.goto(fx, fy)
        drawer.goto(tip_x, tip_y)
    drawer.penup()
    drawer.pensize(1)


def spawn_food():
    """在空白位置随机生成食物。"""
    global food
    while True:
        x = random.randint(-GRID_W // 2, GRID_W // 2 - 1) * CELL
        y = random.randint(-GRID_H // 2, GRID_H // 2 - 1) * CELL
        if (x, y) not in snake:
            food = (x, y)
            return


def draw_border():
    """绘制边界。"""
    drawer.color("gray")
    drawer.penup()
    drawer.goto(-WIDTH / 2 - CELL, -HEIGHT / 2 - CELL)
    drawer.pendown()
    for _ in range(2):
        drawer.forward(WIDTH + 2 * CELL)
        drawer.left(90)
        drawer.forward(HEIGHT + 2 * CELL)
        drawer.left(90)
    drawer.penup()


def move():
    """根据方向移动蛇。"""
    global food, score, running
    head_x, head_y = snake[0]

    if direction == "up":
        new_head = (head_x, head_y + CELL)
    elif direction == "down":
        new_head = (head_x, head_y - CELL)
    elif direction == "left":
        new_head = (head_x - CELL, head_y)
    else:  # right
        new_head = (head_x + CELL, head_y)

    # 撞墙判定
    if abs(new_head[0]) > WIDTH / 2 or abs(new_head[1]) > HEIGHT / 2:
        game_over()
        return

    # 撞自己判定
    if new_head in snake:
        game_over()
        return

    snake.insert(0, new_head)

    # 吃到食物
    if new_head == food:
        score += 1
        spawn_food()
    else:
        snake.pop()

    draw()


def draw():
    """重绘整个画面。"""
    drawer.clear()
    draw_border()
    draw_square(food[0], food[1], "red")
    for i, (x, y) in enumerate(snake):
        if i == 0:
            draw_head(x, y)
        else:
            draw_square(x, y, "green")

    # 分数显示
    drawer.goto(-WIDTH / 2, HEIGHT / 2 + 15)
    drawer.color("white")
    drawer.write(f"得分: {score}   最高分: {high_score}",
                 align="left", font=("Arial", 16, "bold"))
    screen.update()


def game_over():
    """游戏结束。"""
    global running, high_score
    running = False
    high_score = max(high_score, score)
    drawer.goto(0, 40)
    drawer.color("yellow")
    drawer.write("游戏结束！", align="center", font=("Arial", 28, "bold"))
    drawer.goto(0, -10)
    drawer.color("white")
    drawer.write(f"最终得分: {score}   按空格键重新开始",
                 align="center", font=("Arial", 16, "normal"))
    screen.update()


def reset():
    """重新开始游戏。"""
    global snake, direction, next_direction, food, score, running
    snake = [(0, 0), (-CELL, 0), (-2 * CELL, 0)]
    direction = "right"
    next_direction = "right"
    score = 0
    running = True
    spawn_food()
    drawer.clear()
    draw()


def set_direction(new_dir):
    """设置方向（禁止直接反向）。"""
    global next_direction
    opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
    if new_dir != opposites.get(direction):
        next_direction = new_dir


def game_loop():
    """主循环。"""
    global direction
    if running:
        direction = next_direction
        move()
    screen.ontimer(game_loop, int(SPEED * 1000))


# ---------- 键盘绑定 ----------
screen.listen()
screen.onkey(lambda: set_direction("up"), "Up")
screen.onkey(lambda: set_direction("down"), "Down")
screen.onkey(lambda: set_direction("left"), "Left")
screen.onkey(lambda: set_direction("right"), "Right")
screen.onkey(lambda: set_direction("up"), "w")
screen.onkey(lambda: set_direction("down"), "s")
screen.onkey(lambda: set_direction("left"), "a")
screen.onkey(lambda: set_direction("right"), "d")
screen.onkey(reset, "space")

# ---------- 开始游戏 ----------
spawn_food()
draw()
game_loop()
screen.mainloop()
