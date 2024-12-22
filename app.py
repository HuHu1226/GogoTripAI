#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024.4.16
# @Author  : HinGwenWong

import copy
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
import yaml

from utils.web_configs import WEB_CONFIGS

# 初始化 Streamlit 页面配置
st.set_page_config(
    page_title="大咖伴游",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/dashan336/TripBuddyAI/",
        "Report a bug": "https://github.com/PeterH0323/Streamer-Sales/issues",
        "About": "# 大咖伴游",
    },
)
from utils.rag.rag_worker import gen_rag_db
from utils.tools import resize_image

from utils.model_loader import RAG_RETRIEVER  # isort:skip


@st.experimental_dialog("讲解", width="large")
def instruction_dialog(instruction_path):
    """
    显示街道说明书的popup窗口。

    通过给定的说明书路径，将文件内容以markdown格式在Streamlit应用中显示出来，并提供一个“确定”按钮供用户确认阅读。

    Args:
        instruction_path (str): 说明书的文件路径，该文件应为文本文件，并使用utf-8编码。
    """
    print(f"Show instruction : {instruction_path}")
    with open(instruction_path, "r", encoding="utf-8") as f:
        instruct_lines = "".join(f.readlines())

    st.warning("一定要点击下方的【确定】按钮离开该页面", icon="⚠️")
    st.markdown(instruct_lines)
    st.warning("一定要点击下方的【确定】按钮离开该页面", icon="⚠️")
    if st.button("确定"):
        st.rerun()


def on_btton_click(*args, **kwargs):
    """
    按钮点击事件的回调函数。
    """

    # 根据按钮类型执行相应操作
    if kwargs["type"] == "check_instruction":
        # 显示说明书
        st.session_state.show_instruction_path = kwargs["instruction_path"]

    elif kwargs["type"] == "process_sales":
        # 切换到主播卖货页面
        st.session_state.page_switch = "pages/selling_page.py"

        # 更新会话状态中的街道信息
        st.session_state.hightlight = kwargs["heighlights"]
        street_info_struct = copy.deepcopy(st.session_state.street_info_struct_template)
        street_info_str = street_info_struct[0].replace("{name}", kwargs["street_name"])
        street_info_str += street_info_struct[1].replace("{highlights}", st.session_state.hightlight)

        # 生成街道文案 prompt
        st.session_state.first_input = copy.deepcopy(st.session_state.first_input_template).replace(
            "{street_info}", street_info_str
        )

        # 更新图片路径和街道名称
        st.session_state.image_path = kwargs["image_path"]
        st.session_state.street_name = kwargs["street_name"]

        # 更新发货地、快递公司名称
        st.session_state.departure_place = kwargs["departure_place"]
        st.session_state.delivery_company_name = kwargs["delivery_company_name"]

        # 设置为默认数字人视频路径
        st.session_state.digital_human_video_path = WEB_CONFIGS.DIGITAL_HUMAN_VIDEO_PATH

        # # 清空语音
        # if ENABLE_TTS:
        #     for message in st.session_state.messages:
        #         if "wav" not in message:
        #             continue
        #         Path(message["wav"]).unlink()

        # 清空历史对话
        st.session_state.messages = []


def make_street_container(street_name, street_info, image_height, each_card_offset):
    """
    创建并展示街道信息容器。

    参数:
    - street_name: 街道名称。
    - street_info: 包含街道具体位置、附近景点信息，美食信息，以及历史背景。
    - image_height: 图片展示区域的高度。
    - each_card_offset: 容器内各部分间距。
    """

    # 创建带边框的街道信息容器，设置高度
    with st.container(border=True, height=image_height + each_card_offset):

        # 页面标题
        st.header(street_name)
        heighlights_str = "、".join(street_info["heighlights"])
        st.button(
            "主播讲解",
            key=f"process_sales_{street_name}",
            on_click=on_btton_click,
            kwargs={
                "type": "process_sales",
                "street_name": street_name,
                "heighlights": heighlights_str,
                "image_path": street_info["images"],
                "departure_place": street_info["departure_place"],
                "delivery_company_name": street_info["delivery_company_name"],
            },
        )
        # 划分左右两列，左侧为图片，右侧为街道信息
        info_col, image_col  = st.columns([0.7, 0.3])

        # 图片展示区域
        with image_col:
            # print(f"Loading {street_info['images']} ...")
            image = resize_image(street_info["images"], max_height=500)
            st.image(image, use_container_width=True , channels="bgr")

        # 街道信息展示区域
        with info_col:

            # 亮点展示
            st.subheader("街道简介", divider="grey")

            
            st.text(heighlights_str)

            # 说明书按钮
            st.subheader("街道详情介绍", divider="grey")
            st.text('1')
            st.button(
                "查看",
                key=f"check_instruction_{street_name}",
                on_click=on_btton_click,
                kwargs={
                    "type": "check_instruction",
                    "street_name": street_name,
                    "instruction_path": street_info["instruction"],
                },
            )
            # st.button("更新", key=f"update_manual_{street_name}")

            # 讲解按钮
            # st.subheader("主播", divider="grey")
            # st.button(
            #     "开始讲解",
            #     key=f"process_sales_{street_name}",
            #     on_click=on_btton_click,
            #     kwargs={
            #         "type": "process_sales",
            #         "street_name": street_name,
            #         "heighlights": heighlights_str,
            #         "image_path": street_info["images"],
            #         "departure_place": street_info["departure_place"],
            #         "delivery_company_name": street_info["delivery_company_name"],
            #     },
            # )


