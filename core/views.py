from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSignupSerializer
from .models import TelegramUser

@api_view(['GET'])
def home_view(request):
    return Response({"message": "Welcome to the API Home"})

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        try:
            tg = TelegramUser.objects.get(username=user.username)
            tg.user = user
            tg.save()
        except TelegramUser.DoesNotExist:
            pass
        return Response({'message': 'User registered'})
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def public_view(request):
    return Response({"message": "This is a public endpoint."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello {request.user.username}, you are authenticated!"})
