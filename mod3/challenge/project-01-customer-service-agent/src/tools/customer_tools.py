from langchain_core.tools import tool
from src.database.mock_db import MockCustomerDB

class customerTools:

    @tool
    def get_customer_info(email: str) -> str:
        """Retrieve customer information by email address.
        
        Args:
            email: Customer's email address
            
        Returns:
            Customer data including personal details and account information
        """
        db = MockCustomerDB()
        customer_data = db.get_customer_by_email(email)
        return customer_data

    @tool
    def get_order_status(order_id: str) -> str:
        """Get the current status of a customer order.
        
        Args:
            order_id: Unique identifier for the order
            
        Returns:
            Order status information including current stage and details
        """
        db = MockCustomerDB()
        order_data = db.get_order_status(order_id)
        return order_data

    @tool
    def get_shipping_tracking(order_id: str) -> str:
        """Retrieve shipping and tracking information for an order.
        
        Args:
            order_id: Unique identifier for the order
            
        Returns:
            Shipping tracking details including carrier info and delivery status
        """
        db = MockCustomerDB()
        tracking_data = db.get_shipping_tracking(order_id)
        return tracking_data

    @tool
    def get_customer_tickets(email: str) -> str:
        """Retrieve all support tickets for a customer.
        
        Args:
            email: Customer's email address
            
        Returns:
            Customer support ticket history and current open tickets
        """
        db = MockCustomerDB()
        tickets_data = db.get_customer_tickets(email)
        return tickets_data
