from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse,HttpResponseBadRequest,FileResponse
from .functionality import functionality as func
from .functionality.functionality import toList,toString
from .models import Keyword   # can also do from webcreatorApp.models import Keyword  but "." can handle it so no need to mentione the App Name explicitly
from .models import Imgpath
from django.conf import settings
import json,os

# Create your views here.
c = func.videoFunctions()
  

def create(request):

  if request.method=='POST':
    data = json.loads(request.body)
    print(data," this is all info i received")

    imgkeywords = data.get('imgkeywords')
    display = data.get('display')
    reverse = bool(data.get('reverse'))
    titlebar =bool(data.get('titlebar'))
    print(imgkeywords)
    print(display)
    print(reverse)
    print(titlebar)
    if imgkeywords ==""  or display == "":
      return HttpResponseBadRequest(json.dumps({'message': 'All Fields Must be Filled'}), content_type='application/json')
    

    imgkeywords = toList(imgkeywords) 
    # removing spaces in search keywords as these keywords are to be used in path creation and spaces may result in error
    imgkeywords = [name.replace(" ", "") for name in imgkeywords] 
    display = toList(display)  # no need to remove spaces from display
    

    if len(imgkeywords) != len(display):
      return HttpResponseBadRequest(json.dumps({'message': 'Both Fields Should have Same Number of keywords'}), content_type='application/json')

    if not 3 <= len(imgkeywords) <=11:
      return HttpResponseBadRequest(json.dumps({'message': 'No of Keywords Should be between 3 and 10'}), content_type='application/json')
    try:
      # save keywords to database
      key = Keyword()
      key.pic_keywords = toString(imgkeywords)
      key.display_keywords= toString(display)
      key.save() 
      print('data was saved')
      
    #_________________________________ video creation starts______________________________________
    # Step1:  ImageDownloader
      c.imgdownloader(key.id,imgkeywords)

    # step2:  Pick the Best fitting images for each keyword
      best_image_paths =c.bestChoice(key.id,reverse,titlebar)
      string_paths = toString(best_image_paths,sep="|")
      paths = Imgpath(fk=key,paths=string_paths)
      paths.save()

    # step3: start making video  
      print('i did make it here step333')
      c.makeVideo(id=key.id,fk=key)

      c.textOnVideo(key.id,titlebar,reverse,duration=2)
  

      # preparing params 

      user_id= f"user_{key.id}"
      title = display[0].replace(" ","")
      print(' I WAS CREATING THE PATH')


      video_path = os.path.join('media',user_id,f'{title}.mp4')  # because the other part is just MEDIA_ROOT and that is changed automatically
      print(f' THE PATH WAS {video_path}')   
      params = {'user_id':user_id,'title':title,'message':'Video Created!','video_url':video_path}
      print(params)
      return JsonResponse(params)



 
    except Exception as e:

      return HttpResponseBadRequest(json.dumps({'message': 'Video could not be Created!'}), content_type='application/json')
  
    
  return HttpResponseBadRequest(json.dumps({'message': 'Only POST Request is Allowed'}), content_type='application/json')
    












