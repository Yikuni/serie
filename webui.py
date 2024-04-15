import gradio as gr
import time
import threading
import logging

import serie.connection


# 读取日志
def read_log():
    with open('log.log', 'r') as file:
        return file.read()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                        format="%(asctime)s - %(name)-20s - %(levelname)-9s: %(message)s"
                        , datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    logging.getLogger().addHandler(console)

    with gr.Blocks() as app:
        gr.Markdown("""
            # 3组水下机器人控制面板 
        """
                    )
        # 连接按钮
        start_conn = gr.Button("建立连接")
        dis_conn = gr.Button("断开连接")
        gr.update(dis_conn.elem_id, visible=False)
        def connect_button_event():
            if serie.connection.is_connected():
                serie.connection.close_conn()
                gr.update(dis_conn.elem_id, visible=False)
                gr.update(start_conn.elem_id, visible=True)
            else:
                serie.connection.connect(port_index=1)
                gr.update(dis_conn.elem_id, visible=True)
                gr.update(start_conn.elem_id, visible=False)

        start_conn.click(fn=connect_button_event)
        dis_conn.click(fn=connect_button_event)


        # LED灯
        led = gr.Checkbox(value=False, label="LED灯")
        led.change(fn=serie.command.led, inputs=led)
        for i in range(0, 6):
            def set_pwm(speed):
                serie.command.set_pwm(i, speed)


            slider = gr.Slider(minimum=0, maximum=499, value=50, label=f"pwm{i} 占空比")
            slider.change(fn=set_pwm, inputs=slider)
        log_area = gr.TextArea(lines=10, value=read_log, every=0.3, interactive=False)



    app.launch()
