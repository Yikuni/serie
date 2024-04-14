# 赛丽艾模块使用说明
## 连接
### 建立连接
```python
serie.connection.connect()  # 建立连接

serie.connection.close_conn()   # 断开连接
```
## 指令
>  赛丽艾通过指令控制stm32做出相应行动

### LED灯

消息：led on/off

返回消息：ret_msg led on/off

``` python
led(true)	# 亮灯
led(false)	# 灭灯
```

### 姿态

消息：motion

返回：data motion 6轴float数据

更新流程：data.py中启动motion_thread，每一定时间发送motion消息 --> connection.py中的read_thread读取到data消息后通知data.py中的analyze分析消息，从而更新加速度，再更新速度

#### 获取速度和角度

``` python
serie.data.motion	# numpy数组 (6,) dtype=float16，前三个是三轴速度，后三个是三轴角度
```

#### 获取加速度和角速度

``` python
serie.data.raw_motion	# numpy数组 (6,) dtype=float16，前三个是三轴加速度，后三个是三轴角速度
```

### 推进器

消息：pwm set/get

返回消息：在pwm set时返回ret_msg pwm index speed

- 设置推进器：pwm set 推进器id 占空比
- 获取推进器占空比：pwm get

``` python
# 更新pwm速度，基本用不到
serie.command.update_pwm()
# 获取pwm
time.sleep(0.01)
pwm_info = serie.data.pwm_info
# 设置pwm
serie.command.set_pwm(0, 100)
```

## TODO

- pwm设置的数值比较魔幻
- mpu6050数值偏差有点大
