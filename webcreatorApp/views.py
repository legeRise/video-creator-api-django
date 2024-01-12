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
    local_video_path = os.path.join(settings.MEDIA_ROOT,user_id,'temp',f'{title}.mp4')  # because the other part is just MEDIA_ROOT and that is changed automatically
    

    # making connection to s3 bucket (AWS)
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_S3_REGION_NAME)
    
    # destination path of generated video
    destination = f'videos/{user_id}-{title}.mp4'
    
    s3.upload_file(local_video_path, settings.AWS_STORAGE_BUCKET_NAME, destination)
    temporary_link =s3.generate_presigned_url('get_object',Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,'Key': destination},ExpiresIn=60*60*3)   # 3 hours


    context = {'message':'Video Created!','title':f"{title}.mp4","download_link":temporary_link,"Link_Validity":"3 Hours"}
    return Response(context)
 
  else:
    return Response(keyword_data.errors,status=status.HTTP_400_BAD_REQUEST)



   












