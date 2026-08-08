import datetime
from src.db.database import init_db, SessionLocal
from src.db.models import (
    User,
    Product,
    Order,
    Ticket,
    PendingReview,
    ToolAuditLog,
    Conversation,
    Message,
    Feedback,
)
from src.utils.logger import logger


def seed_database() -> None:
    """Populates the database with realistic initial seed records."""
    init_db(recreate=True)
    db = SessionLocal()

    try:
        # Clear existing records in strict reverse foreign-key dependency order
        db.query(Feedback).delete()
        db.query(Message).delete()
        db.query(Conversation).delete()
        db.query(ToolAuditLog).delete()
        db.query(PendingReview).delete()
        db.query(Ticket).delete()
        db.query(Order).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()

        logger.info("Seeding users...")
        users = [
            User(id="user_demo", email="alex.demo@supportflow.ai", name="Alex Mercer", role="customer", status="active"),
            User(id="user_1", email="sarah.miller@example.com", name="Sarah Miller", role="customer", status="active"),
            User(id="user_2", email="david.chen@example.com", name="David Chen", role="customer", status="active"),
            User(id="user_3", email="elena.rostova@example.com", name="Elena Rostova", role="customer", status="active"),
            User(id="user_4", email="marcus.vance@example.com", name="Marcus Vance", role="customer", status="active"),
            User(id="user_5", email="priya.patel@example.com", name="Priya Patel", role="customer", status="active"),
            User(id="user_6", email="jordan.hayes@example.com", name="Jordan Hayes", role="customer", status="active"),
            User(id="user_7", email="hannah.schmidt@example.com", name="Hannah Schmidt", role="customer", status="active"),
            User(id="user_8", email="liam.oconnor@example.com", name="Liam O'Connor", role="customer", status="active"),
            User(id="user_9", email="chloe.dubois@example.com", name="Chloe Dubois", role="customer", status="active"),
            User(id="user_10", email="mateo.silva@example.com", name="Mateo Silva", role="customer", status="active"),
            User(id="user_11", email="aisha.khan@example.com", name="Aisha Khan", role="customer", status="active"),
            User(id="user_12", email="kevin.wright@example.com", name="Kevin Wright", role="customer", status="active"),
            User(id="user_13", email="emily.watson@example.com", name="Emily Watson", role="customer", status="active"),
            User(id="user_14", email="admin.support@supportflow.ai", name="Supervisor Admin", role="admin", status="active"),
        ]
        db.add_all(users)
        db.commit()

        logger.info("Seeding products...")
        products = [
            Product(id="prod_101", name="Pro Wireless Noise-Cancelling Headphones", sku="SF-HEAD-PRO", category="Audio", price=299.99, description="Active noise cancelling with 40-hour battery life.", in_stock=True),
            Product(id="prod_102", name="Ultra-Slim Mechanical Ergonomic Keyboard", sku="SF-KEY-MECH", category="Accessories", price=149.50, description="Hot-swappable tactile switches with RGB lighting.", in_stock=True),
            Product(id="prod_103", name="4K Ultra-HD IPS Monitor 27-inch", sku="SF-MON-4K27", category="Displays", price=429.00, description="99% sRGB color accuracy with USB-C 90W charging.", in_stock=True),
            Product(id="prod_104", name="Ergonomic Lumbar Mesh Office Chair", sku="SF-CHR-ERGO", category="Furniture", price=349.00, description="High-breathability mesh chair with 4D armrests.", in_stock=True),
            Product(id="prod_105", name="Smart USB-C Multiport Docking Station", sku="SF-DOC-USBC", category="Accessories", price=89.99, description="10-in-1 dual 4K HDMI hub with 100W Power Delivery.", in_stock=True),
            Product(id="prod_106", name="Precision Wireless Optical Gaming Mouse", sku="SF-MOU-OPT", category="Accessories", price=79.99, description="26,000 DPI sensor with sub-1ms wireless latency.", in_stock=True),
            Product(id="prod_107", name="Studio Quality Condenser USB Microphone", sku="SF-MIC-STUD", category="Audio", price=129.99, description="Cardioid pickup pattern with built-in pop filter.", in_stock=True),
            Product(id="prod_108", name="Adjustable Aluminum Laptop Stand", sku="SF-STA-ALUM", category="Accessories", price=49.99, description="Heavy-duty folding stand with heat dissipation.", in_stock=True),
        ]
        db.add_all(products)
        db.commit()

        logger.info("Seeding orders...")
        now = datetime.datetime.now(datetime.timezone.utc)
        orders = [
            # user_demo orders
            Order(id="ORD-1001", order_number="ORD-1001", user_id="user_demo", product_id="prod_101", product_name="Pro Wireless Noise-Cancelling Headphones", status="PROCESSING", total_amount=299.99, carrier="FedEx", tracking_number="FX-PENDING-1001", shipping_address="742 Evergreen Terrace, Springfield, IL 62704", created_at=now - datetime.timedelta(hours=4)),
            Order(id="ORD-1002", order_number="ORD-1002", user_id="user_demo", product_id="prod_102", product_name="Ultra-Slim Mechanical Ergonomic Keyboard", status="DELIVERED", total_amount=149.50, carrier="FedEx", tracking_number="FX-992817264", shipping_address="742 Evergreen Terrace, Springfield, IL 62704", created_at=now - datetime.timedelta(days=12)),
            Order(id="ORD-1003", order_number="ORD-1003", user_id="user_demo", product_id="prod_105", product_name="Smart USB-C Multiport Docking Station", status="SHIPPED", total_amount=89.99, carrier="UPS", tracking_number="1Z9999999999999999", shipping_address="742 Evergreen Terrace, Springfield, IL 62704", created_at=now - datetime.timedelta(days=2)),

            # Other user orders
            Order(id="ORD-1004", order_number="ORD-1004", user_id="user_1", product_id="prod_103", product_name="4K Ultra-HD IPS Monitor 27-inch", status="PROCESSING", total_amount=429.00, carrier="FedEx", tracking_number="FX-982103948", shipping_address="100 Market St, San Francisco, CA 94105", created_at=now - datetime.timedelta(hours=8)),
            Order(id="ORD-1005", order_number="ORD-1005", user_id="user_2", product_id="prod_104", product_name="Ergonomic Lumbar Mesh Office Chair", status="DELIVERED", total_amount=349.00, carrier="UPS", tracking_number="1Z8827364519283746", shipping_address="456 Elm St, Austin, TX 78701", created_at=now - datetime.timedelta(days=15)),
            Order(id="ORD-1006", order_number="ORD-1006", user_id="user_3", product_id="prod_101", product_name="Pro Wireless Noise-Cancelling Headphones", status="SHIPPED", total_amount=299.99, carrier="DHL", tracking_number="DHL-7726354123", shipping_address="88 King St, Seattle, WA 98104", created_at=now - datetime.timedelta(days=1)),
            Order(id="ORD-1007", order_number="ORD-1007", user_id="user_4", product_id="prod_106", product_name="Precision Wireless Optical Gaming Mouse", status="DELIVERED", total_amount=79.99, carrier="USPS", tracking_number="9400111899561234567890", shipping_address="12 Ocean Ave, Miami, FL 33139", created_at=now - datetime.timedelta(days=20)),
            Order(id="ORD-1008", order_number="ORD-1008", user_id="user_5", product_id="prod_107", product_name="Studio Quality Condenser USB Microphone", status="PROCESSING", total_amount=129.99, carrier="FedEx", tracking_number="FX-449102837", shipping_address="300 Pine St, Denver, CO 80202", created_at=now - datetime.timedelta(hours=14)),
            Order(id="ORD-1009", order_number="ORD-1009", user_id="user_6", product_id="prod_108", product_name="Adjustable Aluminum Laptop Stand", status="CANCELLED", total_amount=49.99, carrier="USPS", tracking_number=None, shipping_address="500 Broadway, New York, NY 10012", created_at=now - datetime.timedelta(days=5)),
            Order(id="ORD-1010", order_number="ORD-1010", user_id="user_7", product_id="prod_102", product_name="Ultra-Slim Mechanical Ergonomic Keyboard", status="DELIVERED", total_amount=149.50, carrier="FedEx", tracking_number="FX-110293847", shipping_address="21 Michigan Ave, Chicago, IL 60601", created_at=now - datetime.timedelta(days=18)),
            Order(id="ORD-1011", order_number="ORD-1011", user_id="user_8", product_id="prod_103", product_name="4K Ultra-HD IPS Monitor 27-inch", status="SHIPPED", total_amount=429.00, carrier="UPS", tracking_number="1Z4488339922110044", shipping_address="70 Peachtree St, Atlanta, GA 30303", created_at=now - datetime.timedelta(days=3)),
            Order(id="ORD-1012", order_number="ORD-1012", user_id="user_9", product_id="prod_101", product_name="Pro Wireless Noise-Cancelling Headphones", status="PROCESSING", total_amount=299.99, carrier="FedEx", tracking_number="FX-883726154", shipping_address="144 Beacon St, Boston, MA 02116", created_at=now - datetime.timedelta(hours=2)),
            Order(id="ORD-1013", order_number="ORD-1013", user_id="user_10", product_id="prod_104", product_name="Ergonomic Lumbar Mesh Office Chair", status="DELIVERED", total_amount=349.00, carrier="FedEx", tracking_number="FX-662718293", shipping_address="900 Grand Ave, Los Angeles, CA 90017", created_at=now - datetime.timedelta(days=22)),
            Order(id="ORD-1014", order_number="ORD-1014", user_id="user_11", product_id="prod_105", product_name="Smart USB-C Multiport Docking Station", status="DELIVERED", total_amount=89.99, carrier="DHL", tracking_number="DHL-9918273645", shipping_address="330 2nd Ave, Minneapolis, MN 55401", created_at=now - datetime.timedelta(days=8)),
            Order(id="ORD-1015", order_number="ORD-1015", user_id="user_12", product_id="prod_106", product_name="Precision Wireless Optical Gaming Mouse", status="PROCESSING", total_amount=79.99, carrier="FedEx", tracking_number="FX-550192837", shipping_address="112 Main St, Portland, OR 97201", created_at=now - datetime.timedelta(hours=6)),
            Order(id="ORD-1016", order_number="ORD-1016", user_id="user_13", product_id="prod_107", product_name="Studio Quality Condenser USB Microphone", status="SHIPPED", total_amount=129.99, carrier="UPS", tracking_number="1Z1122334455667788", shipping_address="77 Wall St, New York, NY 10005", created_at=now - datetime.timedelta(days=1)),
            Order(id="ORD-1017", order_number="ORD-1017", user_id="user_1", product_id="prod_108", product_name="Adjustable Aluminum Laptop Stand", status="DELIVERED", total_amount=49.99, carrier="USPS", tracking_number="9400111899569988776655", shipping_address="100 Market St, San Francisco, CA 94105", created_at=now - datetime.timedelta(days=25)),
            Order(id="ORD-1018", order_number="ORD-1018", user_id="user_2", product_id="prod_101", product_name="Pro Wireless Noise-Cancelling Headphones", status="REFUNDED", total_amount=299.99, carrier="FedEx", tracking_number="FX-338822991", shipping_address="456 Elm St, Austin, TX 78701", created_at=now - datetime.timedelta(days=30)),
            Order(id="ORD-1019", order_number="ORD-1019", user_id="user_3", product_id="prod_102", product_name="Ultra-Slim Mechanical Ergonomic Keyboard", status="PROCESSING", total_amount=149.50, carrier="FedEx", tracking_number="FX-776655443", shipping_address="88 King St, Seattle, WA 98104", created_at=now - datetime.timedelta(hours=10)),
            Order(id="ORD-1020", order_number="ORD-1020", user_id="user_4", product_id="prod_105", product_name="Smart USB-C Multiport Docking Station", status="DELIVERED", total_amount=89.99, carrier="UPS", tracking_number="1Z7788990011223344", shipping_address="12 Ocean Ave, Miami, FL 33139", created_at=now - datetime.timedelta(days=14)),
        ]
        db.add_all(orders)
        db.commit()

        logger.info("Seeding open tickets...")
        tickets = [
            Ticket(id="TICK-5001", ticket_number="TICK-5001", user_id="user_demo", title="Inquiry about 4K Monitor compatibility", description="Customer asked whether USB-C 90W charging is compatible with 2024 MacBook Air.", priority="LOW", status="RESOLVED", category="PRODUCT_INFO"),
            Ticket(id="TICK-5002", ticket_number="TICK-5002", user_id="user_3", title="Damaged packaging upon arrival", description="Customer reported outer box crushed by delivery carrier; contents inspected.", priority="MEDIUM", status="PENDING_REVIEW", category="SHIPPING"),
            Ticket(id="TICK-5003", ticket_number="TICK-5003", user_id="user_5", title="Billing discrepancy on monthly invoice", description="Customer requested credit clarification on promo discount.", priority="LOW", status="OPEN", category="BILLING"),
            Ticket(id="TICK-5004", ticket_number="TICK-5004", user_id="user_8", title="Account lockout after 5 password attempts", description="Automated security freeze triggered due to failed password attempts.", priority="HIGH", status="OPEN", category="SECURITY"),
            Ticket(id="TICK-5005", ticket_number="TICK-5005", user_id="user_10", title="Return label download link expired", description="Customer requested re-issuance of prepaid return shipping label.", priority="LOW", status="OPEN", category="REFUND"),
        ]
        db.add_all(tickets)
        db.commit()

        logger.info(f"Seed complete: {len(users)} users, {len(products)} products, {len(orders)} orders, {len(tickets)} tickets.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
