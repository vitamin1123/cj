import random
import string
import csv
from datetime import datetime, timedelta

def generate_openid():
    """生成与示例相同格式和长度的openid"""
    return ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=28))

def generate_gender():
    """随机生成性别"""
    return random.choice(['male', 'female'])

def generate_birth_date():
    """生成1980-2025年6月1日的日期"""
    year = random.randint(1980, 2025)
    return f"{year}-06-01 00:00:00"

def generate_height(gender):
    """根据性别生成合理身高"""
    if gender == 'male':
        return str(random.randint(165, 190))
    else:
        return str(random.randint(150, 175))

def generate_weight(gender, height):
    """根据性别和身高生成合理体重"""
    height = int(height)
    if gender == 'male':
        base_weight = (height - 100) * 0.9
        return f"{round(random.uniform(base_weight - 10, base_weight + 10), 1)}"
    else:
        base_weight = (height - 105) * 0.9
        return f"{round(random.uniform(base_weight - 8, base_weight + 8), 1)}"

def generate_region_code():
    """随机生成地区编码"""
    return random.choice(['321282', '310104'])

def generate_occupation():
    """生成职业（限制10个字符）"""
    occupations = [
        "计算机工程师", "建筑设计师", "医生", "教师", "会计", 
        "程序员", "销售", "人力资源", "设计师", "电工", 
        "厨师", "护士", "公务员", "银行职员", "警察",
        "机械工程师", "电子工程师", "软件工程师", "网络工程师", "翻译"
    ]
    # 确保不超过10个字符
    return random.choice([occ[:10] for occ in occupations])

def generate_income_level():
    """生成收入水平，符合ENUM类型"""
    return random.choice(['below_3k', '3k_5k', '5k_8k', '8k_12k', '12k_20k', 'above_20k'])

def generate_education():
    """生成教育程度，符合ENUM类型"""
    return random.choice(['high_school', 'college', 'bachelor', 'master', 'phd'])

def generate_religion():
    """生成宗教，符合ENUM类型"""
    return random.choice(['buddhism', 'christianity', 'islam', 'taoism', 'none', 'other'])

def generate_mbti():
    """生成MBTI类型"""
    types = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 
             'ISTP', 'ISFP', 'INFP', 'INTP', 
             'ESTP', 'ESFP', 'ENFP', 'ENTP', 
             'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']
    return random.choice(types)

def generate_phone():
    """生成11位手机号"""
    return '1' + ''.join(random.choices(string.digits, k=10))

def generate_mem(gender):
    """生成个人介绍"""
    if gender == 'male':
        family_backgrounds = [
            "父母均有稳定工作和退休保障，家庭和睦。",
            "父亲经营企业，母亲是教师，经济条件优越。",
            "父母都是普通工人，已退休，有一定积蓄。",
            "单亲家庭，由母亲抚养长大，母亲已退休。",
            "来自农村，通过自己努力在城市立足。",
            "家庭条件一般，但父母健康，支持我的事业。"
        ]
        
        self_descriptions = [
            "性格开朗，喜欢运动和旅行，希望找到志同道合的伴侣。",
            "工作稳定，有责任心，爱好摄影和阅读，期待稳定的感情。",
            "幽默风趣，热爱生活，喜欢尝试新鲜事物，寻找乐观向上的你。",
            "成熟稳重，有自己的事业规划，希望找到能一起奋斗的另一半。",
            "温和善良，注重家庭，希望未来能组建一个温馨的家庭。",
            "独立自主，有自己的兴趣爱好，期待与你分享生活的点滴。"
        ]
        
        partner_expectations = [
            "希望对方性格温柔，善解人意，有稳定工作。",
            "寻找三观一致，有共同兴趣爱好的女生。",
            "期待对方乐观开朗，热爱生活，能一起面对未来。",
            "希望找到一个孝顺父母，懂得包容的伴侣。",
            "要求不高，只要真诚相待，互相理解支持。",
            "希望对方有自己的追求，同时也重视家庭。"
        ]
    else:
        family_backgrounds = [
            "父母身体健康，有稳定收入和退休保障。",
            "家庭和睦，父母都是知识分子，注重教育。",
            "单亲家庭，与父亲生活，父亲有自己的事业。",
            "来自城市普通家庭，父母已退休。",
            "家庭条件优越，父母经营企业。",
            "父母是工人，勤劳朴实，家庭氛围温馨。"
        ]
        
        self_descriptions = [
            "性格温柔，善解人意，喜欢烹饪和阅读，期待稳定的感情。",
            "开朗活泼，热爱生活，喜欢旅行和拍照，寻找有趣的灵魂。",
            "独立自主，有自己的事业，闲暇时喜欢瑜伽和看电影。",
            "温柔贤惠，注重家庭，希望未来能相夫教子。",
            "乐观向上，爱好广泛，期待与你一起探索生活的美好。",
            "知性优雅，有自己的思想，寻找能与我心灵共鸣的伴侣。"
        ]
        
        partner_expectations = [
            "希望对方有责任心，成熟稳重，能给我安全感。",
            "寻找有上进心，有自己的目标和追求的男生。",
            "期待对方真诚善良，有良好的家庭观念。",
            "希望找到一个懂得尊重和包容的伴侣。",
            "要求对方有稳定工作，性格开朗，乐观积极。",
            "希望对方有一定的经济基础，同时也重视感情。"
        ]
    
    return f"{random.choice(family_backgrounds)}{random.choice(self_descriptions)}{random.choice(partner_expectations)}"

