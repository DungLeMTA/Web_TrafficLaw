from django.urls import  path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('process/',views.process,name='process'),
    path('speechToText/',views.speechToText,name='speechToText'),
    path('textToSpeech/',views.textToSpeech,name='textToSpeech'),
]