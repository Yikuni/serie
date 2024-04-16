import gradio as gr
import time
import threading
import logging

import serie.connection


# 读取日志
def read_log():
    with open('log.log', 'r') as file:
        return file.read()

port_i_value = 0

def tab_main():
    # 连接按钮
    with gr.Row():
        start_conn = None

        def get_conn_label():
            return "断开连接" if serie.connection.is_connected() else "建立连接"

        with gr.Column(scale=1):
            gr.TextArea(value=serie.connection.get_ports, every=0.5, label="端口信息", interactive=False)
        with gr.Column(scale=1):
            port_i = gr.Number(label="选择的端口索引", value=port_i_value)

            def update_port_value(value):
                global port_i_value
                port_i_value = value

            port_i.change(fn=update_port_value, inputs=port_i)
        with gr.Column(scale=1):
            start_conn = gr.Button(value=get_conn_label, every=0.5)
        with gr.Column(scale=1):
            gr.Checkbox(value=serie.connection.is_connected, every=0.5, label="连接状态")

        def connect_button_event():
            if serie.connection.is_connected():
                serie.connection.close_conn()
            else:
                serie.connection.connect(port_index=port_i_value)

        start_conn.click(fn=connect_button_event)

    # LED灯
    led = gr.Checkbox(value=False, label="LED灯")
    led.change(fn=serie.command.led, inputs=led)

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


def tab_motion():
    gr.Image(value=serie.data.motion_history_plot, label="速度图像", every=1)



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

    app.launch()


if __name__ == "__main__":
    main()
