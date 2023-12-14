# Gluttonous-Snake-ESP32-microPython-
# 贪吃蛇功能的实现
在这篇文章中，我将向你展示如何使用Python和ST7789库制作一个简单的贪吃蛇游戏。这个游戏使用了ESP32微控制器，通过SPI接口与显示屏进行通信。

## 游戏说明
游戏界面当中没有打印相关的按键说明，这里先逐一列出，贪吃蛇游戏按键说明：

1. 按方向键上下左右，可以实现蛇移动方向的改变。
2. 吃到食物后蛇身变长一格
3. 蛇不能后退，只能向移动方向垂直的两个方向转向
4. 计分系统，可保存玩家的记录。
## 游戏效果展示
![请添加图片描述](https://img-blog.csdnimg.cn/direct/95ec3991bbce47e69ca8c067e5149793.jpeg)
![请添加图片描述](https://img-blog.csdnimg.cn/direct/f91ecdb9622e42e6bbab701c55800c43.jpeg)
## 游戏代码
博友们可以先阅读下下面的代码，之后我的逐一讲解

```python
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
        # 
        if is_dead:
            tft.text(font, "game over", 50, 100, st7789py.color565(255,0,0), st7789py.color565(255, 255, 255))
        #延迟1s
        time.sleep_ms(1000)
    


def main():  
    play_test()

if __name__=="__main__":
    main()

```
## 屏幕与驱动介绍
在详细讲解代码前我们先来说一下这个项目所用到的外设
**1. 15.4寸240x240彩屏幕spi**

有8个引脚，说明如下
![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/14785193f374465da9e45569b252159b.png)
**2.和esp32接线方面**
![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/8408e793499544c184c4805ef6675aad.png)
**3.通过SPI协议进行传送数据，用到的芯片是ST7789**
![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/12ed6f19af5a476c9a5edcb72765b486.png)
**4.驱动下载**
想要通过SPI协议控制ST7789芯片最终实现屏幕的操作，需要下载安装python模块，

 - github.com:
[st7789py.py库](https://github.com/russhughes/st7789py_mpy)

**5.修复屏幕上述驱动不能显示的bug**
st7789py.py这个库虽然功能很强大但会出现屏幕不显示的问题，所以我们借用***st7789.py***库中的初始化函数去初始化，而具体的功能实现用更强大的***st7789py.py***库

 - 下载st7789.py文件：
[st7789.py库](https://doc.itprojects.cn/0006.zhishi.esp32/01.download/st7789.py)
 - 将st7789py.py文件中的 204、205行 注释

```python
# 解决第1次启动时，不亮的问题
st7789.ST7789(SPI(2, 60000000), dc=Pin(2), cs=Pin(5), rst=Pin(15))

# 创建显示屏对象
tft = st7789py.ST7789(SPI(2, 60000000), 240, 240, reset=Pin(15), dc=Pin(2), cs=Pin(5), rotation=0)

# 屏幕背景显示
tft.fill(st7789py.color565(255,255,255))
```
## 按键输入与外部中断
这里用4个GPIO用来外部输入中断，默认为GPIO_Pin为高电平，当按键按下时回路链接到地，电平被下拉为低电平

 - **Pin 13**	#按键GP_UP外部中断函数
- **Pin 12**	#按键GP_DOWN外部中断函数
 - **Pin 14**	#按键GP_LEFT外部中断函数
 - **Pin 27**	#按键GP_RIGHT外部中断函数

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/9a6c55b9aaab4eb2a0daa206af7cfed7.png)
## 代码详解
### 外设以及驱动的配置
**1.首先，我们需要导入所需的库和模块。这些库包括random、machine、st7789等**

```python
import random
from machine import Pin, SPI 
import st7789_itprojects as st7789
import st7789py
from romfonts import vga2_bold_16x32 as font
import time
```
**2.接下来，我们需要初始化显示屏并且渲染背景图片，在这个例子中，我们使用的是ST7789芯片驱动的显示屏，其分辨率为240x240像素。**

 - 在 st7789py.color565() 方法中传入的是RGB值

```python
# 解决第1次启动时，不亮的问题
st7789.ST7789(SPI(2, 60000000), dc=Pin(2), cs=Pin(5), rst=Pin(15))

# 创建显示屏对象
tft = st7789py.ST7789(SPI(2, 60000000), 240, 240, reset=Pin(15), dc=Pin(2), cs=Pin(5), rotation=0)
# 屏幕背景显示
tft.fill(st7789py.color565(255,255,255))
#绘制界面
tft.hline(0,35,240,st7789py.color565(0, 0, 200))
```
**效果如下：**
![请添加图片描述](https://img-blog.csdnimg.cn/direct/44f2cfda86f74db18139dcf84d550287.jpeg)
 
**3.定义按键GPIO 外部中断：**
首先，通过Pin类创建了四个引脚对象，分别对应于上、下、左和右方向的按键。每个引脚都设置为输入模式（Pin.IN），并启用内部上拉电阻（Pin.PULL_UP）。

然后，定义了一个变量direct，并将其初始值设置为字符串'left'，表示蛇默认的方向为左。
```python
#定义按键GPIO 外部中断
GP_UP = Pin(13, Pin.IN ,Pin.PULL_UP)
GP_DOWN = Pin(12, Pin.IN,Pin.PULL_UP)
GP_LEFT = Pin(14, Pin.IN,Pin.PULL_UP)
GP_RIGHT= Pin(27, Pin.IN,Pin.PULL_UP)

# 定义方向
direct = 'left'
```
**4.接下来，我们需要定义按键的中断处理函数。这些函数会在按键被按下时执行相应的操作。**
这段代码是用于处理四个按键（GP_UP、GP_DOWN、GP_LEFT、GP_RIGHT）的外部中断函数。当按下相应的按键时，会触发相应的中断服务程序，改变全局变量`direct`的值，并打印出对应的方向。

**以下是对每个按键的处理逻辑的解析：**

 1. 按键GP_UP的外部中断函数`GP_UP_irq(GP_UP)`：
   - 首先，使用`time.sleep_ms(10)`进行按键消抖，确保按键被稳定按下后再进行处理。
   - 然后，通过检查`GP_UP.value()`的值来判断按键是否被按下。如果值为0，表示按键被按下。
   - 如果当前的方向为'left'或'right'，则将方向设置为'up'。
   - 最后，打印出"上"，表示按下了向上的方向键。
 
 2. 依次类推依次对 GP_DOWN、GP_LEFT、GP_RIGHT 处理
 

```python
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

```
 3. 配置四个按键（GP_UP、GP_DOWN、GP_LEFT、GP_RIGHT）的外部中断，当按键被按下时触发相应的中断服务程序。每个按键都使用下降沿触发方式进行中断检测。

    按键GP_UP的外部中断函数`GP_UP_irq`：
  	 - 使用`irq()`方法将`GP_UP_irq`函数注册为按键`GP_UP`的中断处理程序。
  	 - 指定中断类型为下降沿触发，使用`Pin.IRQ_FALLING`作为第二个参数传递给`irq()`方法。
  	 - 依次对GP_DOWN、GP_LEFT、GP_RIGHT处理
```python
#初始化中断
GP_UP.irq(GP_UP_irq,Pin.IRQ_FALLING)#配置GP_UP外部中断，下降沿触发
GP_DOWN.irq(GP_DOWN_irq,Pin.IRQ_FALLING)#配置GP_DOWN外部中断，下降沿触发
GP_LEFT.irq(GP_LEFT_irq,Pin.IRQ_FALLING)#配置GP_LEFT外部中断，下降沿触发
GP_RIGHT.irq(GP_RIGHT_irq,Pin.IRQ_FALLING)#配置GP_RIGHT外部中断，下降沿触发
```

处理函数可以用于在嵌入式系统中检测和响应按键事件，并根据按键的不同来执行相应的操作。

### 游戏主逻辑代码详解
**1.游戏框架构建**
首先定义游戏界面的大小，定义游戏区行数和列数。
由于我们用到**240x240**屏幕所以宽高就为**240**，如果博友们用的其他大小屏幕这里可以自行修改
```python
#定义行列
W = 240
H = 240
ROW = 24  # 行
COL = 24  # 列
```
**这里将蛇活动的区域称为游戏区将分数提示的区域称为界面区**![请添加图片描述](https://img-blog.csdnimg.cn/direct/ff2e8b3fd0a3444fb7b5e0c6ba9fc392.jpeg)
**此外我们还需要定义一个点类**

```python
# 点 类
class Point:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def copy(self):
        return Point(self.row, self.col)

```

定义了一个名为`Point`的类，它有两个属性：`row`和`col`。`__init__`方法是一个特殊的方法，用于在创建对象时进行初始化。在这个例子中，`__init__`方法接受两个参数：`row`和`col`，并将它们分别赋值给对象的`row`和`col`属性。

`copy`方法也是一个特殊的方法，用于创建一个对象的副本。在这个例子中，`copy`方法通过调用`Point`类的构造函数并传入当前对象的`row`和`col`属性值来创建一个新的`Point`对象，并将其返回。

**之后在封装一个方法用来对点对象进行渲染绘制**

```python
# 绘制点函数
def rect(Point, color):
    cell_width = W // COL
    cell_height = H // ROW
    left = Point.col * cell_width
    top = Point.row * cell_height

    tft.fill_rect(left,top,cell_width,cell_height,st7789py.color565(color[0],color[1],color[2]))
```
这段代码是一个绘制矩形的函数，函数名为`rect`。它接受两个参数：`Point`和`color`。

- `Point`是一个点对象，包含行（row）和列（col）属性，表示矩形左上角的位置。
- `color`是一个颜色值，是一个包含三个整数的列表，分别表示红、绿、蓝三个通道的值。

函数内部首先计算每个单元格的宽度和高度，然后根据点的行列坐标计算出矩形左上角的坐标。最后使用`tft.fill_rect`方法在屏幕上绘制一个填充了指定颜色的矩形。

**封装一个生成食物的方法**
这段代码是一个生成食物的函数，它接受一个蛇列表作为参数。函数的主要逻辑是在一个二维空间中随机生成食物的位置，并检查该位置是否与蛇的身体重叠。如果重叠，则重新生成食物的位置，直到找到一个不与蛇身体重叠的位置为止。最后返回生成的食物位置。

以下是代码的解析：

```python
def gen_food(snakes):
    while 1:
        pos = Point(random.randint(5, ROW -4), random.randint(0, COL - 4))  # 随机生成食物的位置

        is_coll = False  # 初始化碰撞标志为False

        # 判断食物生成的位置是否在蛇身体上
        if head.row == pos.row and head.col == pos.col:
            is_coll = True  # 如果蛇头和食物位置相同，则设置碰撞标志为True
        for snake in snakes:
            if snake.row == pos.row and snake.col == pos.col:
                is_coll = True  # 如果蛇身体其他部分和食物位置相同，则设置碰撞标志为True

        if not is_coll:
            break  # 如果食物位置没有与蛇身体重叠，则跳出循环

    return pos  # 返回生成的食物位置
```
**蛇身的搭建**
定义**一个列表**用来模拟队列容器，队列头就像是蛇头，队列的尾就像是蛇尾
定义**一个元组**用于存放蛇身体的颜色（RGB格式）
```python
# 定义蛇身体
snakes = []
snakes_color = (128, 128, 128)
```
**定义食物和蛇头的坐标 和颜色**
```python
head = Point(int(ROW / 2), int(COL / 2))
head_color = (0, 128, 128)
food = gen_food(snakes)
food_color = (255, 255, 0)
```
**前面的准备工作已经完成最后就是就到了游戏循环的主逻辑**
  先创建两个变量用来记录蛇的存活和游戏分数

```python
# 游戏循环
no_quit = True
#记录分数
score=0
```
**之后进入贪吃蛇游戏的主循环**。
![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/6c1eeaaea6f5411d97d69b18ebc53df9.png)
当游戏没有退出时，它会不断执行以下操作：

1. 判断蛇是否吃到食物：如果蛇头的位置与食物的位置相同，则表示蛇吃到食物。此时会重新生成食物，并将分数加1。

```python
 # 吃东西
        eat = head.row == food.row and head.col == food.col
        # 从新产生食物
        if eat:
            rect(food, (255,255,255))  # 食物删除渲染（用白色覆盖掉）
            food = Point(random.randint(0, ROW - 1), random.randint(0, COL - 1))
            score+=1    #分数加1
```

2. 更新蛇的身体：将蛇头插入到蛇身体的头部，并删除蛇尾（如果没有吃到食物）。

```python
# 身子
        # 1 先把头插到身子上
        snakes.insert(0, head.copy())
        # 2 把尾巴删掉
        if not eat:
            rect(snakes[-1], (255,255,255))  # 蛇尾删除渲染
            snakes.pop()
```

3. 根据用户输入的方向移动蛇头：根据`direct`变量的值，分别向左、右、上、下移动蛇头。

```python
# 移动
        if direct == 'left':
            head.col -= 1
        elif direct == 'right':
            head.col += 1
        elif direct == 'up':
            head.row -= 1
        elif direct == 'down':
            head.row += 1
```
4. 检查蛇是否死亡：如果蛇头的位置超出了屏幕边界或者与蛇身体的其他部分重叠，则表示蛇死亡。此时会打印"死亡了"，并将`no_quit`设置为False以退出游戏循环。

```python
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
```

5. 渲染游戏画面：使用`rect`函数绘制食物、蛇头和蛇身，并使用`tft.text`函数在屏幕上显示分数。

```python
# 渲染
        rect(food, food_color)  # 食物渲染
        rect(head, head_color)  # 蛇头渲染
        for snake in snakes:  # 渲染身子
            rect(snake, snakes_color)
        
        # 渲染分数
        tft.text(font, "score {}".format(score), 0, 0, st7789py.color565(0, 0, 200), st7789py.color565(255, 255, 255))    
```

 
6. 如果蛇死亡，还会在屏幕上显示"game over"字样。

```python
if is_dead:
   tft.text(font, "game over", 50, 100, st7789py.color565(255,0,0), st7789py.color565(255, 255, 255))
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/e1040e97f29d445d9c1e925ceee4ddf5.png)
7. 最后，程序会延迟1秒钟，然后继续执行下一次循环。

```python
#延迟1s
        time.sleep_ms(1000)
```
这里的延迟时间决定了**程序执行的快慢**，也就是蛇移动的快慢，博友们可以根据需要自行修改

**那这样我们的工作也就全部完成了，在最后main函数中调用游戏循环方法即可**
```python
def main():  
    play_test()
if __name__=="__main__":
    main()
```
**我们将游戏的主逻辑封装到一个函数便于我们在日后对程序进行功能上的拓展，至此我们的程序已经完成**
## 对广大开发者和电子爱好者说的话
**完整项目我放在下面的链接：**
[贪吃蛇 ESP32 (microPython实现)](https://github.com/1589326497/Gluttonous-Snake-ESP32-microPython-)

大家都知道**ESP32**和其他单片机最大的差异是集成了**wifi和蓝牙功能**，可以利用这一特点进行功能的拓展

**以下是我想到的几个可以拓展的点子：**

1. 增加多人模式：允许多名玩家同时进行游戏，看谁能获得更高的分数。

2. 增加关卡模式：设置多个关卡，每个关卡的难度和目标都有所不同，让玩家在满足过关条件后解锁下一关。

3. 引入道具和技能系统：在游戏中加入各种有益的道具和障碍性道具，以及可以提高分数或改变游戏规则的技能。

4. 实现联机对战功能：通过网络连接，允许两名或更多的玩家进行实时对战。

5. 加入皮肤和装扮系统：让玩家可以根据自己的喜好选择不同的游戏外观。

6. 优化视觉效果：提供更丰富的颜色和动态效果，增强游戏的视觉体验。

7. 加入音乐和声效：合适的背景音乐和声效能够提升游戏的氛围感，使玩家更加投入。

欢迎博友们进行创新和拓展，开发出属于自己独一无二的作品



