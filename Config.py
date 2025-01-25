import json
def create_config():
    config = {
        "tick响应所需时间": 1,
        "主环入场时间": 0.5,
        "点动画入场时间": 0.5,
        "点动画出场时间": 0.5,
        "等级消失时间": 2,
        "等级进入时间": 1,
        "设定时间":0,
        "每一业力等级所需的时间":60,
        "单个点所代表的时间": 5,
        "缩放大小":2
    }
    with open("./Settings.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def getValue(key):
    with open("./Settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        return config[key]

def changeValue(value,key):
    with open("./Settings.json", "r+", encoding="utf-8") as f:
        config = json.load(f)
        try:
            config[key] = int(value)
        except:
            pass
        f.seek(0)
        json.dump(config, f, ensure_ascii=False, indent=4)
        f.truncate()