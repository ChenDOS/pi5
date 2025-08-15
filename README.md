# pi5
A simple, powerful Raspberry Pi GPIO operation library
depend lib: RPi.GPIO,board,adafruit_dht

---

# Pi5 GPIO Class Documentation

## Quick Start

### Controlling an LED

```python
from pi5 import GPIO, wait

led = GPIO(BCM=18)      # Use BCM pin 18
led.output(1)           # Set HIGH to turn on (no need to manually configure I/O mode - pi5 handles it automatically)
wait(1000)              # Wait 1 second
led.output(0)           # Turn off
```

### Reading Button State

```python
button = GPIO(board=11)   # Use BOARD pin 11
print(button.Input())     # Read current level (capitalized to avoid conflict with Python's built-in `input`)
```

## Core Features

### 1. Pin Initialization

Supports **BCM** and **BOARD** numbering modes:

```python
# BCM mode (recommended)
gpio_bcm = GPIO(BCM=18)

# BOARD mode
gpio_board = GPIO(board=12)
```

### 2. Output Control

#### Digital Output

```python
gpio = GPIO(BCM=17)
gpio.output(1)  # HIGH
gpio.output(0)  # LOW
```

#### PWM Output

```python
gpio = GPIO(BCM=18)
gpio.output(0.5, frequency=100)  # 50% duty cycle, 100Hz frequency
```

### 3. Input Detection

Supports pull-up/pull-down resistor configuration:

```python
# No pull (capitalized to avoid Python keyword conflict)
val = gpio.Input()  

# Enable pull-up
val = gpio.Input(resistance=pi5.PUD_UP)

# Enable pull-down
val = gpio.Input(resistance=pi5.PUD_DOWN)
```

### 4. Event Callback System

#### Event Type Constants

```python
from pi5 import (
    EVENT_RISING,       # Rising edge
    EVENT_FALLING,      # Falling edge
    EVENT_BOTH          # Both edges
)
```

#### Registering Callbacks

```python
def on_rise():
    print("Rising edge detected!")

callback_id = gpio.addEvent(EVENT_RISING, on_rise)
```

#### Event Detection Control

```python
# With debounce (50ms) and pull-up
gpio.runEvents(resistance=pi5.PUD_UP, bouncetime=50)

# Stop detection
gpio.stopEvents()
```

#### Complete Example

```python
from pi5 import GPIO, EVENT_RISING, wait

btn = GPIO(BCM=23)

def button_pressed():
    print("Button pressed!")

btn.addEvent(EVENT_RISING, button_pressed)
btn.runEvents(resistance=pi5.PUD_DOWN)

try:
    while True:
        wait(100)
except KeyboardInterrupt:
    btn.stopEvents()
```

## Advanced Features

### Multi-Callback Management

```python
# Add callbacks
id1 = gpio.addEvent(EVENT_RISING, callback1)
id2 = gpio.addEvent(EVENT_FALLING, callback2)

# Remove specific callback
gpio.removeEvent(id1)

# Clear all callbacks
gpio.clearEvents()
```

### Resource Cleanup

```python
# Safely stop single pin
gpio.stop()

# Clean all GPIO resources
pi5.close()
```

### Pin Conversion

```python
print(pi5.toBcm(12))    # Convert BOARD to BCM → 18
print(pi5.toBoard(18))   # Convert BCM to BOARD → 12
gpio = pi5.GPIO(BCM=18)
print(gpio.BCM)         # Get BCM code → 18
print(gpio.board)       # Get BOARD code → 12
```

# LED Class

### Lighting an LED

```python
import pi5
gpio18 = pi5.GPIO(18)  # LED GPIO
led = pi5.LED(gpio18)
led.lightUp(1)         # Max brightness (100%)
led.lightUp(0.3, 1000) # Set to 30% brightness, 1kHz PWM
print(led.state)       # LED status (True=ON, False=OFF)
```

### LED Blinking

```python
led.flashing(500, 6)   # Blink 6 times with 500ms intervals
```

### Advanced LED Control

```python
# Linear breathing template (t = time in ms)
def linear_breath(t):
    if t == 10*1000:
        return None    # Exit after 10s
    cycle = t % 200
    brightness = cycle/100 if cycle <= 100 else (200-cycle)/100
    return brightness

led.control(function=linear_breath, _range=500, frequency=1000)  # 500ms interval, 1kHz PWM
```

