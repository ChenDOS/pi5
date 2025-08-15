import RPi.GPIO as GPI
import time
board_to_bcm = {
    # 电源引脚（无GPIO功能）
    1: None,   # 3.3V
    2: None,   # 5V
    4: None,   # 5V
    6: None,   # GND
    9: None,   # GND
    14: None,  # GND
    17: None,  # 3.3V
    20: None,  # GND
    25: None,  # GND
    30: None,  # GND
    34: None,  # GND
    39: None,  # GND

    # GPIO引脚（可编程）
    3: 2,      # BOARD3 → BCM2 (SDA1)
    5: 3,      # BOARD5 → BCM3 (SCL1)
    7: 4,      # BOARD7 → BCM4
    8: 14,     # BOARD8 → BCM14 (TXD0)
    10: 15,    # BOARD10 → BCM15 (RXD0)
    11: 17,    # BOARD11 → BCM17
    12: 18,    # BOARD12 → BCM18 (PCM_CLK)
    13: 27,    # BOARD13 → BCM27
    15: 22,    # BOARD15 → BCM22
    16: 23,    # BOARD16 → BCM23
    18: 24,    # BOARD18 → BCM24
    19: 10,    # BOARD19 → BCM10 (MOSI)
    21: 9,     # BOARD21 → BCM9 (MISO)
    22: 25,    # BOARD22 → BCM25
    23: 11,    # BOARD23 → BCM11 (SCLK)
    24: 8,     # BOARD24 → BCM8 (CE0)
    26: 7,     # BOARD26 → BCM7 (CE1)
    27: 0,     # BOARD27 → BCM0 (ID_SD)
    28: 1,     # BOARD28 → BCM1 (ID_SC)
    29: 5,     # BOARD29 → BCM5
    31: 6,     # BOARD31 → BCM6
    32: 12,    # BOARD32 → BCM12
    33: 13,    # BOARD33 → BCM13
    35: 19,    # BOARD35 → BCM19 (MISO)
    36: 16,    # BOARD36 → BCM16
    37: 26,    # BOARD37 → BCM26
    38: 20,    # BOARD38 → BCM20 (MOSI)
    40: 21,    # BOARD40 → BCM21 (SCLK)
}

# BCM编号 → BOARD编号 映射（反向推导）
bcm_to_board = {v: k for k, v in board_to_bcm.items() if v is not None}
PUD_UP = 0x01
PUD_DOWN = 0x02
EVENT_RISING = 0x03
EVENT_FALLING = 0x04
EVENT_BOTH = 0x05

events = {}
_id = 0

class GPIO:
    def __init__(self,BCM=None,board=None):
        
        if BCM is not None:
            self.BCM = BCM
            self.board = bcm_to_board[self.BCM]
        else:
            self.board = board
            self.BCM = board_to_bcm[self.board]
        GPI.setmode(GPI.BCM)
        self.callBacks = {
            "RISING":{},
            "FALLING":{},
            "BOTH":{},
            "id_RISING":0,
            "id_FALLING":0,
            "id_BOTH":0
        }
    
    def output(self,level=1,frequency=None):
        try:
            self.pwm.stop()
            del self.pwm
            GPI.cleanup(self.BCM)
        except:
            pass
        if (frequency is None) and (level==1):
            GPI.setup(self.BCM,GPI.OUT)
            GPI.output(self.BCM,GPI.HIGH)
        elif (frequency is None) and (level==0):
            GPI.setup(self.BCM,GPI.OUT)
            GPI.output(self.BCM,GPI.LOW)
        else:
            GPI.setup(self.BCM,GPI.OUT)
            self.pwm = GPI.PWM(self.BCM,frequency)
            self.pwm.start(level*100)
    
    def Input(self,resistance=None):
        try:
            self.pwm.stop()
            del self.pwm
            GPI.cleanup(self.BCM)
        except:
            pass

        if resistance is None:
            GPI.setup(self.BCM, GPI.IN)
        elif resistance == 0x01:
            GPI.setup(self.BCM, GPI.IN,pull_up_down=GPI.PUD_UP)
        elif resistance == 0x02:
            GPI.setup(self.BCM, GPI.IN,pull_up_down=GPI.PUD_DOWN)
        
        value = GPI.input(self.BCM)
        return value

    def addEvent(self,event_type,callback):
        if event_type == EVENT_RISING:
            _id = self.callBacks["id_RISING"]
            self.callBacks["RISING"][_id] = callback
            self.callBacks["id_RISING"] += 1
            _id = ("RISING",_id)
        elif event_type == EVENT_FALLING:
            _id = self.callBacks["id_FALLING"]
            self.callBacks["FALLING"][_id] = callback
            self.callBacks["id_FALLING"] += 1
            _id = ("FALLING",_id)
        elif event_type == EVENT_BOTH:
            _id = self.callBacks["id_BOTH"]
            self.callBacks["BOTH"][_id] = callback
            self.callBacks["id_BOTH"] += 1
            _id = ("BOTH",_id) 
        return _id
    
    def removeEvent(self,_id):
        del self.callBacks[_id[0]][_id[1]]
    
    def runEvents(self,resistance=None,bouncetime=50):
        try:
            self.pwm.stop()
            del self.pwm
            GPI.cleanup(self.BCM)
        except:
            pass
        if resistance == PUD_UP:
            GPI.setup(self.BCM,GPI.IN,GPI.PUD_UP)
        elif resistance == PUD_DOWN:
            GPI.setup(self.BCM,GPI.IN,GPI.PUD_DOWN)
        elif resistance is None:
            GPI.setup(self.BCM,GPI.IN)
        def smart_callback(channel):
            if self.Input(resistance):
                for i in self.callBacks["RISING"].values():
                    i()
                for i in self.callBacks["BOTH"].values():
                    i()
            else:
                for i in self.callBacks["FALLING"].values():
                    i()
                for i in self.callBacks["BOTH"].values():
                    i()
            GPI.remove_event_detect(self.BCM)
            GPI.add_event_detect(self.BCM, GPI.BOTH, callback=smart_callback, bouncetime=bouncetime)
        
        GPI.add_event_detect(self.BCM, GPI.BOTH, callback=smart_callback, bouncetime=bouncetime)
    
    def stopEvents(self):
        GPI.remove_event_detect(self.BCM)
    
    def clearEvents(self):
        self.callBacks = {
            "RISING":{},
            "FALLING":{},
            "BOTH":{},
            "id_RISING":0,
            "id_FALLING":0,
            "id_BOTH":0
        }
    

    
    def stop(self):
        try:
            self.pwm.stop()
            del self.pwm
            self.stopEvents()
        except:
            pass
        GPI.setup(self.BCM,GPI.OUT)
        GPI.output(self.BCM,GPI.LOW)
        GPI.cleanup(self.BCM)
    
    def __del__(self):
        try:
            self.stop()
        except:
            pass

