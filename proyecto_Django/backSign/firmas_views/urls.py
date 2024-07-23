from rest_framework.routers import DefaultRouter
from .views import FirmasViewSet

router = DefaultRouter()
router.register(r'firmas', FirmasViewSet, basename='firma')
urlpatterns = router.urls
