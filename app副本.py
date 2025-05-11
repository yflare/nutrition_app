from flask import Flask, render_template, request, jsonify
import openai
import mysql.connector
import logging
import pandas as pd
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage
from dotenv import load_dotenv
import re

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# 使用 OpenAI API 的地方，请将 {API_KEY} 替换为你的 API Key
openai.api_key = "{API_KEY}"

# 连接到MySQL数据库
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # 替换为你的MySQL用户名
        password='root',  # 替换为你的MySQL密码
        database='ruangong_fooddb',  # 替换为你的数据库名
        charset='utf8mb4'  # 确保使用UTF-8字符集处理中文
    )
    return connection

# 获取所有食物名称
@app.route('/get_food_items', methods=['GET'])
def get_food_items():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT name FROM food")
    food_items = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify([item['name'] for item in food_items])

# 主页面
@app.route('/')
def home():
    return render_template('0index.html')

# 查询食物营养成分页面
@app.route('/search')
def search():
    return render_template('1search.html')

@app.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    nutrition_data = None
    if request.method == 'POST':
        # 获取用户输入，并将其转换为小写
        food_name = request.form['food_name'].strip().lower()

        print(f"User input (after stripping and lowering): {food_name}")  # 打印用户输入


        # 查询食物及其特征和营养成分
        connection = get_db_connection()
        cursor = None  # 初始化cursor为None
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT f.name, f.image_url, f.detail_url, f.calories, f.carbs, f.fat, f.protein, f.fiber, f.category, ff.feature 
            FROM food f
            LEFT JOIN food_feature ff ON f.id = ff.food_id
            WHERE LOWER(f.name) = LOWER(%s)
            """
            cursor.execute(query, (food_name,))

            print("Food Name:", food_name)  # 打印用户输入的食物名

            nutrition_data = cursor.fetchall()  # 确保读取所有数据
            print(f"Nutrition data found: {nutrition_data}")

            if not nutrition_data:
                print("No nutrition data found for the food name.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if cursor:  # 确保cursor不为None再关闭
                cursor.close()  # 在所有结果读取后关闭游标
            connection.close()


    return render_template('1diabetes.html', nutrition_data=nutrition_data)

#糖尿病查询

# 加载环境变量
load_dotenv()

# 初始化Spark AI接口
appid = "7633a97b"  # 填写控制台中获取的 APPID 信息
api_secret = "MTJiYjg1ZDU4OGZkNTczZWQyMTMxY2Fm"  # 填写控制台中获取的 APISecret 信息
api_key = "f38846db3bcd7d49d96b9c7fb3db7843"  # 填写控制台中获取的 APIKey 信息
spark = ChatSparkLLM(
    spark_api_url="wss://spark-api.xf-yun.com/v4.0/chat",
    spark_app_id=appid,
    spark_api_key=api_key,
    spark_api_secret=api_secret,
    spark_llm_domain="4.0Ultra",
    streaming=False,
    )

# 调用API接口查询信息
def query_api(food_name, disease):
    messages = [ChatMessage(
        role="user",
        content=f"{food_name}对{disease}患者的作用是什么？"
    )]
    a = spark.generate([messages])
    for response in a.generations:
        return response[0].text


# 加载Excel文件
file_path = r"2、糖尿病\2、食物营养成分查询系统\详细版本糖尿病有益食物.xls"
df = pd.read_excel(file_path)

# 查询特定类型的食物
def query_specific_type_food(food_type, disease):
    matched_foods = df[(df['类别'].str.contains(food_type)) & (df['治疗疾病'].str.contains(disease))]
    if matched_foods.empty:
        # 如果在DataFrame中未找到信息，调用API接口
        return query_api(food_type, disease)
    else:
        return matched_foods

# 查询食物的具体作用
def query_food_effect(food_name, disease):
    food_info = df[(df['食品名称'] == food_name) & (df['治疗疾病'].str.contains(disease))]
    if food_info.empty:
        # 如果在DataFrame中未找到信息，调用API接口
        return query_api(food_name, disease)
    else:
        return f"{food_name}对{disease}患者的作用：{food_info['作用'].values[0]}"

#1.	查询特定类型的食物：
	#“有哪些谷物对糖尿病患者有益？”
	#“列举一些适宜糖尿病患者食用的水果。”
#2.	查询食物的具体作用：
	#“西瓜对糖尿病患者有什么作用？”

# 解析用户问题
def parse_question(question):
    # 处理“有哪些xxx（食物类型）对xxx（疾病）患者有益？”和“列举一些适宜xxx（疾病）患者食用的xxx（食物类型）。”两种形式
    pattern1 = r"有哪些(.+?)对(.+?)患者有益"
    pattern2 = r"列举一些适宜(.+?)患者食用的(.+?)"
    
    match1 = re.search(pattern1, question)
    match2 = re.search(pattern2, question)
    
    if match1:
        food_type = match1.group(1)
        disease = match1.group(2)
        if food_type=="食物":
            result = query_specific_type_food("", disease)
        else:
            result = query_specific_type_food(food_type, disease)
        print(f"适宜{disease}患者的{food_type}有：")
        return result[['食品名称', '图片链接','作用']]
    elif match2:
        disease = match2.group(1)
        food_type = match2.group(2)
        if food_type=="食物":
            result = query_specific_type_food("", disease)
        else:
            result = query_specific_type_food(food_type, disease)
        print(f"适宜{disease}患者的{food_type}有：")
        return result[['食品名称','图片链接', '作用']]
    else:
        # 处理“xxx（食物名字）对xxx（疾病）患者有什么作用？”形式
        pattern3 = r"(.+?)对(.+?)患者有什么作用"
        match3 = re.search(pattern3, question)
        if match3:
            food_name = match3.group(1)
            disease = match3.group(2)
            result = query_food_effect(food_name, disease)
            return result
        else:
            return "无法解析问题，请尝试更明确的提问。"

#question = input("请输入您的问题：")
#result = parse_question(question)
#print(result)

def process_image_links(data):
    if isinstance(data, pd.DataFrame):
        return data.apply(lambda row: {"name": row['食品名称'], "image": "<img src='" + row['图片链接'] + "'>", "effect": row['作用']}, axis=1).tolist()
    elif isinstance(data, dict):
        return data
    else:
        return data

@app.route('/query', methods=['POST'])
def query():
    question = request.form.get('question')
    answer = parse_question(question)
    processed_answer = process_image_links(answer)
    return render_template('2query.html', result=processed_answer, query=question)

# 2的主页面
@app.route('/web', methods=['GET'])
def web():
    return render_template('2web.html')


# 用户提问：有哪些谷物对糖尿病患者有益？
#grain_beneficial = query_specific_type_food("谷物","糖尿病")
#if not grain_beneficial.empty:
    #print("适宜糖尿病患者的谷物有：")
    #print(grain_beneficial[['食品名称', '作用']])
#else:
    #print("未找到适宜糖尿病患者的谷物。")

# 用户提问：列举一些适宜糖尿病患者食用的水果。
#fruit_beneficial = query_specific_type_food("水果","糖尿病")
#if not fruit_beneficial.empty:
    #print("适宜糖尿病患者食用的水果有：")
    #print(fruit_beneficial[['食品名称', '作用']])
#else:
    #print("未找到适宜糖尿病患者的水果。")

# 用户提问：西瓜对糖尿病患者有什么作用？
#watermelon_effect = query_food_effect("西瓜","糖尿病")
#print(watermelon_effect)

# 用户提问：有哪些食物对心脏病患者有益？
#heart_disease_beneficial = query_specific_type_food("", "心脏病")
#if not heart_disease_beneficial.empty:
    #print("适宜心脏病患者的食物有：")
    #print(heart_disease_beneficial[['食品名称', '作用']])
#else:
    #print("未找到适宜心脏病患者的食物。")

# 用户提问：茶油对心脏病患者有什么作用？
#tea_oil_effect = query_food_effect("茶油", "心脏病")
#print(tea_oil_effect)


# 计算多种食物的热量总和

from flask import Flask, request, jsonify


@app.route('/search_food', methods=['GET'])
def search_food():
    query = request.args.get('query')
    print(f"Received query: {query}")  # 添加调试输出

    if not query:
        return jsonify({"error": "请输入食物名称"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 查询食物
    search_query = """
        SELECT name, image_url, calories, category
        FROM food
        WHERE name = %s
    """
    cursor.execute(search_query, (query,))  # 直接传入查询字符串
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    if results:
        return jsonify(results)  # 返回查询结果
    else:
        return jsonify({'error': '未找到该食物'}), 404

    
@app.route('/calculate', methods=['POST'])
def calculate():
    food_data = request.json
    total_calories = 0

    # 验证输入数据
    for item in food_data:
        food_name = item.get('name')
        portion = item.get('portion')

        if not food_name or not isinstance(portion, (int, float)) or portion <= 0:
            return jsonify({'error': '无效的食物数据'}), 400

    connection = get_db_connection()
    
    with connection:
        cursor = connection.cursor(dictionary=True)
        for item in food_data:
            food_name = item['name']
            portion = item['portion']

            # 查询数据库获取每100克的卡路里值
            query = "SELECT calories FROM food WHERE name = %s"
            cursor.execute(query, (food_name,))
            result = cursor.fetchone()

            if result:
                calories_per_100g = result['calories']
                total_calories += (calories_per_100g / 100) * portion
                print(f"食物: {food_name}, 每100克卡路里: {calories_per_100g}")
            else:
                print(f"未找到食物: {food_name}")

    return jsonify({'totalCalories': total_calories})


# 餐盘计算界面路由
@app.route('/calculate_calories')
def calculate_calories():
    return render_template('3calculate_calories.html')  # 渲染计算餐盘热量的页面


'''@app.route('/calculate_calories', methods=['POST'])
def calculate_calories():
    food_data = request.json  # 获取前端传递的食物数据
    total_calories = 0

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    for item in food_data:
        food_name = item['name']
        portion = item['portion']  # 用户输入的克数

        # 从数据库中查询每100克食物的卡路里
        query = "SELECT calories FROM food WHERE name = %s"
        cursor.execute(query, (food_name,))
        result = cursor.fetchone()

        if result:
            calories_per_100g = result['calories']
            # 计算每种食物的总热量
            total_calories += (calories_per_100g / 100) * portion

    cursor.close()
    connection.close()
    # 返回 JSON 响应而不是渲染模板
    return jsonify({'totalCalories': total_calories})

# 新路由：渲染 HTML 页面
@app.route('/xuanran')
def xuanran():
    return render_template('3calculate_calories')  '''

if __name__ == '__main__':
    app.run(debug=True)
