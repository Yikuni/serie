from serie.motion import MotionController, MotionState

mc = MotionController()  # 初始化MotionController对象，保存在全局
mc.update_state(MotionState.TILT_LEFT)  # 需要改变姿态的时候调用
