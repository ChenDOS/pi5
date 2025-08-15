# pi5
一个简洁、功能强大的树莓派GPIO操作库
依赖库：RPi.GPIO,board,adafruit_dht
# Pi5 GPIO类使用文档

## 快速开始

### 控制LED

```python
from pi5 import GPIO,wait

led = GPIO(BCM=18)      # 使用BCM编号18
led.output(1)           # 高电平点亮，无需配置输入/输出模式，pi5库执行相应函数会自动切换
wait(1000)              # 等待1秒
led.output(0)           # 关闭
```

### 读取按钮状态

```python
button = GPIO(board=11)   # 使用BOARD编号11
print(button.Input())   # 读取当前电平，因为与Python内置函数input冲突所以第一个字母设计为大写
```

## 核心功能

### 1. 引脚初始化

支持**BCM**和**BOARD**两种编号模式：

```python
# BCM模式（推荐）
gpio_bcm = GPIO(BCM=18)

# BOARD模式
gpio_board = GPIO(board=12)
```

### 2. 输出控制

#### 数字输出

```python
gpio = GPIO(BCM=17)
gpio.output(1)  # 高电平
gpio.output(0)  # 低电平
```

#### PWM输出

```python
gpio = GPIO(BCM=18)
gpio.output(0.5, frequency=100)  # 50%占空比，100Hz频率
```

### 3. 输入检测

支持上拉/下拉电阻配置：

```python
# 无上下拉，因为与Python内置函数input冲突所以第一个字母设计为大写
val = gpio.Input()  

# 启用上拉电阻
val = gpio.Input(resistance=pi5.PUD_UP)

# 启用下拉电阻
val = gpio.Input(resistance=pi5.PUD_DOWN)
```

### 4. 事件回调系统

#### 事件类型常量

```python
from pi5 import (
    EVENT_RISING,       # 上升沿
    EVENT_FALLING,      # 下降沿
    EVENT_BOTH          # 双边沿
)
```

#### 注册回调

```python
def on_rise():
    print("检测到上升沿！")

callback_id = gpio.addEvent(EVENT_RISING, on_rise)
```

#### 启动事件检测

```python
# 带防抖（50ms）和上拉电阻
gpio.runEvents(resistance=pi5.PUD_UP, bouncetime=50)

# 停止检测
gpio.stopEvents()
```

#### 完整示例

```python
from pi5 import GPIO, EVENT_RISING,wait

btn = GPIO(BCM=23)

def button_pressed():
    print("按钮被按下！")

btn.addEvent(EVENT_RISING, button_pressed)
btn.runEvents(resistance=pi5.PUD_DOWN)

try:
    while True:
        wait(100)
except KeyboardInterrupt:
    btn.stopEvents()
```

## 高级功能

### 多回调管理

```python
# 添加回调
id1 = gpio.addEvent(EVENT_RISING, callback1)
id2 = gpio.addEvent(EVENT_FALLING, callback2)

# 移除特定回调
gpio.removeEvent(id1)

# 清除所有回调
gpio.clearEvents()
```

### 资源清理

```python
# 安全停止单个引脚
gpio.stop()

# 清理所有GPIO资源
pi5.close()
```

### 引脚转换

```python
print(pi5.toBcm(12)) # 将board引脚转成BCM，输出18
print(pi5.toBoard(18)) # 将BCM引脚转成board，输出12
gpio = pi5.GPIO(BCM=18)
print(gpio.BCM) # 获取GPIO对象的BCM编码，也会输出18
print(gpio.board) # 获取GPIO对象的BCM编码，也会输出12
```

# LED类

### 点亮LED

```python
import pi5
gpio18 = pi5.GPIO(18) # LED所在GPIO
led = pi5.LED(gpio18)
led.lightUp(1) # 点亮至最大亮度(100%)
led.lightUp(0.3,1000) # 改变亮度至30%亮度，PWM频率1kHz
print(led.state) # LED状态，输出True(点亮)、False(熄灭)
```

### LED闪烁

```python
led.flashing(500,6) # 闪烁6次，每次间隔500ms
```

### LED高级控制

```python
# 线性呼吸灯模板，t表示时间，led.control会定时传入t参数
def linear_breath(t):
    # 亮度在 0~1 之间循环
    if t == 10*1000:
        return None # 10s后退出控制，退出控制需要主动返回None
    cycle = t % 200  # 一个周期200步
    if cycle <= 100:
        brightness = cycle / 100
    else:
        brightness = (200 - cycle) / 100
    return brightness
led.control(function=linear_breath,_range=500,frequency=1000) # 模板函数为linear_breath，定时间隔为500ms，PWM频率为1kHz
```

# RGB LED类

### 点亮三色LED模块

```python
import pi5
gpio17 = pi5.GPIO(17) # 三色LED R分量引脚
gpio27 = pi5.GPIO(27) # 三色LED G分量引脚
gpio22 = pi5.GPIO(22) # 三色LED B分量引脚
RGB_LED = pi5.RGBLED(gpio17,gpio27,gpio22) # 初始化三色LED
RGB_LED.lightUp(R_brightness=1,G_brightness=0,B_brightness=1) # 点亮红蓝
RGB_LED.lightUp(R_brightness=0.2,G_brightness=0.3,B_brightness=0.7,frequency=1000) # PWM调光，频率1kHz
print(RGB_LED.G_GPIO_STATE) # 输出绿色状态(True=点亮，False=熄灭)
RGB_LED.flashing(500,6) # 闪烁6次，每次间隔500ms
```

