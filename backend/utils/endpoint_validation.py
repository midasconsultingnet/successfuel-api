from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable
from utils.security import verify_token, is_admin_user_type
from services.auth_service import log_unauthorized_access_attempt
from services.auth_service import get_user_by_id
import uuid


class EndpointValidationMiddleware:
    """
    Middleware to validate that users access the correct endpoints based on their type
    """
    
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        
        # Check if this is an admin endpoint
        path = request.url.path
        is_admin_endpoint = path.startswith('/api/v1/admin/')
        
        # For non-API routes, skip validation
        if not path.startswith('/api/'):
            return await self.app(scope, receive, send)

        # Skip validation for authentication routes (login, register, etc.)
        if path in ['/api/v1/auth/login', '/api/v1/admin/login', '/api/v1/auth/refresh'] or \
           path.startswith('/api/v1/auth/login') or path.startswith('/api/v1/admin/login'):
            return await self.app(scope, receive, send)

        # Check for auth token in headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # For API routes, authentication is required
            if path.startswith('/api/'):
                return await self.send_error_response(
                    scope,
                    receive,
                    send,
                    status.HTTP_401_UNAUTHORIZED,
                    "Not authenticated"
                )
        
        if auth_header:
            token = auth_header.replace("Bearer ", "")
            payload = verify_token(token)
            
            if not payload:
                # Invalid token
                return await self.send_error_response(
                    scope,
                    receive,
                    send,
                    status.HTTP_401_UNAUTHORIZED,
                    "Invalid or expired token"
                )
            
            user_type = payload.get("type_utilisateur", "utilisateur_compagnie")
            token_endpoint_type = payload.get("type_endpoint", "utilisateur")
            
            # Check if the user is trying to access the wrong endpoint type
            if is_admin_endpoint:
                # This is an admin endpoint
                if not is_admin_user_type(user_type):
                    # Non-admin user trying to access admin endpoint
                    user_id = payload.get("sub")
                    if user_id:
                        # Log unauthorized access attempt
                        # For this implementation we'll just use a placeholder function
                        # In a real implementation, you would have a database session
                        # For now we'll use print to log it
                        print(f"Unauthorized access attempt to admin endpoint by user {user_id} (type: {user_type})")
                    
                    return await self.send_error_response(
                        scope,
                        receive,
                        send,
                        status.HTTP_403_FORBIDDEN,
                        "Access denied: Admin endpoints can only be accessed by admin users"
                    )
                
                # Admin user accessing admin endpoint - check token type
                if token_endpoint_type != "administrateur":
                    user_id = payload.get("sub")
                    if user_id:
                        print(f"User {user_id} with admin rights tried to access admin endpoint with user token")
                    
                    return await self.send_error_response(
                        scope,
                        receive,
                        send,
                        status.HTTP_403_FORBIDDEN,
                        "Access denied: Admin endpoint requires admin token"
                    )
            else:
                # This is a user endpoint (not admin)
                if is_admin_user_type(user_type) and path.startswith('/api/v1/'):
                    # Admin user accessing user endpoint - this is not allowed
                    # Except for auth routes which both can access
                    if not path.startswith('/api/v1/auth/'):
                        user_id = payload.get("sub")
                        if user_id:
                            print(f"Admin user {user_id} tried to access user endpoint")
                        
                        return await self.send_error_response(
                            scope,
                            receive,
                            send,
                            status.HTTP_403_FORBIDDEN,
                            "Access denied: Admin users should use admin endpoints"
                        )
                
                # For user endpoints, ensure token is for user endpoint
                if token_endpoint_type != "utilisateur" and not path.startswith('/api/v1/auth/'):
                    user_id = payload.get("sub")
                    if user_id:
                        print(f"User {user_id} tried to access user endpoint with admin token")
                    
                    return await self.send_error_response(
                        scope,
                        receive,
                        send,
                        status.HTTP_403_FORBIDDEN,
                        "Access denied: User endpoint requires user token"
                    )
        
        # If validation passes, continue with the request
        return await self.app(scope, receive, send)

    async def send_error_response(self, scope, receive, send, status_code: int, detail: str):
        """
        Send an error response
        """
        response = JSONResponse(
            status_code=status_code,
            content={"detail": detail}
        )
        await response(scope, receive, send)


def setup_endpoint_validation(app):
    """
    Add the endpoint validation middleware to the app
    """
    app.add_middleware(EndpointValidationMiddleware)