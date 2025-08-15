from pi5 import GPIO, wait, PUD_UP
import board
import time
import adafruit_dht

class DHT11:
    def __init__(self, gpio):
        self.gpio = gpio
        # 在初始化时创建DHT设备对象
        pin = getattr(board, f"D{self.gpio.BCM}")
        self.dhtDevice = adafruit_dht.DHT11(pin)

    def getTemperature(self):
        return self.get()[0]
    
    def getHumidity(self):
        return self.get()[1]
        
    def get(self):
        try:
            temperature = self.dhtDevice.temperature
            humidity = self.dhtDevice.humidity
            return (temperature, humidity)
        except RuntimeError as e:
            print(f"读取失败: {e}")
            return (None, None)
        except Exception as e:
            print(f"错误: {e}")
            return (None, None)
