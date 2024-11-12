from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import SignUpSerializer

class SignUpView(CreateAPIView):
    """API endpoint for user registration."""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]  # Ensure anyone can access this endpoint

    def post(self, request, *args, **kwargs):
        """Handle POST request to create a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validates input data
        self.perform_create(serializer)
        return Response(
            {"message": "User created successfully."},
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        """Save the serializer to create the user."""
        serializer.save()