def generate_nickname(gender, existing_nicknames=None):
    """生成不重复的昵称，使用形容词+名词+随机后缀的组合"""
    if existing_nicknames is None:
        existing_nicknames = set()
    
    # 大量的形容词和名词选项，增加组合可能性
    adjectives = [
        "快乐", "悲伤", "勇敢", "聪明", "善良", "美丽", "可爱", "高大", "矮小", "肥胖", "瘦弱",
        "开朗", "内向", "活泼", "文静", "热情", "冷漠", "温柔", "暴躁", "坚强", "脆弱", "乐观",
        "悲观", "勤奋", "懒惰", "诚实", "虚伪", "谦虚", "骄傲", "自信", "自卑", "稳重", "轻浮",
        "成熟", "幼稚", "稳重", "幽默", "严肃", "风趣", "优雅", "粗俗", "大方", "小气", "慷慨",
        "吝啬", "正直", "邪恶", "忠诚", "背叛", "守信", "失信", "细心", "粗心", "耐心", "急躁",
        "温和", "严厉", "果断", "犹豫", "勇敢", "怯懦", "聪明", "愚蠢", "机智", "迟钝", "灵活",
        "呆板", "敏捷", "迟缓", "健康", "虚弱", "强壮", "弱小", "高大", "矮小", "美丽", "丑陋",
        "整洁", "邋遢", "干净", "肮脏", "朴素", "华丽", "时尚", "过时", "新潮", "守旧", "现代",
        "传统", "先进", "落后", "文明", "野蛮", "礼貌", "粗鲁", "热情", "冷淡", "和蔼", "严厉",
        "善良", "凶恶", "正直", "奸诈", "诚实", "虚伪", "谦虚", "骄傲", "自信", "自卑", "坚强",
        "软弱", "乐观", "悲观", "勤奋", "懒惰", "认真", "马虎", "细心", "粗心", "耐心", "急躁",
        "温和", "暴躁", "果断", "犹豫", "勇敢", "怯懦", "聪明", "愚蠢", "机智", "迟钝", "灵活",
        "呆板", "敏捷", "迟缓", "健康", "虚弱", "强壮", "弱小", "高大", "矮小", "美丽", "丑陋",
        "整洁", "邋遢", "干净", "肮脏", "朴素", "华丽", "时尚", "过时", "新潮", "守旧", "现代",
        "传统", "先进", "落后", "文明", "野蛮", "礼貌", "粗鲁"
    ]
    
    nouns = [
        "小猫", "小狗", "小鸟", "小鱼", "小马", "小牛", "小羊", "小猴", "小鸡", "小鸭", "小猪",
        "老虎", "狮子", "大象", "猴子", "兔子", "老鼠", "狐狸", "狼", "熊", "长颈鹿", "熊猫",
        "企鹅", "袋鼠", "考拉", "树懒", "刺猬", "松鼠", "蝙蝠", "蛇", "鳄鱼", "乌龟", "青蛙",
        "蝴蝶", "蜜蜂", "蚂蚁", "蜻蜓", "蚊子", "苍蝇", "蟑螂", "蜘蛛", "蜈蚣", "蜗牛", "蚯蚓",
        "苹果", "香蕉", "橘子", "梨", "葡萄", "西瓜", "草莓", "蓝莓", "樱桃", "芒果", "菠萝",
        "柠檬", "橙子", "柚子", "猕猴桃", "火龙果", "柿子", "石榴", "山楂", "红枣", "栗子",
        "核桃", "花生", "瓜子", "杏仁", "开心果", "腰果", "榛子", "巴旦木", "椰子", "橄榄", "榴莲",
        "白菜", "萝卜", "土豆", "西红柿", "黄瓜", "茄子", "辣椒", "豆角", "南瓜", "冬瓜", "丝瓜",
        "苦瓜", "洋葱", "大蒜", "生姜", "韭菜", "香菜", "芹菜", "菠菜", "生菜", "油麦菜", "西兰花",
        "胡萝卜", "莲藕", "山药", "红薯", "紫薯", "芋头", "玉米", "小麦", "水稻", "大豆", "绿豆",
        "红豆", "黑豆", "芝麻", "油菜", "花生", "向日葵", "棉花", "烟草", "茶叶", "咖啡", "可可",
        "玫瑰", "牡丹", "菊花", "兰花", "荷花", "梅花", "桃花", "杏花", "梨花", "桂花", "茉莉花",
        "百合花", "郁金香", "康乃馨", "满天星", "薰衣草", "向日葵", "蒲公英", "仙人掌", "多肉",
        "松树", "柏树", "杨树", "柳树", "槐树", "榆树", "枫树", "银杏树", "梧桐树", "樟树", "榕树",
        "苹果树", "梨树", "桃树", "杏树", "枣树", "柿子树", "石榴树", "山楂树", "葡萄树", "猕猴桃树"
    ]
    
    # 增加一些特殊的地点和动作组合，如"飞越鄱阳湖的小辣椒"
    special_locations = [
        "的", "在", "飞越", "潜入", "攀登", "路过", "守护", "仰望", "拥抱", "追逐", "梦见", "思念",
        "等待", "寻找", "遇见", "爱上", "忘记", "记得", "想念", "渴望", "期待", "憧憬", "回忆", "怀念"
    ]
    
    special_objects = [
        "鄱阳湖", "长江", "黄河", "泰山", "黄山", "长城", "故宫", "西湖", "洱海", "草原", "沙漠",
        "森林", "海洋", "天空", "月亮", "星星", "太阳", "云朵", "彩虹", "闪电", "雷鸣", "风雨",
        "雪花", "迷雾", "清晨", "黄昏", "夜晚", "黎明", "春天", "夏天", "秋天", "冬天", "时间",
        "空间", "梦想", "希望", "未来", "过去", "现在", "回忆", "思念", "爱情", "友情", "亲情",
        "自由", "快乐", "幸福", "悲伤", "痛苦", "孤独", "寂寞", "勇气", "力量", "智慧", "真理",
        "生命", "死亡", "成长", "奋斗", "成功", "失败", "挑战", "机遇", "命运", "缘分", "奇迹"
    ]
    
    max_attempts = 1000  # 最大尝试次数，防止无限循环
    for _ in range(max_attempts):
        # 70%概率生成普通组合昵称，30%概率生成特殊组合昵称
        if random.random() < 0.7:
            nickname = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(1, 100)}"
        else:
            # 特殊组合：特殊动作/地点 + 特殊物体 + 的 + 形容词 + 名词
            nickname = f"{random.choice(special_locations)}{random.choice(special_objects)}的{random.choice(adjectives)}{random.choice(nouns)}"
        
        if nickname not in existing_nicknames:
            existing_nicknames.add(nickname)
            return nickname[:10]
    
    # 如果尝试多次仍无法生成唯一昵称，返回默认带编号的昵称
    default_nick = f"用户{len(existing_nicknames) + 1}"
    existing_nicknames.add(default_nick)
    return default_nick

