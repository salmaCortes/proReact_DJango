from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrearDocViewSet, FirmarDoc

router = DefaultRouter()
router.register(r'documentos', CrearDocViewSet, basename='documento')

urlpatterns = [
    path('', include(router.urls)),
    path('firmaDoc/', FirmarDoc.as_view(), name='firmaDoc')
]
