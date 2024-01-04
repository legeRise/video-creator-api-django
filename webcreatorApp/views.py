from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from functionality import functionality as func
from .models import Imgpath
from .serializers import KeywordSerializer
import os


# Create your views here.
c = func.videoFunctions()
  
@api_view(['POST'])
def create(request):

  # step 1: Get Keywords from user
  keyword_data = KeywordSerializer(data=request.data)  # make sure you mention "data=request.data" and not request.data
  if keyword_data.is_valid():
    key =keyword_data.save()

    # step 2: Download Images based on keywords
    c.downloadImages(key.id,key.pic_keywords)  
    
    # choose a single image for each keyword and generate it's path
    best_image_paths =c.bestChoice(key.id,key.reverse,key.titlebar)
    string_paths = "|".join(best_image_paths)
    paths = Imgpath(fk=key,paths=string_paths)
    paths.save()

    #step 3: create video
    user_id,title= c.makeVideo(id=key.id,fk=key,reverse=key.reverse,titlebar=key.titlebar)
    
    video_path = os.path.join('media',user_id,'temp',f'{title}.mp4')  # because the other part is just MEDIA_ROOT and that is changed automatically
    context = {'message':'Video Created!','user_id':user_id,'title':title,'video_url':video_path}
    return Response(context)
 
  else:
    return Response(keyword_data.errors,status=status.HTTP_400_BAD_REQUEST)



   












