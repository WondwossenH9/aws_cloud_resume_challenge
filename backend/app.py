"""
AWS Lambda function for Cloud Resume Challenge
Handles visitor count operations for the resume website
"""

import json
import boto3
import os
from decimal import Decimal
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'visitor-count')
table = dynamodb.Table(table_name)

# CORS headers for API Gateway
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
}


def create_response(status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Create a standardized API Gateway response
    
    Args:
        status_code: HTTP status code
        body: Response body as dictionary
        headers: Optional additional headers
    
    Returns:
        API Gateway response format
    """
    response_headers = CORS_HEADERS.copy()
    if headers:
        response_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps(body, default=decimal_default)
    }


def decimal_default(obj):
    """
    JSON serializer for Decimal objects from DynamoDB
    
    Args:
        obj: Object to serialize
    
    Returns:
        Serialized object
    """
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError


def get_visitor_count() -> int:
    """
    Retrieve the current visitor count from DynamoDB
    
    Returns:
        Current visitor count
    """
    try:
        response = table.get_item(
            Key={'id': 'main'}
        )
        
        if 'Item' in response:
            return response['Item']['count']
        else:
            # Initialize with 0 if no record exists
            logger.info("No visitor count record found, initializing with 0")
            table.put_item(
                Item={
                    'id': 'main',
                    'count': 0
                }
            )
            return 0
            
    except Exception as e:
        logger.error(f"Error getting visitor count: {str(e)}")
        raise


def increment_visitor_count() -> int:
    """
    Increment the visitor count in DynamoDB atomically
    
    Returns:
        New visitor count after increment
    """
    try:
        response = table.update_item(
            Key={'id': 'main'},
            UpdateExpression='ADD #count :increment',
            ExpressionAttributeNames={'#count': 'count'},
            ExpressionAttributeValues={':increment': 1},
            ReturnValues='UPDATED_NEW'
        )
        
        return response['Attributes']['count']
        
    except Exception as e:
        logger.error(f"Error incrementing visitor count: {str(e)}")
        # If the item doesn't exist, create it with count 1
        try:
            table.put_item(
                Item={
                    'id': 'main',
                    'count': 1
                }
            )
            return 1
        except Exception as create_error:
            logger.error(f"Error creating initial visitor count: {str(create_error)}")
            raise


def validate_request(event: Dict[str, Any]) -> bool:
    """
    Validate the incoming request
    
    Args:
        event: API Gateway event
    
    Returns:
        True if request is valid
    """
    # Add any validation logic here
    # For now, we'll just check if it's a valid HTTP method
    http_method = event.get('httpMethod', '')
    return http_method in ['GET', 'POST', 'OPTIONS']


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function
    
    Args:
        event: API Gateway event
        context: Lambda context
    
    Returns:
        API Gateway response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {'message': 'CORS preflight successful'})
        
        # Validate request
        if not validate_request(event):
            return create_response(400, {'error': 'Invalid request method'})
        
        http_method = event.get('httpMethod', '')
        
        if http_method == 'GET':
            # Get current visitor count
            count = get_visitor_count()
            return create_response(200, {
                'count': count,
                'message': 'Visitor count retrieved successfully'
            })
            
        elif http_method == 'POST':
            # Increment visitor count
            new_count = increment_visitor_count()
            return create_response(200, {
                'count': new_count,
                'message': 'Visitor count incremented successfully'
            })
        
        else:
            return create_response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        })


# Health check function for testing
def health_check() -> Dict[str, Any]:
    """
    Simple health check function
    
    Returns:
        Health status
    """
    try:
        # Try to access DynamoDB table
        table.describe_table()
        return {
            'status': 'healthy',
            'table': table_name,
            'timestamp': str(context.aws_request_id) if 'context' in globals() else 'unknown'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'table': table_name
        }


# Test function for local development
if __name__ == "__main__":
    # Mock event for testing
    test_event = {
        'httpMethod': 'GET',
        'headers': {},
        'body': None
    }
    
    class MockContext:
        aws_request_id = 'test-request-id'
    
    test_context = MockContext()
    
    # Test GET request
    print("Testing GET request:")
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))
    
    # Test POST request
    test_event['httpMethod'] = 'POST'
    print("\nTesting POST request:")
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))
