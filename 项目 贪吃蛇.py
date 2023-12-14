import random
from machine import Pin, SPI 
import st7789_itprojects as st7789
import st7789py
from romfonts import vga2_bold_16x32 as font
import time


# 解决第1次启动时，不亮的问题
st7789.ST7789(SPI(2, 60000000), dc=Pin(2), cs=Pin(5), rst=Pin(15))

# 创建显示屏对象
tft = st7789py.ST7789(SPI(2, 60000000), 240, 240, reset=Pin(15), dc=Pin(2), cs=Pin(5), rotation=0)

# 屏幕背景显示
tft.fill(st7789py.color565(255,255,255))
#绘制界面
tft.hline(0,35,240,st7789py.color565(0, 0, 200))
#定义按键GPIO 外部中断
GP_UP = Pin(13, Pin.IN ,Pin.PULL_UP)
GP_DOWN = Pin(12, Pin.IN,Pin.PULL_UP)
GP_LEFT = Pin(14, Pin.IN,Pin.PULL_UP)
GP_RIGHT= Pin(27, Pin.IN,Pin.PULL_UP)

# 定义方向
direct = 'left'

#按键GP_UP外部中断函数
def GP_UP_irq(GP_UP):
    global direct
    time.sleep_ms(10) #按键消抖
    if GP_UP.value()==0:
        if direct == 'left' or direct == 'right':
                direct = 'up'
        print("上")

#按键GP_DOWN外部中断函数
def GP_DOWN_irq(GP_DOWN):
    global direct
    time.sleep_ms(10) #按键消抖
    if GP_DOWN.value()==0:
        if direct == 'left' or direct == 'right':
                direct = 'down'
        print("下")
#按键GP_LEFT外部中断函数
def GP_LEFT_irq(GP_LEFT):
    global direct
    time.sleep_ms(10) #按键消抖
    if GP_LEFT.value()==0:
        if direct == 'up' or direct == 'down':
                direct = 'left'
        print("左")
#按键GP_RIGHT外部中断函数
def GP_RIGHT_irq(GP_RIGHT):
    global direct
    time.sleep_ms(10) #按键消抖
    if GP_RIGHT.value()==0:
        if direct == 'up' or direct == 'down':
                direct = 'right'
        print("右")
#初始化中断
GP_UP.irq(GP_UP_irq,Pin.IRQ_FALLING)#配置GP_UP外部中断，下降沿触发
GP_DOWN.irq(GP_DOWN_irq,Pin.IRQ_FALLING)#配置GP_DOWN外部中断，下降沿触发
GP_LEFT.irq(GP_LEFT_irq,Pin.IRQ_FALLING)#配置GP_LEFT外部中断，下降沿触发
GP_RIGHT.irq(GP_RIGHT_irq,Pin.IRQ_FALLING)#配置GP_RIGHT外部中断，下降沿触发


#定义行列
W = 240
H = 240
ROW = 24  # 行
COL = 24  # 列

# 点 类
class Point:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def copy(self):
        return Point(self.row, self.col)

# 绘制点函数
def rect(Point, color):
    cell_width = W // COL
    cell_height = H // ROW
    left = Point.col * cell_width
    top = Point.row * cell_height

    tft.fill_rect(left,top,cell_width,cell_height,st7789py.color565(color[0],color[1],color[2]))

# 生成食物函数
def gen_food(snakes):
    while 1:
        pos = Point(random.randint(5, ROW -4), random.randint(0, COL - 4))  # random.randint()方法生成随机的行和列的食物

        # 判断食物生成的位置是否在蛇身体上
        is_coll = False
        if head.row == pos.row and head.col == pos.col:
            is_coll = True
        for snake in snakes:
            if snake.row == pos.row and snake.col == pos.col:
                is_coll = True
        if not is_coll:
            break
    return pos

# 定义蛇身体
snakes = []
snakes_color = (128, 128, 128)

# 定义坐标 和颜色
head = Point(int(ROW / 2), int(COL / 2))
head_color = (0, 128, 128)
food = gen_food(snakes)
food_color = (255, 255, 0)


# 游戏循环
no_quit = True

#记录分数
score=0
#游戏执行方法
def play_test():
    # 声明全局变量
    global no_quit
    global direct
    global snakes
    global score
    global food
    global head
    while no_quit:
        # 吃东西
        eat = head.row == food.row and head.col == food.col
        # 从新产生食物
        if eat:
            rect(food, (255,255,255))  # 食物删除渲染（用白色覆盖掉）
            food = Point(random.randint(0, ROW - 1), random.randint(0, COL - 1))
            score+=1    #分数加1
        # 身子
        # 1 先把头插到身子上
        snakes.insert(0, head.copy())
        # 2 把尾巴删掉
        if not eat:
            rect(snakes[-1], (255,255,255))  # 蛇尾删除渲染
            snakes.pop()
            

        # 移动
        if direct == 'left':
            head.col -= 1
        elif direct == 'right':
            head.col += 1
        elif direct == 'up':
            head.row -= 1
        elif direct == 'down':
            head.row += 1
        # 检查
        is_dead = False
        # 1，撞墙
        if head.col < 0 or head.row < 0 or head.col > COL or head.row > ROW:
            is_dead = True
        # 2，撞自己
        for snake in snakes:
            if snake.col == head.col and snake.row == head.row:
                is_dead = True
                break
        if is_dead:
            print("死亡了")
            no_quit = False
        # 渲染
        rect(food, food_color)  # 食物渲染
        rect(head, head_color)  # 蛇头渲染
        for snake in snakes:  # 渲染身子
            rect(snake, snakes_color)
        
        # 渲染分数
        tft.text(font, "score {}".format(score), 0, 0, st7789py.color565(0, 0, 200), st7789py.color565(255, 255, 255))
        #死亡显示game over
        if is_dead:
            tft.text(font, "game over", 50, 100, st7789py.color565(255,0,0), st7789py.color565(255, 255, 255))
        #延迟1s
        time.sleep_ms(1000)
    


def main():  
    play_test()

if __name__=="__main__":
    main()