# RGB LED Class

### Controlling RGB LED Module

```python
import pi5
gpio17 = pi5.GPIO(17)  # Red
gpio27 = pi5.GPIO(27)  # Green
gpio22 = pi5.GPIO(22)  # Blue
rgb = pi5.RGBLED(gpio17, gpio27, gpio22)
rgb.lightUp(R_brightness=1, G_brightness=0, B_brightness=1)  # Purple
rgb.lightUp(R=0.2, G=0.3, B=0.7, frequency=1000)  # 1kHz PWM
print(rgb.G_GPIO_STATE)  # Green channel status
rgb.flashing(500, 6)     # Blink 6 times
```

### Advanced RGB Control: Random Colors

```python
import random
def func(t):
    if t >= 20*1000:
        return None
    return (random.random(), random.random(), random.random())  # Random RGB

rgb.control(function=func, _range=500, frequency=1000)
```

# PassiveBuzzer Class

### Overview

Driver for passive buzzers supporting:
- Single-tone playback
- Tone sequence playback

---

## Quick Start

### Basic Beep

```python
from pi5 import GPIO, PassiveBuzzer

buzzer = PassiveBuzzer(GPIO(BCM=18))
buzzer.beep(1000)          # 1kHz, 1s, 50% volume
buzzer.beep(880, 0.3, 500) # 880Hz, 500ms, 30% volume
```

---

## Core Methods

### 1. `beep(frequency, volume=0.5, t=1000)`
Play single tone

| Parameter  | Type  | Default | Description          |
|------------|-------|---------|----------------------|
| frequency  | int   | Required| 0-20kHz (Hz)         |
| volume     | float | 0.5     | 0.0-1.0              |
| t          | int   | 1000    | Duration (ms)        |

**Example**:
```python
# Alarm sound
buzzer.beep(2000, volume=0.8, t=200)
```

---

### 2. `beeps(spectrum:list)`
Play tone sequence

| Parameter | Type       | Description                     |
|-----------|------------|---------------------------------|
| spectrum  | list[tuple]| (freq, volume, duration) tuples |

**Example**:
```python
alarm_pattern = [
    (2000, 0.7, 200),  # 2kHz 70% 200ms
    (0, 0, 100),        # Silence
    (2000, 0.7, 200),
    (0, 0, 100)
]
buzzer.beeps(alarm_pattern)
```

### 3. `stop()` - Stop playback
```python
buzzer.stop()
```

# ActiveBuzzer Class

## Core Features

The `ActiveBuzzer` class provides simple control for active buzzers (alarms/notifications).

### Initialization
```python
buzzer = ActiveBuzzer(GPIO(BCM=18))
```

### Method Reference
| Method | Parameters | Description |
|--------|------------|-------------|
| `beep(volume=1, t=1000)` | volume: 0.0-1.0<br>t: milliseconds | Single beep (auto-off) |
| `beeps(spectrum)` | [(volume, t_ms), ...] | Play sequence |
| `stop()` | None | Force stop |

## Best Practices

### 1. Basic Beep
```python
# Short beep
buzzer.beep(t=100)

# Gradual increase
buzzer.beeps([(i*0.1, 50) for i in range(1,11)])
```

### 2. Alarm Patterns
```python
# Emergency alert
alert = [(1,100), (0,50)] * 5
buzzer.beeps(alert)

# Breathing effect
breath = [(math.sin(i/5)*0.5+0.5, 50) for i in range(30)]
buzzer.beeps(breath)
```

### 3. Composite Sounds
```python
# System check sound
self_test = [
    (0.3, 200), (0, 100),
    (0.6, 200), (0, 100),
    (1.0, 500)
]
buzzer.beeps(self_test)
```

# Pi5 Extensions
#### pi5 supports official/third-party extensions
---

# DHT11 Extension (Official)

## Basic Usage
```python
import pi5_DHT11
dht = pi5_DHT11.DHT11(GPIO(BCM=18))
print(dht.get())            # (temperature, humidity)
print(dht.getTemperature()) # Temperature only
print(dht.getHumidity())    # Humidity only
```

---