def delete_old_files(directory, limit_time_s=60 * 60 * 5):
    """
    删除指定目录下超过一定时间的文件。

    :param directory: 要检查和删除文件的目录路径
    """
    # 获取当前时间戳
    current_time = time.time()

    # 遍历目录下的所有文件和子目录
    for file_path in Path(directory).iterdir():

        # 获取文件的修改时间戳
        file_mtime = os.path.getmtime(file_path)

        # 计算文件的年龄（以秒为单位）
        file_age_seconds = current_time - file_mtime

        # 检查文件是否超过 n 秒
        if file_age_seconds > limit_time_s:
            try:

                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    continue

                # 删除文件
                file_path.unlink()
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")


def get_sales_info():
    """
    从配置文件中加载销售相关信息，并存储到session状态中。

    该函数不接受参数，也不直接返回任何值，但会更新全局的session状态，包括：
    - sales_info: 系统问候语，针对销售角色定制
    - first_input_template: 对话开始时的第一个输入模板
    - street_info_struct_template: 街道信息结构模板

    """

    # 加载对话配置文件
    with open(WEB_CONFIGS.CONVERSATION_CFG_YAML_PATH, "r", encoding="utf-8") as f:
        dataset_yaml = yaml.safe_load(f)

    # 从配置中提取角色信息
    sales_info = dataset_yaml["role_type"][WEB_CONFIGS.SALES_NAME]

    # 从配置中提取对话设置相关的信息
    system = dataset_yaml["conversation_setting"]["system"]
    first_input = dataset_yaml["conversation_setting"]["first_input"]
    street_info_struct = dataset_yaml["street_info_struct"]

    # 将销售角色名和角色信息插入到 system prompt
    system_str = system.replace("{role_type}", WEB_CONFIGS.SALES_NAME).replace("{character}", "、".join(sales_info))

    # 更新session状态，存储销售相关信息
    st.session_state.sales_info = system_str
    st.session_state.first_input_template = first_input
    st.session_state.street_info_struct_template = street_info_struct


def init_street_info():
    # 读取 yaml 文件
    with open(WEB_CONFIGS.street_info_YAML_PATH, "r", encoding="utf-8") as f:
        street_info_dict = yaml.safe_load(f)

    # 根据 ID 排序，避免乱序
    street_info_dict = dict(sorted(street_info_dict.items(), key=lambda item: item[1]["id"]))

    street_name_list = list(street_info_dict.keys())

    # 生成街道信息
    for row_id in range(0, len(street_name_list), WEB_CONFIGS.EACH_ROW_COL):
        for col_id, col_handler in enumerate(st.columns(WEB_CONFIGS.EACH_ROW_COL)):
            with col_handler:
                if row_id + col_id >= len(street_name_list):
                    continue

                street_name = street_name_list[row_id + col_id]
                make_street_container(
                    street_name, street_info_dict[street_name], WEB_CONFIGS.street_IMAGE_HEIGHT, WEB_CONFIGS.EACH_CARD_OFFSET
                )

    return len(street_name_list)


def init_tts():
    # TTS 初始化
    if "gen_tts_checkbox" not in st.session_state:
        st.session_state.gen_tts_checkbox = WEB_CONFIGS.ENABLE_TTS
    if WEB_CONFIGS.ENABLE_TTS:
        # 清除 1 小时之前的所有语音
        Path(WEB_CONFIGS.TTS_WAV_GEN_PATH).mkdir(parents=True, exist_ok=True)
        delete_old_files(WEB_CONFIGS.TTS_WAV_GEN_PATH)


def init_digital_human():
    # 数字人 初始化
    if "digital_human_video_path" not in st.session_state:
        st.session_state.digital_human_video_path = WEB_CONFIGS.DIGITAL_HUMAN_VIDEO_PATH
    if "gen_digital_human_checkbox" not in st.session_state:
        st.session_state.gen_digital_human_checkbox = WEB_CONFIGS.ENABLE_DIGITAL_HUMAN

    if WEB_CONFIGS.ENABLE_DIGITAL_HUMAN:
        # 清除 1 小时之前的所有视频
        Path(WEB_CONFIGS.DIGITAL_HUMAN_GEN_PATH).mkdir(parents=True, exist_ok=True)
        # delete_old_files(st.session_state.digital_human_root)


