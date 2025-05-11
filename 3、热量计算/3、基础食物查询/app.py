from flask import Flask, request, jsonify, render_template
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 连接到MySQL数据库
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # 替换为你的MySQL用户名
        password='root',  # 替换为你的MySQL密码
        database='ruangong_fooddb'  # 替换为你的数据库名
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


# 主页面路由
@app.route('/', methods=['GET', 'POST'])
def index():
    nutrition_data = None
    if request.method == 'POST':
        food_name = request.form['food_name']

        # 查询食物及其特征和营养成分
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT f.name, f.image_url, f.detail_url, f.calories, f.carbs, f.fat, f.protein, f.fiber, f.category, ff.feature 
        FROM food f
        JOIN food_feature ff ON f.id = ff.food_id
        WHERE f.name = %s
        """
        cursor.execute(query, (food_name,))
        nutrition_data = cursor.fetchall()
        if nutrition_data:
            print("Nutrition data found:", nutrition_data)
        else:
            print("No nutrition data found for the food name.")

        cursor.close()
        connection.close()

    return render_template('index.html', nutrition_data=nutrition_data)


# 计算多种食物的热量总和
@app.route('/calculate_calories', methods=['POST'])
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

    return jsonify({'totalCalories': total_calories})


if __name__ == '__main__':
    app.run(debug=True)
