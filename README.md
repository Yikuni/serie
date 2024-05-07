# 赛丽艾模块使用说明

---

## 安装

环境要求：python3

~~~ sh
pip install -r requirements.txt
~~~

## 打开控制面板

``` sh
python webui.py
```

然后在电脑上用浏览器打开 http://127.0.0.1:7860，其中ip要替换为树莓派的局域网ip

## 连接

### 建立连接
```python
serie.connection.connect(device_name="/dev/ttyS5") # 建立连接

serie.connection.close_conn()   # 断开连接
```


## 指令

>  赛丽艾通过指令控制stm32做出相应行动

### LED灯

消息：led on/off

返回消息：ret_msg led on/off

``` python
serie.command.led(true)	# 亮灯
serie.command.led(false)	# 灭灯
```

### 获取压强

__第一次获取压强前需要初始化__：

初始化最多耗时5秒

``` python
serie.command.init_ms5837()
```

> 获取压强存在一定的延迟(<0.04s)，需要传入一个callback函数，该函数接受一个float参数，会在获取到压强后自动执行
> - 该函数会在读取消息线程中运行，请不要安排耗时长的任务！！！
``` python
def callback_method(pressure):
    logger.info("pressure: " + str(pressure))
serie.command.get_pressure(callback_method)
```
压强单位：mbar，即$ 10^{-2} Pa $

### 推进器

消息：pwm set/get

返回消息：在pwm set时返回ret_msg pwm index speed

- 设置推进器：pwm set 推进器id 占空比
- 获取推进器占空比：pwm get

``` python
# 更新pwm速度，基本用不到
serie.command.update_pwm()
# 获取pwm
time.sleep(0.03)
pwm_info = serie.data.pwm_info
# 设置pwm
serie.command.set_pwm(0, 100)
```
### 与lora通信

``` python
msg = "this is a message"
serie.command.send_lora_msg(msg)
```
### 姿态

#### 初始化

初始化最多耗时5s

``` python
serie.command.init_dmp()	# 初始化dmp
time.sleep(5)
serie.data.start_motion_thread()	# 开启读取stm32姿态数据的进程
```

如果初始化失败或程序停止，需要停止stm32内的dmp自动更新：

~~~python
serie.command.stop_dmp()
~~~

#### 消除误差

由于mpu6050存在一定的误差，所以在初始化完毕后大约10s需要进行纠正

``` python
serie.data.motion_calculator.correct_raw_motion()
```

#### 获取角度和速度

下面两项的类型都是numpy.ndarray，shape为(3,)

``` python
angle = serie.data.motion_calculator.angle
velocity = serie.data.motion_calculator.velocity
```

## 附加功能

### 监听响应消息

树莓派在接收到指令后一般会回传一个消息表明收到指令，可以对消息进行监听：

~~~python
from serie import data

def dmp_init_listener(msg):
    if msg.startswith('ret_msg dmp init success'):
        time.sleep(3)
        serie.command.start_dmp()


data.add_ret_msg_analyzer(dmp_init_listener)
~~~

