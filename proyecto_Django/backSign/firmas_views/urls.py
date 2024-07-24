from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter()
router.register(r'firma', views.FirmasViewSet, basename='firma')
urlpatterns = router.urls