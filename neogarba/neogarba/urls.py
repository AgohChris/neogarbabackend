from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.utilisateurs.urls')),
    # path('api/catalogue', include('apps.catalogue.urls')),
    # path('api/commandes', include('apps.commandes.urls')),
    # path('api/livraisons', include('apps.livraisons.urls')),
    # path('api/paiements', include('apps.paiements.urls')),
]
