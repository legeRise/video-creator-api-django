from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from functionality import functionality as func
from .models import Imgpath
from .serializers import KeywordSerializer
import os
import boto3
from django.conf import settings


# Create your views here.
c = func.videoFunctions()
  
@api_view(['POST'])
def create(request):
    
  # step 1: Get Video title from user
  title =request.data.get("title")
  keywords =  c.title_to_keywords(title)
  pic_keywords,display_keywords = keywords.split("\n")
  pic_keywords  = pic_keywords.split(":")[1]
  display_keywords  = display_keywords.split(":")[1]


  print(pic_keywords)
  print(display_keywords)

  data = { "pic_keywords" : pic_keywords, "display_keywords" : display_keywords, "reverse" : True, "titlebar" : True}

  # step 1: Get Keywords from user
  print(request.data,'is the reqdata')
  keyword_data = KeywordSerializer(data=data)  
  if keyword_data.is_valid():
    key =keyword_data.save()

    # step 2: Download Images based on keywordsZ
    c.downloadImages(key.id,key.pic_keywords)  
    
    # choose a single image for each keyword and generate it's path
    best_image_paths =c.bestChoice(key.id,key.reverse,key.titlebar)
    string_paths = "|".join(best_image_paths)
    paths = Imgpath(fk=key,paths=string_paths)
    paths.save()

    #step 3: create video
    user_id,title= c.makeVideo(id=key.id,fk=key,reverse=key.reverse,titlebar=key.titlebar)
    local_video_path = os.path.join(settings.MEDIA_ROOT,user_id,'temp',f'{title}.mp4')  # because the other part is just MEDIA_ROOT and that is changed automatically
    
    
    # destination path of generated video
    destination = f'videos/{user_id}-{title}.mp4'
    print(local_video_path)
    print(destination)


    context = {'message':'Video Created!','title':f"{title}.mp4"}
    return Response(context)
 
  else:
    return Response(keyword_data.errors,status=status.HTTP_400_BAD_REQUEST)



   












