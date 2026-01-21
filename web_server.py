#!/usr/bin/env python3
"""
Flask Web服务器
为市场情绪分析面板提供数据API
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

from flask import Flask, jsonify, render_template, send_from_directory
from datetime import datetime
import json
import os

from market_sentiment_enhanced import AStockMarketSentimentEnhanced

app = Flask(__name__, template_folder='templates')

# 全局变量存储最新的分析数据
latest_sentiment_data = None
last_update_time = None


def update_sentiment_data():
    """更新情绪数据"""
    global latest_sentiment_data, last_update_time

    try:
        analyzer = AStockMarketSentimentEnhanced(use_mock_data=True)
        report = analyzer.generate_sentiment_report()

        if report:
            # 提取需要的数据
            indices_data = []
            for name, df in report['indices'].items():
                if not df.empty:
                    indices_data.append({
                        'name': name,
                        'price': float(df['close'].iloc[0]),
                        'change': float(df['change_pct'].iloc[0])
                    })

            latest_sentiment_data = {
                'score': report['score'],
                'sentiment': report['sentiment'],
                'indices': indices_data,
                'breadth': report['breadth'],
                'timestamp': report['timestamp'].isoformat()
            }
            last_update_time = datetime.now()
            return True
    except Exception as e:
        print(f"更新数据出错: {str(e)}")

    return False


@app.route('/')
def index():
    """主页"""
    return send_from_directory('templates', 'sentiment_dashboard.html')


@app.route('/api/sentiment')
def get_sentiment():
    """获取情绪数据API"""
    global latest_sentiment_data, last_update_time

    # 如果没有数据或超过60秒，更新数据
    if latest_sentiment_data is None or last_update_time is None:
        update_sentiment_data()
    elif (datetime.now() - last_update_time).seconds > 60:
        update_sentiment_data()

    if latest_sentiment_data:
        return jsonify({
            'success': True,
            'data': latest_sentiment_data,
            'update_time': last_update_time.isoformat() if last_update_time else None
        })
    else:
        return jsonify({
            'success': False,
            'message': '无法获取数据'
        }), 500


@app.route('/api/refresh')
def refresh_sentiment():
    """强制刷新数据"""
    if update_sentiment_data():
        return jsonify({
            'success': True,
            'message': '数据刷新成功',
            'data': latest_sentiment_data
        })
    else:
        return jsonify({
            'success': False,
            'message': '数据刷新失败'
        }), 500


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'has_data': latest_sentiment_data is not None
    })


if __name__ == '__main__':
    # 尝试多个端口
    PORT = 5000

    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    # 如果5000端口被占用，尝试其他端口
    if is_port_in_use(PORT):
        print("⚠️  端口5000被占用，尝试使用端口8080...")
        PORT = 8080
        if is_port_in_use(PORT):
            print("⚠️  端口8080也被占用，尝试使用端口3000...")
            PORT = 3000

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🌐 A股市场情绪分析Web服务器                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # 初始化数据
    print("📡 正在初始化市场数据...")
    update_sentiment_data()

    if latest_sentiment_data:
        print("✅ 数据初始化成功")
        print(f"   当前情绪: {latest_sentiment_data['sentiment']}")
        print(f"   情绪得分: {latest_sentiment_data['score']:.3f}")
    else:
        print("⚠️  数据初始化失败，将在首次请求时重试")

    print("\n🚀 启动Web服务器...")
    print(f"📊 访问地址: http://localhost:{PORT}")
    print("📡 API接口:")
    print("   - GET  /                 主页")
    print("   - GET  /api/sentiment    获取情绪数据")
    print("   - GET  /api/refresh      强制刷新数据")
    print("   - GET  /api/health       健康检查")
    print("\n按 Ctrl+C 停止服务器\n")

    # 启动服务器
    app.run(host='0.0.0.0', port=PORT, debug=True)