### 三色LED模块高级控制：随机颜色

```python
import pi5
import random
gpio17 = pi5.GPIO(17) # 三色LED R分量引脚
gpio27 = pi5.GPIO(27) # 三色LED G分量引脚
gpio22 = pi5.GPIO(22) # 三色LED B分量引脚
RGB_LED = pi5.RGBLED(gpio17,gpio27,gpio22) # 初始化三色LED
def func(t):
    if t >= 20*1000:
        return None # 20s后退出控制，退出控制需要主动返回None
    R_color = (random.randint(0,100)/100)
    G_color = (random.randint(0,100)/100)
    B_color = (random.randint(0,100)/100) # 随机颜色
    return (R_color,G_color,B_color) # 需要返回三色亮度列表/元组
RGB_LED.control(function=func,_range=500,frequency=1000) # 控制函数func，控制时间间隔500ms，PWM频率1kHz
```

# PassiveBuzzer类

### 类功能概述

无源蜂鸣器驱动类，支持：
- 单音发声（固定频率和时长）
- 连续音序列播放

---

## 快速开始

### 基础蜂鸣

```python
from pi5 import GPIO, PassiveBuzzer

buzzer_gpio = GPIO(BCM=18)  # 连接蜂鸣器的GPIO引脚
buzzer = PassiveBuzzer(buzzer_gpio)

# 发出1kHz声音，持续1秒（50%音量）
buzzer.beep(1000)  

# 发出880Hz声音，持续500ms（30%音量）
buzzer.beep(880, volume=0.3, t=500)  
```

---

## 核心方法

### 1. `beep(frequency, volume=0.5, t=1000)`
播放单个音调

| 参数        | 类型    | 默认值 | 说明                     |
|-------------|---------|--------|--------------------------|
| frequency   | int     | 必填   | 频率(Hz)，0-20kHz范围    |
| volume      | float   | 0.5    | 音量(0.0-1.0)            |
| t           | int     | 1000   | 持续时间(毫秒)           |

**示例**：
```python
# 报警音效
buzzer.beep(2000, volume=0.8, t=200)
```

---

### 2. `beeps(spectrum:list)`
播放音调序列

| 参数      | 类型       | 说明                              |
|-----------|------------|-----------------------------------|
| spectrum  | list[tuple]| 每个元素为(freq,volume,duration)  |

**示例**：
```python
# 警报声模式
alarm_pattern = [
    (2000, 0.7, 200),  # 2kHz 70%音量 200ms
    (0, 0, 100),        # 静音100ms
    (2000, 0.7, 200),
    (0, 0, 100)
]
buzzer.beeps(alarm_pattern)
```

### 3. `stop()`停止发声
```python
buzzer.stop()
```

# ActiveBuzzer 类

## 核心功能说明

`ActiveBuzzer` 类为有源蜂鸣器提供简洁高效的控制接口，适用于警报、提示音等场景。

### 初始化
```python
buzzer = ActiveBuzzer(GPIO(BCM=18))  # 指定GPIO引脚初始化
```

### 方法速查表
| 方法 | 参数 | 说明 |
|------|------|------|
| `beep(volume=1, t=1000)` | volume: 0.0-1.0<br>t: 毫秒时长 | 单次蜂鸣（自动关闭） |
| `beeps(spectrum)` | spectrum: [(volume:音量,t:时间ms),...] | 播放音效序列 |
|`stop()`|无|停止发声|

## 最佳实践示例

### 1. 基础提示音
```python
# 短促提示音
buzzer.beep(t=100)  # 100ms短鸣

# 渐进提示音（通过列表推导式实现渐变）
buzzer.beeps([(i*0.1, 50) for i in range(1,11)])  # 音量10%→100%阶梯上升
```

### 2. 警报模式
```python
# 紧急警报（急促鸣响）
alert = [(1,100), (0,50)] * 5  # 快速鸣响5次
buzzer.beeps(alert)

# 呼吸式警报（平滑渐变）
breath = [(math.sin(i/5)*0.5+0.5, 50) for i in range(30)]  # 正弦波音量变化
buzzer.beeps(breath)
```

### 3. 复合音效
```python
# 启动自检音效
self_test = [
    (0.3, 200), (0, 100),
    (0.6, 200), (0, 100),
    (1.0, 500)
]
buzzer.beeps(self_test)
```

# Pi5扩展库
#### pi5允许使用官方或第三方扩展库,实现更多功能
---

# DHT11扩展库：By:官方

## 基础使用
```python
import pi5
import pi5_DHT11
GPIO18 = pi5.GPIO(BCM=18) # 传感器所在GPIO
dht = pi5_DHT11.DHT11(GPIO18) # 初始化传感器
print(dht.get()) # 输出元组(温度,湿度)
print(dht.getTemperature()) # 仅输出温度
print(dht.getHumidity()) # 仅输出湿度
```