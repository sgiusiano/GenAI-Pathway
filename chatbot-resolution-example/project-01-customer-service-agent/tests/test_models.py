"""
Tests for Pydantic models

This module tests the data models used throughout the system.
"""

import pytest
from src.models.entities import ExtractedEntities
from src.models.query_analysis import QueryAnalysis
from src.models.conversation_summary import ConversationSummary


class TestExtractedEntities:
    """Test cases for ExtractedEntities model."""
    
    def test_valid_entities(self):
        """Test creating valid entities."""
        entities = ExtractedEntities(
            product_name="iPhone 15",
            order_number="TEC-2024001",
            date="tomorrow"
        )
        
        assert entities.product_name == "iPhone 15"
        assert entities.order_number == "TEC-2024001"
        assert entities.date == "tomorrow"
    
    def test_partial_entities(self):
        """Test creating entities with partial data."""
        entities = ExtractedEntities(product_name="laptop")
        
        assert entities.product_name == "laptop"
        assert entities.order_number is None
        assert entities.date is None
    
    def test_empty_entities(self):
        """Test creating empty entities."""
        entities = ExtractedEntities()
        
        assert entities.product_name is None
        assert entities.order_number is None
        assert entities.date is None


class TestQueryAnalysis:
    """Test cases for QueryAnalysis model."""
    
    def test_valid_analysis(self):
        """Test creating valid query analysis."""
        entities = ExtractedEntities(product_name="router")
        
        analysis = QueryAnalysis(
            query_category="technical_support",
            urgency_level="high",
            customer_sentiment="negative",
            entities=entities
        )
        
        assert analysis.query_category == "technical_support"
        assert analysis.urgency_level == "high"
        assert analysis.customer_sentiment == "negative"
        assert analysis.entities.product_name == "router"
    
    def test_invalid_category(self):
        """Test that invalid categories raise validation error."""
        entities = ExtractedEntities()
        
        with pytest.raises(ValueError):
            QueryAnalysis(
                query_category="invalid_category",
                urgency_level="low",
                customer_sentiment="neutral",
                entities=entities
            )
    
    def test_invalid_urgency(self):
        """Test that invalid urgency levels raise validation error."""
        entities = ExtractedEntities()
        
        with pytest.raises(ValueError):
            QueryAnalysis(
                query_category="product_inquiry",
                urgency_level="invalid_urgency",
                customer_sentiment="neutral",
                entities=entities
            )


class TestConversationSummary:
    """Test cases for ConversationSummary model."""
    
    def test_valid_summary(self):
        """Test creating valid conversation summary."""
        entities = ExtractedEntities(product_name="tablet")
        
        summary = ConversationSummary(
            timestamp="2024-01-15T10:30:00",
            customer_id="CUST-001",
            conversation_summary="Customer inquired about returns",
            query_category="returns",
            customer_sentiment="neutral",
            urgency_level="medium",
            mentioned_products=["tablet"],
            extracted_information=entities,
            resolution_status="resolved",
            actions_taken=["Provided return assistance"],
            follow_up_required=False
        )
        
        assert summary.timestamp == "2024-01-15T10:30:00"
        assert summary.customer_id == "CUST-001"
        assert summary.query_category == "returns"
        assert summary.follow_up_required is False
    
    def test_default_values(self):
        """Test default values for optional fields."""
        entities = ExtractedEntities()
        
        summary = ConversationSummary(
            timestamp="2024-01-15T10:30:00",
            conversation_summary="Test conversation",
            query_category="general_information",
            customer_sentiment="neutral",
            urgency_level="low",
            mentioned_products=[],
            extracted_information=entities,
            resolution_status="resolved",
            actions_taken=[],
            follow_up_required=False
        )
        
        assert summary.customer_id == "auto_generated"
        assert summary.mentioned_products == []
        assert summary.actions_taken == [] 