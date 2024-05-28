import gradio as gr
import time
import threading
import logging

import serie.connection
from serie.motion import MotionState, MotionController

# 读取日志
def read_log():
    with open('log.log', 'r') as file:
        return file.read()


port_i_value = 0


def tab_main():
    # 连接按钮
    with gr.Row():
        def get_conn_label():
            return "断开连接" if serie.connection.is_connected() else "建立连接"

        with gr.Column(scale=1):
            gr.TextArea(value=serie.connection.get_ports, every=0.5, label="端口信息", interactive=False, lines=2)
            gr.Checkbox(value=serie.connection.is_connected, every=0.5, label="连接状态")
        with gr.Column(scale=1):
            port_name = gr.Textbox(value="/dev/ttyS5", interactive=True)
            port_name_button = gr.Button("通过端口名称连接")
            def connect_through_name():
                serie.connection.connect(device_name=port_name.value)
            port_name_button.click(fn=connect_through_name)
        with gr.Column(scale=1):
            port_i = gr.Number(label="选择的端口索引", value=port_i_value)

            def update_port_value(value):
                global port_i_value
                port_i_value = value

            port_i.change(fn=update_port_value, inputs=port_i)
            start_conn = gr.Button(value=get_conn_label, every=0.5)

            def connect_button_event():
                if serie.connection.is_connected():
                    serie.connection.close_conn()
                else:
                    serie.connection.connect(port_index=port_i_value)

            start_conn.click(fn=connect_button_event)
        with gr.Column(scale=1):
            gr.Button(value="初始化dmp").click(fn=serie.command.init_dmp)
            gr.Button(value="结束dmp更新").click(fn=serie.command.stop_dmp)
            gr.Button(value="初始化水压传感器").click(fn=serie.command.init_ms5837)
    # LED灯
    with gr.Row():
        led = gr.Checkbox(value=False, label="LED灯")
        led.change(fn=serie.command.led, inputs=led)

        def led2():
            for _ in range(2):
                serie.command.led(False)
                time.sleep(0.5)
                serie.command.led(True)
                time.sleep(0.5)
            serie.command.led(False)

        def led3():
            for _ in range(3):
                serie.command.led(False)
                time.sleep(0.5)
                serie.command.led(True)
                time.sleep(0.5)
            serie.command.led(False)

        gr.Button("LED灯闪2下").click(fn=led2)
        gr.Button("LED灯闪3下").click(fn=led3)

    with gr.Row():
        with gr.Column(scale=1):
            # pwm
            def set_pwm(label, slider):
                serie.command.set_pwm(label, slider)

            for i in range(0, 6):
                label = gr.Number(value=i, interactive=False, visible=False)
                slider = gr.Slider(minimum=0, maximum=499, value=50, label=f"pwm{i} 占空比")
                slider.change(fn=set_pwm, inputs=[label, slider])
        with gr.Column(scale=2):
            # 日志
            gr.TextArea(lines=15, value=read_log, every=0.3, interactive=False, max_lines=15)

    def get_pressure():
        return serie.data.pressure

    with gr.Row():
        with gr.Column(scale=1):
            # 压强
            gr_button = gr.Button(value="获取压强")
            gr_button.click(fn=serie.command.get_pressure)
            gr.Number(value=get_pressure, interactive=False, every=0.3, label="压强(mbar)")
        with gr.Column(scale=1):
            # 向lora送信
            text = gr.Text(placeholder="消息格式：指令;", label="向lora送信")
            gr_button = gr.Button(value="送信")
            gr_button.click(fn=serie.command.send_lora_msg, inputs=text)

def plot_thread():
    while serie.data.motion_t is not None and serie.data.motion_t.is_alive():
        time.sleep(0.5)
        serie.data.motion_history_plot()
        serie.data.raw_motion_history_plot()
        serie.data.motion_history_plot2()
        serie.data.raw_motion_history_plot2()


def plot_name_1():
    return "motion.png"

def plot_name_2():
    return "raw_motion.png"

def plot_name_3():
    return "motion2.png"

def plot_name_4():
    return "raw_motion2.png"

def tab_motion():
    with gr.Row():
        with gr.Column(scale=1):
            motion_button = gr.Button("开启速度解算进程", every=1)

            def motion_button_event():
                if not serie.data.is_motion_t_alive():
                    serie.data.start_motion_thread()
                    time.sleep(0.5)
                    thread = threading.Thread(target=plot_thread)
                    thread.start()
            motion_button.click(fn=motion_button_event)
        with gr.Column(scale=1):
            gr.Button("清空姿态数据").click(fn=serie.data.motion_calculator.clear_data)
        with gr.Column(scale=1):
            offset_button = gr.Button(value="校准速度误差")
            offset_button.click(fn=serie.data.motion_calculator.correct_raw_motion)
        with gr.Column(scale=1):
            gr.Checkbox(label="速度解算线程状态", interactive=False, every=1, value=serie.data.is_motion_t_alive)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(value=plot_name_1, label="速度图像", every=1)
        with gr.Column(scale=1):
            gr.Image(value=plot_name_2, label="加速度图像", every=1)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(value=plot_name_3, label="角度图像", every=1)
        with gr.Column(scale=1):
            gr.Image(value=plot_name_4, label="角速度图像", every=1)


def tab_pwm_control():
    mc = MotionController()
    with gr.Row():
        gr.Button("初始化").click(fn=mc.init_pwm)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Textbox(label="状态1", value=mc.state1.name, every=1)
        with gr.Column(scale=1):
            with gr.Row():
                def update_state1():
                    mc.update_state(MotionState.STOP)
                gr.Button("停止").click(fn=update_state1)
                def update_state2():
                    mc.update_state(MotionState.NO_TURN)
                gr.Button("直行").click(fn=update_state2)
        with gr.Column(scale=1):
            with gr.Row():
                def update_state3():
                    mc.update_state(MotionState.TURN_LEFT)
                gr.Button("左转").click(fn=update_state3)
                def update_state4():
                    mc.update_state(MotionState.TURN_RIGHT)
                gr.Button("右转").click(fn=update_state4)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Textbox(label="状态2", value=mc.state2.name, every=1)
        with gr.Column(scale=1):
            with gr.Row():
                def update_state5():
                    mc.update_state(MotionState.NO_TILT)
                gr.Button("不倾斜").click(fn=update_state5)
                def update_state6():
                    mc.update_state(MotionState.TILT_RIGHT)
                gr.Button("右倾").click(fn=update_state6)
        with gr.Column(scale=1):
            def update_state7():
                mc.update_state(MotionState.TILT_LEFT)
            gr.Button("左倾").click(fn=update_state7)
def main():
    # 配置日志
    logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w+',
                        format="%(asctime)s - %(name)-20s - %(levelname)-9s: %(message)s"
                        , datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    logging.getLogger().addHandler(console)

    with gr.Blocks() as app:
        gr.Markdown("""
                # 3组水下机器人控制面板 
            """
                    )
        with gr.Tab(label="主面板"):
            tab_main()
        with gr.Tab(label="姿态数据"):
            tab_motion()
        with gr.Tab(label="推进器控制"):
            tab_pwm_control()

    app.launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
