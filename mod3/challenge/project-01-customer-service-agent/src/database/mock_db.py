import sqlite3
import json
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict


@dataclass
class Customer:
    id: str
    email: str
    name: str
    category: str
    status: str
    registration_date: str


@dataclass
class Order:
    id: str
    order_number: str
    customer_id: str
    products: list[dict[str, Any]]
    status: str
    tracking_number: str | None
    total_amount: float


@dataclass
class SupportTicket:
    id: str
    ticket_number: str
    customer_id: str
    category: str
    priority: str
    status: str
    description: str


class MockCustomerDB:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
        self._populate_sample_data()

    def _initialize_database(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        # Create Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                registration_date TEXT NOT NULL
            )
        """)
        
        # Create Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                order_number TEXT UNIQUE NOT NULL,
                customer_id TEXT NOT NULL,
                products TEXT NOT NULL,
                status TEXT NOT NULL,
                tracking_number TEXT,
                total_amount REAL NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Create Support Tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id TEXT PRIMARY KEY,
                ticket_number TEXT UNIQUE NOT NULL,
                customer_id TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        self.connection.commit()

    def _populate_sample_data(self):
        # Sample customers
        sample_customers = [
            Customer(
                id="CUST-001",
                email="john.smith@email.com",
                name="John Smith",
                category="premium",
                status="active",
                registration_date="2023-01-15"
            ),
            Customer(
                id="CUST-002",
                email="sarah.johnson@email.com",
                name="Sarah Johnson",
                category="standard",
                status="active",
                registration_date="2023-02-20"
            ),
            Customer(
                id="CUST-003",
                email="michael.brown@email.com",
                name="Michael Brown",
                category="premium",
                status="inactive",
                registration_date="2023-03-10"
            ),
            Customer(
                id="CUST-004",
                email="emily.davis@email.com",
                name="Emily Davis",
                category="standard",
                status="active",
                registration_date="2023-04-05"
            ),
            Customer(
                id="CUST-005",
                email="david.wilson@email.com",
                name="David Wilson",
                category="vip",
                status="active",
                registration_date="2023-05-12"
            )
        ]
        
        # Sample orders
        sample_orders = [
            Order(
                id="ORD-001",
                order_number="ON-2024-001",
                customer_id="CUST-001",
                products=[
                    {"name": "Laptop", "quantity": 1, "price": 999.99},
                    {"name": "Mouse", "quantity": 1, "price": 29.99}
                ],
                status="delivered",
                tracking_number="TRK-12345",
                total_amount=1029.98
            ),
            Order(
                id="ORD-002",
                order_number="ON-2024-002",
                customer_id="CUST-002",
                products=[
                    {"name": "Smartphone", "quantity": 1, "price": 699.99}
                ],
                status="shipped",
                tracking_number="TRK-12346",
                total_amount=699.99
            ),
            Order(
                id="ORD-003",
                order_number="ON-2024-003",
                customer_id="CUST-004",
                products=[
                    {"name": "Headphones", "quantity": 2, "price": 149.99}
                ],
                status="in_transit",
                tracking_number=None,
                total_amount=299.98
            ),
            Order(
                id="ORD-004",
                order_number="ON-2024-004",
                customer_id="CUST-005",
                products=[
                    {"name": "Tablet", "quantity": 1, "price": 399.99},
                    {"name": "Case", "quantity": 1, "price": 49.99}
                ],
                status="pending",
                tracking_number=None,
                total_amount=449.98
            )
        ]
        
        # Sample support tickets
        sample_tickets = [
            SupportTicket(
                id="TKT-001",
                ticket_number="TN-2024-001",
                customer_id="CUST-001",
                category="technical",
                priority="high",
                status="open",
                description="Laptop not turning on after recent update"
            ),
            SupportTicket(
                id="TKT-002",
                ticket_number="TN-2024-002",
                customer_id="CUST-002",
                category="billing",
                priority="medium",
                status="resolved",
                description="Question about refund policy"
            ),
            SupportTicket(
                id="TKT-003",
                ticket_number="TN-2024-003",
                customer_id="CUST-004",
                category="shipping",
                priority="low",
                status="pending",
                description="Delivery address change request"
            ),
            SupportTicket(
                id="TKT-004",
                ticket_number="TN-2024-004",
                customer_id="CUST-005",
                category="technical",
                priority="urgent",
                status="in_progress",
                description="Critical system error affecting business operations"
            )
        ]
        
        # Insert sample data
        for customer in sample_customers:
            self.create_customer(customer)
        for order in sample_orders:
            self.create_order(order)
        for ticket in sample_tickets:
            self.create_support_ticket(ticket)

    # Customer CRUD operations
    def create_customer(self, customer: Customer) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO customers 
                (id, email, name, category, status, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                customer.id,
                customer.email,
                customer.name,
                customer.category,
                customer.status,
                customer.registration_date
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating customer: {e}")
            return False

    def get_customer_by_email(self, email: str) -> str:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row:
                return f"""Customer Information:
                    - ID: {row['id']}
                    - Name: {row['name']}
                    - Email: {row['email']}
                    - Category: {row['category']}
                    - Status: {row['status']}
                    - Registration Date: {row['registration_date']}
                """
            return f"Customer with email '{email}' not found in database"
        except sqlite3.Error as e:
            return f"Error retrieving customer by email: {e}"

    def get_customer_tickets(self, email: str) -> str:
        try:
            cursor = self.connection.cursor()
            # First get customer ID from email
            cursor.execute("SELECT id FROM customers WHERE email = ?", (email,))
            customer_row = cursor.fetchone()
            
            if not customer_row:
                return f"Customer with email '{email}' not found in database"
            
            customer_id = customer_row['id']
            
            # Get all tickets for this customer
            cursor.execute("SELECT * FROM support_tickets WHERE customer_id = ?", (customer_id,))
            ticket_rows = cursor.fetchall()
            
            if not ticket_rows:
                return f"No support tickets found for customer with email '{email}'"
            
            tickets_info = f"Support Tickets for {email}:\n"
            for ticket in ticket_rows:
                tickets_info += f"""
                    - Ticket ID: {ticket['id']}
                    - Ticket Number: {ticket['ticket_number']}
                    - Category: {ticket['category']}
                    - Priority: {ticket['priority']}
                    - Status: {ticket['status']}
                    - Description: {ticket['description']}
                """
            
            return tickets_info
        except sqlite3.Error as e:
            return f"Error retrieving customer tickets: {e}"

    # Order CRUD operations
    def create_order(self, order: Order) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO orders 
                (id, order_number, customer_id, products, status, tracking_number, total_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                order.id,
                order.order_number,
                order.customer_id,
                json.dumps(order.products),
                order.status,
                order.tracking_number,
                order.total_amount
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating order: {e}")
            return False

    def get_order_status(self, order_id: str) -> str:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            
            if row:
                return f"""Order Information:
                    - Order ID: {row['id']}
                    - Order Number: {row['order_number']}
                    - Customer ID: {row['customer_id']}
                    - Status: {row['status']}
                """
            return f"Order with ID '{order_id}' not found in database"
        except sqlite3.Error as e:
            return f"Error retrieving order by number: {e}"

    def get_shipping_tracking(self, order_id: str) -> str:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            
            if row:
                if row['status'] == 'pending':
                    return f"""Shipping & Tracking Information:
                    - Order ID: {row['id']}
                    - Order Number: {row['order_number']}
                    - Status: {row['status']}
                    - Tracking Number: Not yet assigned
                    - Shipping Status: Order is being prepared for shipment
                """
                elif row['status'] == 'in_transit':
                    tracking_num = row['tracking_number'] if row['tracking_number'] else "Not assigned"
                    return f"""Shipping & Tracking Information:
                    - Order ID: {row['id']}
                    - Order Number: {row['order_number']}
                    - Status: {row['status']}
                    - Tracking Number: {tracking_num}
                    - Shipping Status: Package is currently in transit to destination
                    - Estimated Delivery: 1-3 business days
                """
                elif row['status'] == 'delivered':
                    tracking_num = row['tracking_number'] if row['tracking_number'] else "Not assigned"
                    return f"""Shipping & Tracking Information:
                    - Order ID: {row['id']}
                    - Order Number: {row['order_number']}
                    - Status: {row['status']}
                    - Tracking Number: {tracking_num}
                    - Shipping Status: Package has been successfully delivered
                    - Delivery Date: Completed
                """
                elif row['status'] == 'canceled':
                    tracking_num = row['tracking_number'] if row['tracking_number'] else "Not assigned"
                    return f"""Shipping & Tracking Information:
                    - Order ID: {row['id']}
                    - Order Number: {row['order_number']}
                    - Status: {row['status']}
                    - Tracking Number: {tracking_num}
                    - Shipping Status: Order has been cancelled
                    - Delivery Date: N/A
                """
                else:
                    return f"""Shipping & Tracking Information:
                    - Order ID: {row['id']}
                    - Order Number: {row['order_number']}
                    - Status: {row['status']}
                    - Tracking Number: Not available
                    - Shipping Status: Please contact customer service for assistance
                """
            return f"Order with ID '{order_id}' not found in database"
        except sqlite3.Error as e:
            return f"Error retrieving shipping tracking information: {e}"

    # Support Ticket CRUD operations
    def create_support_ticket(self, ticket: SupportTicket) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO support_tickets 
                (id, ticket_number, customer_id, category, priority, status, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket.id,
                ticket.ticket_number,
                ticket.customer_id,
                ticket.category,
                ticket.priority,
                ticket.status,
                ticket.description
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating support ticket: {e}")
            return False

    def close(self):
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
