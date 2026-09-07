"""
Generate Test Data
生成测试数据脚本
用于制造大量订单数据，便于测试慢SQL
"""
import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.order import Order


def create_tables():
    """创建数据表"""
    print("正在创建数据表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据表创建完成")


def create_test_users(db: Session, count: int = 10):
    """创建测试用户"""
    print(f"正在创建 {count} 个测试用户...")

    users = []
    for i in range(1, count + 1):
        user = User(
            username=f"user{i}",
            password_hash=f"hash_password{i}",
            email=f"user{i}@example.com",
            role='user'
        )
        db.add(user)
        users.append(user)

    db.commit()
    print(f"✓ 创建 {len(users)} 个用户完成")
    return users


def create_test_orders(db: Session, user_ids: list, count: int = 10000):
    """
    创建大量测试订单
    为了制造慢SQL，需要创建大量数据
    """
    print(f"正在创建 {count} 个测试订单...")

    products = [
        "iPhone 15 Pro", "MacBook Pro", "iPad Air", "Apple Watch",
        "AirPods Pro", "Magic Mouse", "Magic Keyboard", "HomePod",
        "Mac Mini", "Studio Display", "Mac Pro", "Pro Display XDR"
    ]

    statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']

    orders = []
    for i in range(1, count + 1):
        user_id = random.choice(user_ids)
        order = Order(
            user_id=user_id,
            product_name=random.choice(products),
            amount=Decimal(str(round(random.uniform(100, 10000), 2))),
            status=random.choice(statuses),
            created_at=datetime.now() - timedelta(days=random.randint(0, 365))
        )
        orders.append(order)

        # 批量提交，每1000条提交一次
        if i % 1000 == 0:
            db.bulk_save_objects(orders)
            db.commit()
            print(f"  已创建 {i}/{count} 条订单")
            orders = []

    # 提交剩余的订单
    if orders:
        db.bulk_save_objects(orders)
        db.commit()

    print(f"✓ 创建 {count} 个订单完成")


def main():
    """主函数"""
    print("=" * 60)
    print("SmartOps 测试数据生成工具")
    print("=" * 60)

    # 创建数据表
    create_tables()

    # 获取数据库会话
    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        existing_orders = db.query(Order).count()

        if existing_users > 0 or existing_orders > 0:
            print(f"\n警告：数据库中已存在数据")
            print(f"  用户数：{existing_users}")
            print(f"  订单数：{existing_orders}")
            response = input("是否清空并重新生成？(y/n): ")
            if response.lower() != 'y':
                print("已取消")
                return

            # 清空数据
            db.query(Order).delete()
            db.query(User).delete()
            db.commit()
            print("✓ 已清空现有数据")

        # 创建测试用户
        users = create_test_users(db, count=10)
        user_ids = [user.id for user in users]

        # 创建测试订单（10000条，用于慢SQL测试）
        create_test_orders(db, user_ids, count=10000)

        # 显示统计信息
        print("\n" + "=" * 60)
        print("数据生成统计：")
        print(f"  用户总数：{db.query(User).count()}")
        print(f"  订单总数：{db.query(Order).count()}")
        print("=" * 60)

        print("\n✓ 测试数据生成完成！")
        print("\n现在可以测试慢SQL：")
        print("  1. 启动后端服务：uvicorn app.main:app --reload")
        print("  2. 启用慢SQL：POST /api/orders/debug/enable-slow-sql")
        print("  3. 查询用户订单：GET /api/orders/user/1")
        print("  4. 观察查询时间（应该很慢，因为没有索引）")

    except Exception as e:
        print(f"\n✗ 错误：{e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