def init_asr():
    # 清理 ASR 旧文件
    if WEB_CONFIGS.ENABLE_ASR and Path(WEB_CONFIGS.ASR_WAV_SAVE_PATH).exists():
        delete_old_files(WEB_CONFIGS.ASR_WAV_SAVE_PATH)

    st.session_state.asr_text_cache = ""


def main():
    """
    初始化页面配置，加载模型，处理页面跳转，并展示街道信息。
    """
    print("Starting...")

    # 初始化页面跳转
    if "page_switch" not in st.session_state:
        st.session_state.page_switch = "app.py"
    st.session_state.current_page = "app.py"

    # 显示街道介绍
    if "show_instruction_path" not in st.session_state:
        st.session_state.show_instruction_path = "X-X"
    if st.session_state.show_instruction_path != "X-X":
        instruction_dialog(st.session_state.show_instruction_path)
        st.session_state.show_instruction_path = "X-X"

    # 判断是否需要跳转页面
    if st.session_state.page_switch != st.session_state.current_page:
        st.switch_page(st.session_state.page_switch)

    # TTS 初始化
    init_tts()

    # 数字人 初始化
    init_digital_human()

    # ASR 初始化
    init_asr()

    if "enable_agent_checkbox" not in st.session_state:
        st.session_state.enable_agent_checkbox = WEB_CONFIGS.ENABLE_AGENT

        if WEB_CONFIGS.AGENT_DELIVERY_TIME_API_KEY is None or WEB_CONFIGS.AGENT_WEATHER_API_KEY is None:
            WEB_CONFIGS.ENABLE_AGENT = False
            st.session_state.enable_agent_checkbox = False

    # 获取销售信息
    if "sales_info" not in st.session_state:
        get_sales_info()

    # 添加页面导航页
    # st.sidebar.page_link("app.py", label="街道页", disabled=True)
    # st.sidebar.page_link("./pages/selling_page.py", label="主播卖货")

    # 主页标题
    st.title("大咖伴游-您的智能旅游搭子")
    st.header("**")

    # 说明
    st.info(
        "这是主播后台，这里需要主播讲解的地点，选择一个地点名称，点击【开始讲解】即可跳转到主播讲解页面。",
        icon="ℹ️",
    )

    # 初始化街道列表
    street_num = init_street_info()

    # 侧边栏显示街道数量，入驻品牌方
    with st.sidebar:
        # 标题
        st.header("大咖伴游", divider="grey")
        st.markdown("[大咖伴游 Github repo](https://github.com/dashan336/TripBuddyAI/)")
        st.subheader("功能点：", divider="grey")
        st.markdown(
            "1. 📜 **主播文案一键生成**\n2. 🚀 KV cache + Turbomind **推理加速**\n3. 📚 RAG **检索增强生成**\n4. 🔊 TTS **文字转语音**\n5. 🦸 **数字人生成**\n6. 🌐 **Agent 网络查询**\n7. 🎙️ **ASR 语音转文字**"
        )

        st.subheader(f"主播后台信息", divider="grey")
        st.markdown(f"共有街道：{street_num} 件")
        st.markdown(f"共有街道介绍：{street_num} 个")

        # TODO 单品成交量
        # st.markdown(f"共有品牌方：{len(street_name_list)} 个")

        if WEB_CONFIGS.ENABLE_TTS:
            # 是否生成 TTS
            st.subheader(f"TTS 配置", divider="grey")
            st.session_state.gen_tts_checkbox = st.toggle("生成语音", value=st.session_state.gen_tts_checkbox)

        if WEB_CONFIGS.ENABLE_DIGITAL_HUMAN:
            # 是否生成 数字人
            st.subheader(f"数字人 配置", divider="grey")
            st.session_state.gen_digital_human_checkbox = st.toggle(
                "生成数字人视频", value=st.session_state.gen_digital_human_checkbox
            )

        if WEB_CONFIGS.ENABLE_AGENT:
            # 是否使用 agent
            st.subheader(f"Agent 配置", divider="grey")
            with st.container(border=True):
                st.markdown("**插件列表**")
                st.button("结合天气查询到货时间", type="primary")
            st.session_state.enable_agent_checkbox = st.toggle("使用 Agent 能力", value=st.session_state.enable_agent_checkbox)

    # 添加新街道上传表单
    with st.form(key="add_street_form"):
        street_name_input = st.text_input(label="添加街道名称")
        heightlight_input = st.text_input(label="添加街道特性，以'、'隔开")
        departure_place_input = st.text_input(label="具体位置")
        delivery_company_input = st.text_input(label="附近景点")
        street_image = st.file_uploader(label="上传街道图片", type=["png", "jpg", "jpeg", "bmp"])
        street_instruction = st.file_uploader(label="上传街道详细介绍", type=["md"])
        submit_button = st.form_submit_button(label="提交", disabled=WEB_CONFIGS.DISABLE_UPLOAD)

        if WEB_CONFIGS.DISABLE_UPLOAD:
            st.info(
                "Github 上面的代码已支持上传新街道逻辑。\n但因开放性的 Web APP 没有新增街道审核机制，暂不在此开放上传街道。\n您可以 clone 本项目到您的机器启动即可使能上传按钮",
                icon="ℹ️",
            )

        if submit_button:
            update_street_info(
                street_name_input,
                heightlight_input,
                street_image,
                street_instruction,
                departure_place_input,
                delivery_company_input,
            )


