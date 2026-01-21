# 🚀 快速开始 - Mac用户

## 方式1: 一键安装 (推荐)

在终端运行:

```bash
cd /Users/user/Desktop/量化ai
./setup.sh
```

安装完成后运行:

```bash
source venv/bin/activate
python test_system.py
```

## 方式2: 手动安装

### 步骤1: 创建虚拟环境

```bash
cd /Users/user/Desktop/量化ai
python3 -m venv venv
```

### 步骤2: 激活虚拟环境

```bash
source venv/bin/activate
```

### 步骤3: 安装依赖

```bash
pip install --upgrade pip
pip install pandas numpy yfinance matplotlib seaborn scipy scikit-learn plotly
```

### 步骤4: 测试系统

```bash
python test_system.py
```

## 常用命令

### 每次使用前,先激活虚拟环境:

```bash
cd /Users/user/Desktop/量化ai
source venv/bin/activate
```

### 运行示例:

```bash
# 快速示例
python example.py

# 测试AAPL股票
python main.py --symbol AAPL

# 对比多个策略
python main.py --compare --symbol AAPL

# 回测多只股票
python main.py --symbols AAPL MSFT GOOGL
```

### 退出虚拟环境:

```bash
deactivate
```

## 如果遇到问题

### 问题1: "command not found: python3"

**解决方案**: 安装Homebrew和Python

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.13
```

### 问题2: 网络连接问题

**解决方案**: 使用国内镜像源

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas numpy yfinance matplotlib seaborn
```

### 问题3: 权限错误

**解决方案**: 确保在虚拟环境中安装,不要使用 --break-system-packages

## 完整示例流程

```bash
# 1. 进入项目目录
cd /Users/user/Desktop/量化ai

# 2. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install pandas numpy yfinance matplotlib seaborn scipy scikit-learn

# 4. 运行测试
python test_system.py

# 5. 运行第一个回测
python main.py --symbol AAPL

# 6. 查看结果
open results/AAPL_report_*.html
```

## 下一步

运行成功后,您可以:

1. 📖 阅读 [README.md](README.md) 了解更多功能
2. 📝 修改 [config.yaml](config.yaml) 配置您的策略
3. 💻 参考 [example.py](example.py) 学习编程用法
4. 🎯 创建自己的交易策略!

## 需要帮助?

- 查看 [QUICKSTART.md](QUICKSTART.md) 详细指南
- 运行 `python test_system.py` 诊断问题
- 检查日志文件 `logs/*.log`

---

**祝您交易愉快! 📈💰**
