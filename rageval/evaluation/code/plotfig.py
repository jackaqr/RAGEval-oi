import matplotlib.pyplot as plt

# 示例数据
x = [1, 2, 3, 4, 5]
y = [0.33, 0.327, 0.44, 0.39, 0.404, 0.405, 0.45, 0.359, 0.395, 0.31, 0.338, 0.388, 0.3, 0.29, 0.33]

labels = ['FlashRAG', 'OI', 'Dify混合召回', 'Dify向量', 'E']

# 绘制散点图
plt.scatter(x, y)

# 为每个点添加标签
for i in range(len(x)):
    plt.text(x[i] + 0.1, y[i] + 0.1, labels[i], fontsize=12)  # 调整标签位置，避免遮挡点

# 添加标题和坐标轴标签
plt.title("带标签的散点图")
plt.xlabel("X 值")
plt.ylabel("Y 值")

# 显示图形
plt.show()