def update_street_info(
    street_name_input, heightlight_input, street_image, street_instruction, departure_place, delivery_company
):
    """
    更新街道信息的函数。

    参数:
    - street_name_input: 地点名称输入，字符串类型。
    - heightlight_input: 街道主要特点，字符串类型。
    - street_image: 地点图片，图像类型。
    - street_instruction: 地点介绍，文本类型。
    - departure_place: 发货地。
    - delivery_company: 快递公司。

    返回值:
    无。该函数直接操作UI状态，不返回任何值。
    """

    # TODO 可以不输入图片和特性，大模型自动生成一版让用户自行选择

    # 检查入参#################################################################################
    if street_name_input == "" or heightlight_input == "":
        st.error("街道名称和介绍不能为空")
        return

    if street_image is None or street_instruction is None:
        st.error("图片和说明书不能为空")
        return

    if departure_place == "" or delivery_company == "":
        st.error("附近景点介绍和附近景点名称不能为空")
        return

    # 显示上传状态，并执行上传操作
    with st.status("正在上传街道...", expanded=True) as status:

        save_tag = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        image_save_path = Path(WEB_CONFIGS.street_IMAGES_DIR).joinpath(f"{save_tag}{Path(street_image.name).suffix}")
        instruct_save_path = Path(WEB_CONFIGS.street_INSTRUCTION_DIR).joinpath(
            f"{save_tag}{Path(street_instruction.name).suffix}"
        )

        st.write("图片保存中...")
        with open(image_save_path, "wb") as file:
            file.write(street_image.getvalue())

        st.write("说明书保存中...")
        with open(instruct_save_path, "wb") as file:
            file.write(street_instruction.getvalue())

        st.write("更新街道信息表...")
        with open(WEB_CONFIGS.street_info_YAML_PATH, "r", encoding="utf-8") as f:
            street_info_dict = yaml.safe_load(f)

        # 排序防止乱序
        street_info_dict = dict(sorted(street_info_dict.items(), key=lambda item: item[1]["id"]))
        max_id_key = max(street_info_dict, key=lambda x: street_info_dict[x]["id"])

        street_info_dict.update(
            {
                street_name_input: {
                    "heighlights": heightlight_input.split("、"),
                    "images": str(image_save_path),
                    "instruction": str(instruct_save_path),
                    "id": street_info_dict[max_id_key]["id"] + 1,
                    "departure_place": departure_place,
                    "delivery_company_name": delivery_company,
                }
            }
        )

        # 备份
        if Path(WEB_CONFIGS.street_info_YAML_BACKUP_PATH).exists():
            Path(WEB_CONFIGS.street_info_YAML_BACKUP_PATH).unlink()
        shutil.copy(WEB_CONFIGS.street_info_YAML_PATH, WEB_CONFIGS.street_info_YAML_BACKUP_PATH)

        # 覆盖保存
        with open(WEB_CONFIGS.street_info_YAML_PATH, "w", encoding="utf-8") as f:
            yaml.dump(street_info_dict, f, allow_unicode=True)

        st.write("生成数据库...")
        if WEB_CONFIGS.ENABLE_RAG:
            # 重新生成 RAG 向量数据库
            gen_rag_db(force_gen=True)

            # 重新加载 retriever
            RAG_RETRIEVER.pop("default")
            RAG_RETRIEVER.get(fs_id="default", config_path=WEB_CONFIGS.RAG_CONFIG_PATH, work_dir=WEB_CONFIGS.RAG_VECTOR_DB_DIR)

        # 更新状态
        status.update(label="添加街道成功!", state="complete", expanded=False)

        st.toast("添加街道成功!", icon="🎉")

        with st.spinner("准备刷新页面..."):
            time.sleep(3)

        # 刷新页面
        st.rerun()


if __name__ == "__main__":
    # streamlit run app.py --server.address=0.0.0.0 --server.port 7860

    # print("Starting...")
    main()
