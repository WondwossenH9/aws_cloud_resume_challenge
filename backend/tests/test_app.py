"""
Unit tests for the Cloud Resume Challenge Lambda function
"""

import json
import pytest
import boto3
from moto import mock_dynamodb
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import (
    lambda_handler,
    get_visitor_count,
    increment_visitor_count,
    create_response,
    decimal_default,
    validate_request
)


class TestLambdaHandler:
    """Test cases for the main lambda_handler function"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        os.environ['TABLE_NAME'] = 'test-visitor-count'
    
    def teardown_method(self):
        """Clean up after each test"""
        if 'TABLE_NAME' in os.environ:
            del os.environ['TABLE_NAME']
    
    @mock_dynamodb
    def test_get_visitor_count_success(self):
        """Test successful GET request for visitor count"""
        # Create mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add initial data
        table.put_item(Item={'id': 'main', 'count': 42})
        
        # Test event
        event = {
            'httpMethod': 'GET',
            'headers': {},
            'body': None
        }
        
        # Mock context
        context = MagicMock()
        context.aws_request_id = 'test-request-id'
        
        # Call handler
        response = lambda_handler(event, context)
        
        # Assertions
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 42
        assert body['message'] == 'Visitor count retrieved successfully'
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    @mock_dynamodb
    def test_increment_visitor_count_success(self):
        """Test successful POST request to increment visitor count"""
        # Create mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add initial data
        table.put_item(Item={'id': 'main', 'count': 10})
        
        # Test event
        event = {
            'httpMethod': 'POST',
            'headers': {},
            'body': None
        }
        
        # Mock context
        context = MagicMock()
        context.aws_request_id = 'test-request-id'
        
        # Call handler
        response = lambda_handler(event, context)
        
        # Assertions
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 11
        assert body['message'] == 'Visitor count incremented successfully'
    
    def test_cors_preflight_request(self):
        """Test CORS preflight OPTIONS request"""
        event = {
            'httpMethod': 'OPTIONS',
            'headers': {},
            'body': None
        }
        
        context = MagicMock()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'CORS preflight successful'
    
    def test_invalid_method(self):
        """Test request with invalid HTTP method"""
        event = {
            'httpMethod': 'DELETE',
            'headers': {},
            'body': None
        }
        
        context = MagicMock()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert 'error' in body


class TestHelperFunctions:
    """Test cases for helper functions"""
    
    def test_create_response(self):
        """Test create_response function"""
        body = {'message': 'test'}
        response = create_response(200, body)
        
        assert response['statusCode'] == 200
        assert response['body'] == json.dumps(body)
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    def test_decimal_default(self):
        """Test decimal_default function"""
        from decimal import Decimal
        
        # Test with Decimal
        result = decimal_default(Decimal('42'))
        assert result == 42
        
        # Test with non-Decimal (should raise TypeError)
        with pytest.raises(TypeError):
            decimal_default('not a decimal')
    
    def test_validate_request(self):
        """Test validate_request function"""
        # Valid requests
        assert validate_request({'httpMethod': 'GET'})
        assert validate_request({'httpMethod': 'POST'})
        assert validate_request({'httpMethod': 'OPTIONS'})
        
        # Invalid requests
        assert not validate_request({'httpMethod': 'DELETE'})
        assert not validate_request({'httpMethod': 'PUT'})
        assert not validate_request({})


class TestDynamoDBOperations:
    """Test cases for DynamoDB operations"""
    
    def setup_method(self):
        """Set up test environment"""
        os.environ['TABLE_NAME'] = 'test-visitor-count'
    
    def teardown_method(self):
        """Clean up after each test"""
        if 'TABLE_NAME' in os.environ:
            del os.environ['TABLE_NAME']
    
    @mock_dynamodb
    def test_get_visitor_count_existing_record(self):
        """Test getting visitor count when record exists"""
        # Create mock table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item={'id': 'main', 'count': 100})
        
        # Test function
        count = get_visitor_count()
        assert count == 100
    
    @mock_dynamodb
    def test_get_visitor_count_no_record(self):
        """Test getting visitor count when no record exists"""
        # Create mock table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Test function (should create record with count 0)
        count = get_visitor_count()
        assert count == 0
        
        # Verify record was created
        response = table.get_item(Key={'id': 'main'})
        assert 'Item' in response
        assert response['Item']['count'] == 0
    
    @mock_dynamodb
    def test_increment_visitor_count_existing_record(self):
        """Test incrementing visitor count when record exists"""
        # Create mock table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item={'id': 'main', 'count': 50})
        
        # Test function
        new_count = increment_visitor_count()
        assert new_count == 51
        
        # Verify in database
        response = table.get_item(Key={'id': 'main'})
        assert response['Item']['count'] == 51
    
    @mock_dynamodb
    def test_increment_visitor_count_no_record(self):
        """Test incrementing visitor count when no record exists"""
        # Create mock table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Test function (should create record with count 1)
        new_count = increment_visitor_count()
        assert new_count == 1
        
        # Verify record was created
        response = table.get_item(Key={'id': 'main'})
        assert 'Item' in response
        assert response['Item']['count'] == 1


class TestErrorHandling:
    """Test cases for error handling"""
    
    @patch('app.table')
    def test_get_visitor_count_dynamodb_error(self, mock_table):
        """Test error handling in get_visitor_count"""
        # Mock DynamoDB error
        mock_table.get_item.side_effect = Exception("DynamoDB error")
        
        with pytest.raises(Exception):
            get_visitor_count()
    
    @patch('app.table')
    def test_increment_visitor_count_dynamodb_error(self, mock_table):
        """Test error handling in increment_visitor_count"""
        # Mock DynamoDB error
        mock_table.update_item.side_effect = Exception("DynamoDB error")
        mock_table.put_item.side_effect = Exception("DynamoDB error")
        
        with pytest.raises(Exception):
            increment_visitor_count()
    
    def test_lambda_handler_malformed_event(self):
        """Test lambda handler with malformed event"""
        event = None
        context = MagicMock()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body


# Integration test
class TestIntegration:
    """Integration tests"""
    
    @mock_dynamodb
    def test_full_workflow(self):
        """Test the complete workflow: GET -> POST -> GET"""
        # Set up environment
        os.environ['TABLE_NAME'] = 'test-visitor-count'
        
        # Create mock table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-visitor-count',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        context = MagicMock()
        context.aws_request_id = 'test-request-id'
        
        # Test 1: Initial GET (should return 0)
        get_event = {'httpMethod': 'GET', 'headers': {}, 'body': None}
        response = lambda_handler(get_event, context)
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 0
        
        # Test 2: POST to increment
        post_event = {'httpMethod': 'POST', 'headers': {}, 'body': None}
        response = lambda_handler(post_event, context)
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 1
        
        # Test 3: GET again (should return 1)
        response = lambda_handler(get_event, context)
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 1
        
        # Clean up
        del os.environ['TABLE_NAME']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