class LED:
    def __init__(self,gpio:GPIO):
        self.gpio = gpio
        self.gpio.output(0)
        self.state = False
    def lightUp(self,brightness=1,frequency=None):
        self.gpio.output(brightness,frequency)
        if brightness == 0:
            self.state = False
        else:
            self.state = True
            # LED状态: False为熄灭，True为点亮
    def flashing(self,t,times=1):
        for _ in range(times):
            self.gpio.output(1)
            self.state = True
            wait(t)
            self.gpio.output(0)
            self.state = False
            wait(t)
    def control(self,function,_range=1000,frequency=100): # 更高级亮度控制，使用函数，开发者自定义函数，传入时间，输出亮度
        t = 0
        while True:
            _return = function(t)
            if _return is None: # 退出条件：函数主动返回None
                break
            else:
                if _return == 0:
                    self.state = False
                else:
                    self.state = True
                self.gpio.output(_return,frequency)
            wait(_range)
            t += _range

class RGBLED:
    def __init__(self,R_GPIO:GPIO,G_GPIO:GPIO,B_GPIO:GPIO):
        self.R_GPIO = R_GPIO
        self.G_GPIO = G_GPIO
        self.B_GPIO = B_GPIO
        
        self.R_GPIO.output(0)
        self.G_GPIO.output(0)
        self.B_GPIO.output(0)

        self.R_GPIO_STATE = False
        self.G_GPIO_STATE = False
        self.B_GPIO_STATE = False
    
    def lightUp(self,R_brightness,G_brightness,B_brightness,frequency=None):
        self.R_GPIO.output(R_brightness,frequency)
        self.G_GPIO.output(G_brightness,frequency)
        self.B_GPIO.output(B_brightness,frequency)

        self.R_GPIO_STATE = bool(R_brightness)
        self.G_GPIO_STATE = bool(G_brightness)
        self.B_GPIO_STATE = bool(B_brightness)
    
    def flashing(self,t,times=1):
        for _ in range(times):
            self.R_GPIO.output(1)
            self.G_GPIO.output(1)
            self.B_GPIO.output(1)
            self.R_GPIO_STATE = True
            self.G_GPIO_STATE = True
            self.B_GPIO_STATE = True
            wait(t)
            self.R_GPIO.output(0)
            self.G_GPIO.output(0)
            self.B_GPIO.output(0)
            self.R_GPIO_STATE = False
            self.G_GPIO_STATE = False
            self.B_GPIO_STATE = False
            wait(t)
    
    def control(self,function,_range=1000,frequency=100):
        t = 0
        while True:
            _return = function(t)
            if _return is None:
                break
            self.R_GPIO.output(_return[0],frequency)
            self.G_GPIO.output(_return[1],frequency)
            self.B_GPIO.output(_return[2],frequency)
            self.R_GPIO_STATE = bool(_return[0])
            self.G_GPIO_STATE = bool(_return[1])
            self.B_GPIO_STATE = bool(_return[2])           
            wait(_range)
            t += _range


class PassiveBuzzer:
    def __init__(self,gpio:GPIO):
        self.gpio = gpio
        self.gpio.output(0)
    def beep(self,frequency,volume=0.5,t=1000):
        if frequency == 0:
            self.gpio.output(0)
            wait(t)
        else:
            self.gpio.output(volume,frequency)
            wait(t)
            self.gpio.output(0)
    def beeps(self,spectrum:list):
        for i in spectrum:
            if i[0] == 0:
                self.gpio.output(0)
            else:
                self.gpio.output(i[1],i[0])  # 格式：(频率,响度,持续时间)
            wait(i[2])
        self.gpio.output(0)
    def stop(self):
        self.gpio.output(0)

class ActiveBuzzer:
    def __init__(self,gpio:GPIO):
        self.gpio = gpio
        self.gpio.output(0)
    def beep(self,volume=1,t=1000):
        # 有源蜂鸣器无法通过PWM频率改变声音音调，因此此处无frequency
        if volume in (0,1):
            fre = None
        else:
            fre = 1000
        self.gpio.output(volume,fre)
        wait(t)
        self.gpio.output(0)
    def beeps(self,spectrum:list):
        for i in spectrum:
            self.beep(i[0],i[1]) # 格式：(响度,持续时间)
    def stop(self):
        self.gpio.output(0)


def toBoard(BCM):
    return bcm_to_board[BCM]

def toBcm(board):
    return board_to_bcm[board]


def close():
    GPI.cleanup()

def wait(t): # ms为单位
    time.sleep(t/1000)