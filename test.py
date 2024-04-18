import numpy as np

# 变量定义
Kp = 100.0                        # 比例增益支配率收敛到加速度计/磁强计
Ki = 0.002                # 积分增益支配率的陀螺仪偏见的衔接
halfT = 0.001                # 采样周期的一半

q0, q1, q2, q3 = 1, 0, 0, 0          # 四元数的元素，代表估计方向
exInt, eyInt, ezInt = 0, 0, 0        # 按比例缩小积分误差

Yaw, Pitch, Roll = 0, 0, 0  # 偏航角，俯仰角，翻滚角
# 加速度单位g，陀螺仪rad/s
def IMUupdate(gx, gy, gz, ax, ay, az):
    global q0, q1, q2, q3, exInt, eyInt, ezInt, Yaw, Pitch, Roll

    # 测量正常化
    norm = np.sqrt(ax*ax + ay*ay + az*az)
    ax, ay, az = ax / norm, ay / norm, az / norm

    # 估计方向的重力
    vx = 2*(q1*q3 - q0*q2)
    vy = 2*(q0*q1 + q2*q3)
    vz = q0*q0 - q1*q1 - q2*q2 + q3*q3

    # 错误的领域和方向传感器测量参考方向之间的交叉乘积的总和
    ex = (ay*vz - az*vy)
    ey = (az*vx - ax*vz)
    ez = (ax*vy - ay*vx)

    # 积分误差比例积分增益
    exInt += ex*Ki
    eyInt += ey*Ki
    ezInt += ez*Ki

    # 调整后的陀螺仪测量
    gx = gx + Kp*ex + exInt
    gy = gy + Kp*ey + eyInt
    gz = gz + Kp*ez + ezInt

    # 整合四元数率和正常化
    q0 += (-q1*gx - q2*gy - q3*gz)*halfT
    q1 += (q0*gx + q2*gz - q3*gy)*halfT
    q2 += (q0*gy - q1*gz + q3*gx)*halfT
    q3 += (q0*gz + q1*gy - q2*gx)*halfT

    # 正常化四元
    norm = np.sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3)
    q0, q1, q2, q3 = q0 / norm, q1 / norm, q2 / norm, q3 / norm

    Pitch = np.arcsin(-2 * q1 * q3 + 2 * q0 * q2) * 57.3  # pitch, 转换为度数
    Roll = np.arctan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2 * q2 + 1) * 57.3  # roll
    Yaw = np.arctan2(2*(q1*q2 + q0*q3), q0*q0+q1*q1-q2*q2-q3*q3) * 57.3