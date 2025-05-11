// 检测页面加载完成后执行的函数
document.addEventListener("DOMContentLoaded", function() {
    console.log("页面已加载");

    // 餐盘热量计算页面：用户选择食物后更新可视化展示
    const foodCheckboxes = document.querySelectorAll('input[name="food"]');
    const selectedFoodsList = document.createElement('ul');
    document.body.appendChild(selectedFoodsList);

    foodCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener("change", function() {
            updateSelectedFoods();
        });
    });

    function updateSelectedFoods() {
        selectedFoodsList.innerHTML = ""; // 清空已选择的列表
        foodCheckboxes.forEach(function(checkbox) {
            if (checkbox.checked) {
                const listItem = document.createElement('li');
                listItem.textContent = checkbox.value;
                selectedFoodsList.appendChild(listItem);
            }
        });
    }
});

// 餐盘页面提交按钮的动画效果
const submitButton = document.querySelector("button[type='submit']");
submitButton.addEventListener("click", function() {
    submitButton.style.transform = "scale(1.1)";
    setTimeout(function() {
        submitButton.style.transform = "scale(1)";
    }, 100);
});