def generate_avatar():
    """生成头像文件名"""
    if random.random() < 0.7:  # 70%概率有头像
        return f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=32))}.jpeg"
    return None

def generate_photo():
    """生成照片字段"""
    if random.random() < 0.3:  # 30%概率有照片
        return f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=32))}.jpeg"
    return None

def generate_created_updated_at():
    """生成创建和更新时间"""
    now = datetime.now()
    created_at = now - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    updated_at = created_at + timedelta(days=random.randint(0, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    if updated_at > now:
        updated_at = now
    return created_at.strftime('%Y-%m-%d %H:%M:%S'), updated_at.strftime('%Y-%m-%d %H:%M:%S')

def generate_user_data(start_id, count):
    """生成指定数量的用户数据"""
    users = []
    existing_nicknames = set()
    
    for i in range(count):
        user_id = start_id + i
        openid = generate_openid()
        gender = generate_gender()
        birth_date = generate_birth_date()
        height = generate_height(gender)
        weight = generate_weight(gender, height)
        region_code = generate_region_code()
        occupation = generate_occupation()
        income_level = generate_income_level()
        education = generate_education()
        religion = generate_religion()
        mbti = generate_mbti()
        phone = generate_phone()
        mem = generate_mem(gender)
        mem_pri = None
        avatar = generate_avatar()
        photo = generate_photo()
        created_at, updated_at = generate_created_updated_at()
        nickname = generate_nickname(gender, existing_nicknames)
        
        users.append([
            openid, user_id, gender, birth_date, height, weight, region_code, 
            occupation, income_level, education, religion, mbti, phone, mem, 
            mem_pri, avatar, photo, created_at, updated_at, nickname
        ])
    return users

def write_to_sql_file(users, filename):
    """将用户数据写入SQL文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("INSERT INTO user (openid, id, gender, birth_date, height, weight, region_code, occupation, income_level, education, religion, mbti, phone, mem, mem_pri, avatar, photo, created_at, updated_at, nickname) VALUES\n")
        
        for i, user in enumerate(users):
            # 处理NULL值
            values = []
            for value in user:
                if value is None:
                    values.append('NULL')
                else:
                    # 转义单引号
                    if isinstance(value, str):
                        value = value.replace("'", "''")
                    values.append(f"'{value}'")
            
            # 生成SQL行
            sql_line = f"({', '.join(values)})"
            
            # 最后一行以分号结束，其他行以逗号结束
            if i == len(users) - 1:
                sql_line += ";\n"
            else:
                sql_line += ",\n"
            
            f.write(sql_line)

if __name__ == "__main__":
    start_id = 5555
    count = 5000
    output_file = "user_data.sql"
    
    print(f"开始生成{count}条用户数据...")
    users = generate_user_data(start_id, count)
    print(f"数据生成完成，正在写入{output_file}...")
    write_to_sql_file(users, output_file)
    print(f"数据已成功写入{output_file}")    