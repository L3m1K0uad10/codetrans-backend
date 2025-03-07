from django.urls import path 

from .views import ProcessingView 


urlpatterns = [
    path("translate/", ProcessingView, name = "translate_code"),
]