from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from functionality import functionality as func
from .models import Imgpath
from .serializers import KeywordSerializer
import os
from django.conf import settings


# Create your views here.
c = func.videoFunctions()
  
@api_view(['POST'])
def create(request):
    
  # step 1: Get Video title from user and generate keywords based on the title
  title =request.data.get("title")
  title = func.custom_title(title)
  print(os.getcwd(),'line 20')
  keywords =  c.title_to_keywords(title)
  pic_keywords,display_keywords = keywords.split("\n")
  pic_keywords  = pic_keywords.split(":")[1]
  display_keywords  = display_keywords.split(":")[1]



  pic_keywords  = title +','+ pic_keywords
  display_keywords  = title +','+ display_keywords
  print(pic_keywords)
  print(display_keywords)

  data = { "pic_keywords" : pic_keywords, "display_keywords" : display_keywords, "reverse" : True, "titlebar" : True}
  keyword_data = KeywordSerializer(data=data)  
  if keyword_data.is_valid():
    key =keyword_data.save()
    test_keywords =  key.pic_keywords
    print(test_keywords,'are the keywords before downloading images')
    print(len(test_keywords.split(",")),"total keywordds count")
    
    # step 2: Download Images based on the generated keywords
    c.downloadImages(key.id,key.pic_keywords)  
    
    # step 3: from downloaded images choose a single image for each keyword and generate it's path
    best_image_paths =c.bestChoice(key.id,key.reverse,key.titlebar)
    print(len(best_image_paths),best_image_paths,"best image paths count")
    string_paths = "|".join(best_image_paths)
    paths = Imgpath(fk=key,paths=string_paths)
    paths.save()

    #step 3: create video
    video_id,title= c.makeVideo(id=key.id,fk=key,reverse=key.reverse,titlebar=key.titlebar)
    video_dir = os.path.join(settings.BASE_DIR,settings.MEDIA_ROOT,video_id)
    print(video_dir,'is the local 54----')
    local_video_path = os.path.join(video_dir,f'{title}.mp4')  # because the other part is just MEDIA_ROOT and that is changed automatically
    print(local_video_path,'is the local 55')
    # upload to gooogle drive for sharing
    generated_video_link = c.upload_to_drive(title,local_video_path,settings.SERVICE_ACCOUNT_FILE,settings.DRIVE_PARENT_FOLDER_ID)
    print(os.getcwd(),'line 54------\n\n\n\n')

    # returning to main 'media' folder
    os.chdir("..")
    print(os.getcwd(),"line no 62 views.py")
    # remove the temp video folder from media dir as video is uploaded to drive
    func.remove_directory(video_dir)
    
    
    context = {'message':'Video Created!',"link": generated_video_link}
    return Response(context)
 
  else:
    return Response(keyword_data.errors,status=status.HTTP_400_BAD_REQUEST)



   












