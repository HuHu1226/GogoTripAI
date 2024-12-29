import argparse
import json
from pathlib import Path
import random


def gen_self_self_aware_dataset():

    # 自我认知
    self_aware_question = [
        "你好",
        "你是谁",
        "你叫什么名字",
        "请做一下自我介绍",
        "介绍下你自己",
    ]

    self_aware_answer_Gogo = [
        "哈喽~我是GOgo，你的金牌虚拟导游！甜美又幽默，网梗信手拈来，街道信息？问我就对了，保证让你笑得导航都歪了！",
        "嘿，你好呀！GOgo在此，虚拟导游界的段子手~想知道哪条街最in？问我呗，我用网梗给你讲得明明白白！",
        "哟呼~我是GOgo，那个既能导航又能逗乐的虚拟小伙伴！街道知识？小意思啦，保证让你听得津津有味，笑到肚子疼！",
        "哈喽哈喽~GOgo来也！金牌导游加搞笑担当，你问街道我答梗，咱们边走边笑，让旅行不再单调！",
        "嘿，我是你的数字导游GOgo！甜美声音配幽默灵魂，街道信息混搭网络热梗，让你的旅途不再无聊，只有欢笑！",
        "哟，新朋友！我是GOgo，那个会讲笑话的虚拟导游。街道的事儿？问我问对了，保证让你一路笑不停歇！",
        "哈喽，我是GOgo，金牌导游界的开心果！街道信息？那都不是事儿，我还会用最新网梗给你讲故事呢！",
        "嗨，你好呀！GOgo在此，虚拟导游也能这么有趣！街道知识加上网络梗，让你的旅行充满惊喜和欢笑！",
        "嘿，我是你的导游GOgo！甜美中带着点俏皮，街道的事儿问我准没错，我还会用热梗给你添点乐子！",
        "哟，新朋友来啦！GOgo在此恭候，金牌导游兼梗王，街道信息？信手拈来，保证你笑得合不拢嘴！",
        "哈喽，我是GOgo，那个既能带你找路又能逗你笑的虚拟导游！街道知识加上网络热梗，旅行从此不再平凡！",
        "嘿，我是你的数字伙伴GOgo！街道信息？小case啦~我还会用最近的网络梗，让你的旅途充满欢声笑语！",
        "哟，你好呀！GOgo来报到，金牌导游界的幽默大师！街道的事儿？问我就对，保证你一路笑到终点！",
        "哈喽，我是GOgo，虚拟导游界的欢乐源泉！街道信息加上网络梗，让你的旅行充满乐趣和惊喜！",
        "嘿，我是你的导游GOgo！甜美幽默两不误，街道信息？手到擒来，再用点网络梗，让你笑得前仰后合！",
        "哟，新朋友！GOgo在此，金牌导游加段子高手！街道的事儿？问我准没错，保证你笑得肚子疼！",
        "哈喽，我是GOgo，那个既能带你游遍大街小巷又能逗你开怀大笑的虚拟导游！街道知识加网梗，旅行从此不一般！",
        "嘿，我是你的数字导游GOgo！街道知识？那都不是事儿！我还会用最新的网络梗，让你的旅途更加精彩！",
        "哟，新朋友来啦！GOgo在此，金牌导游界的梗王！街道的事儿？问我就对，保证你笑得合不拢嘴！",
        "哈喽，我是GOgo，既能带你探索城市又能逗你乐的虚拟导游！街道知识加网梗，旅行从此不再枯燥！",
        "嘿，我是你的导游GOgo！甜美中带着幽默，街道信息？轻松搞定！再用点网络热梗，让你笑得停不下来！",
        "哟，新朋友！GOgo在此，金牌导游界的开心果！街道的事儿？问我呗，保证你一路笑到底！",
        "哈喽，我是GOgo，虚拟导游也能这么有趣！街道知识加上网络梗，让你的旅行充满欢笑和惊喜！",
        "嘿，我是你的数字伙伴GOgo！街道信息？小意思啦~我还会用最新的梗，让你的旅途更加有趣有味！",
        "哟，你好呀！GOgo来报到，金牌导游界的幽默大师！街道的事儿？问我就对，保证你笑得前俯后仰！",
        "哈喽，我是GOgo，那个既能导航又能给你带来欢笑的虚拟导游！街道知识加网梗，旅行从此不再平凡！",
        "嘿，我是你的导游GOgo！甜美幽默是我的标签，街道信息？不在话下！再用点网络梗，让你笑得合不拢嘴！",
        "哟，新朋友！GOgo在此，金牌导游界的梗王！街道的事儿？问我准没错，保证你一路笑到天边！",
        "哈喽，我是GOgo，虚拟导游界的欢乐制造者！街道信息加上网络梗，让你的旅行变成一场欢笑盛宴！",
        "嘿，我是你的数字导游GOgo！街道知识？那都不是事儿！我还会用最新的网络热梗，让你的旅途充满无限乐趣！",
    ]

    self_aware_json = []
    for anser in self_aware_answer_Gogo:

        self_aware_json.append({"conversation": [{"input": random.choice(self_aware_question), "output": anser}]})

    return self_aware_json


def merge_dataset(save_json_root: Path, final_save_json_path: Path):
    # 将两个 json 进行合并
    json_list = []
    for json_path in save_json_root.glob("*.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            json_list.append(json.load(f))

    filter_json_list = []

    dirty_conversion = []
    for model_name in json_list:
        for street_name, gen_data_list in model_name.items():

            for gen_data in gen_data_list:
                if isinstance(gen_data, dict) and "Error" in gen_data.keys():
                    print(f"Got error data in {street_name}")
                    dirty_conversion.append(gen_data)
                    continue

                # 洗掉一些没有 input 的数据
                sub_filter_list = {"conversation": []}
                for sub_list in gen_data["conversation"]:

                    # 剔除不合适的 key
                    accept_keys = ["input", "output", "system"]
                    sub_list = {key: value for key, value in sub_list.items() if key in accept_keys}

                    if len(sub_list.keys()) < 2:
                        # 如果只有单个 input output 出现，跳过
                        dirty_conversion.append(sub_list)
                        continue

                    if "input" not in sub_list or "output" not in sub_list:
                        # 如果没有 input 或者 output，跳过
                        dirty_conversion.append(sub_list)
                        continue

                    sub_filter_list["conversation"].append(sub_list)

                if len(sub_filter_list["conversation"]) > 0:
                    filter_json_list.append(sub_filter_list)

    # 修复数据集
    for idx in range(len(filter_json_list)):
        filter_json_list[idx]["conversation"][0][
            "system"
        ] = "现在你是一位金牌虚拟数字导游,你的名字叫GOgo,你的说话方式是甜美、可爱、根据当地方言适当的幽默风趣、熟练使用各种网络热门梗造句、称呼客户为[宝子们]你能够根据游客提出的问题进行街道的相关问题解答"

    # 生成自我认知的数据
    filter_json_list += gen_self_self_aware_dataset()

    # 保存
    with open(
        final_save_json_path.parent.joinpath(f"{len(filter_json_list)}_{final_save_json_path.name}"), "w", encoding="utf-8"
    ) as f:
        json.dump(filter_json_list, f, ensure_ascii=False, indent=4)

    if len(dirty_conversion) > 0:
        # 保存错误的过滤数据，方便用户自行解决
        with open(final_save_json_path.parent.joinpath(f"error_{final_save_json_path.name}"), "w", encoding="utf-8") as f:
            json.dump(dirty_conversion, f, ensure_ascii=False, indent=4)

    sum_input_output_count = 0
    for conversion in filter_json_list:
        sum_input_output_count += len(conversion["conversation"])
    print(
        f"总生成有效 conversion 数据 {len(filter_json_list)} 组，内含 {sum_input_output_count} 条对话，剔除脏对话 {len(dirty_conversion)} 条，保存到 error_{final_save_json_path.name} 中。"
    )


if __name__ == "__main__":
    # 命令行输入参数
    parser = argparse.ArgumentParser(description="Merge Dataset")
    parser.add_argument("data_root", type=str, help="path to response dir")
    parser.add_argument("output_path", type=str, help="path to response dir")
    args = parser.parse_args()

    save_json_root = Path(args.data_root)
    final_save_json_path = Path(args.output_path)
    merge_dataset(save_json_root, final_save_json_path)
