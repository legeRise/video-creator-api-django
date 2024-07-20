import os
import shutil
import time
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips,AudioFileClip
from webcreatorApp.models import Keyword
from webcreatorApp.models import Imgpath
from .function_wrap_center import add_text_to_image
from django.conf import settings
from django.conf import settings
from gtts import gTTS
import pollinations.ai as ai  # image ai

# for interacting with gemini
import google.generativeai as genai

#for uploading file to google drive
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


#_________________________________________________________________________________________________________
# some helper functions are here

def remove_directory(dir_path):
    """
    Remove the specified directory and all its contents.
    """
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
        print(f"{dir_path} and its contents have been removed.")
    else:
        print(f"{dir_path} does not exist or is not a directory.")


def custom_title(text):
    return ' '.join([word[0].upper() + word[1:] if word else '' for word in text.split(' ')])


def toList(topdisp,sep=None):
    if sep:
        return topdisp.split(sep)
    return topdisp.split(",")


def toString(topdisp,sep=None):
    if sep:
        return sep.join(topdisp)
    return ",".join(topdisp)

        
def colorname(color_name):
    import webcolors
    try:
        rgb = webcolors.name_to_rgb(color_name)
        # Swap red and blue color values
        rgb = (rgb[2], rgb[1], rgb[0])
        return rgb
    except ValueError:
        return (0, 0, 0)  # Default to black if color name is not found
    

def arrange(actual,reverse,titlebar=True):   # arranges  items in reverse order for 5 4 3 2 1  type of video   

    actual = [i for i in actual if i!=""]  # first make sure no empty list in actual list
    first = actual[0]  # save the title
    if reverse:
        if titlebar:
            actual.pop(0)  # means if title is given in keywords : then the first item won't be reversed
            actual.reverse()
            actual.insert(0, first)
        else:
          actual.reverse()
    return actual
    
#__________________________________________________________________________________________________________________

class videoFunctions:

    def title_to_keywords(self,title):
        genai.configure(api_key=settings.GEMINI_API)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        PROMPT = settings.PROMPT + title
        # print("the prompt is: \n",PROMPT)
        response = model.generate_content(PROMPT)
        return response.text
    
    def downloadImages(self,id,imgkeywords):
        model = ai.Image()

        imgkeywords =toList(imgkeywords)
        print(imgkeywords,'92 downloadImages ---imgkeywords')
        media=settings.MEDIA_ROOT
        os.chdir(media)
        os.makedirs(f'video_{id}',exist_ok=True)
        os.makedirs(f'video_{id}/images',exist_ok=True)
        os.chdir(f"video_{id}/images")
        print(os.getcwd())
        for img_keyword in imgkeywords:
            print('Downloading Image for',img_keyword)
            image =model.generate(prompt=img_keyword)
            image.save(f"{img_keyword}.png")
            print('Download Complete...')
        os.chdir(media)
        
    #_______________________________________________________________________________________________________________________
    def bestChoice(self,id,reverse,titlebar):
                                 
        media=settings.MEDIA_ROOT
        os.chdir( os.path.join(media,f'video_{id}')) 

        all_images = os.listdir('images')
        print(all_images,'117')
        # img keywords
        img_keywords =Keyword.objects.get(id=id)     # get keyword list from database
        img_keywords = toList(img_keywords.pic_keywords)
        print(img_keywords,'before arranging')
        img_keywords= arrange(img_keywords,reverse,titlebar)
        print(img_keywords,f'when reverse was {reverse}')
        print("124--img_keywords",img_keywords)

        imgpaths = []
        for keyword in img_keywords:
            for img in all_images:
                print(img)
                if  keyword== img.split(".")[0]: # removing image extension to find exact match bcz img is same name as the keyword
                    img_path = os.path.join(media,f'video_{id}','images',img)
                    imgpaths.append(img_path)
        print(imgpaths)
        return imgpaths
    #_______________________________________________________________________________________________________________________

    def  makeVideo(self,id,fk,titlebar=False,reverse=False):


        def generate_and_add_audio(display_text):
            audio_file_paths = []

            for index, text in enumerate(display_text):
                tts = gTTS(text=text, lang='en')  # Using English language as an example
                destination = os.path.join("audio_clips", f"{index}.mp3")
                tts.save(destination)
                audio_file_paths.append(destination)

            audio_clips = [AudioFileClip(file_path) for file_path in audio_file_paths]
            return audio_clips
            



        def overlay_text(display_text,path_list):
            count=0
            for text,image_path in zip(display_text,path_list):
                if titlebar and count==0:
                    add_text_to_image(image_path, text, is_title=True, save_to=image_path)
                else:
                    add_text_to_image(image_path, text, is_title=False, save_to=image_path)
                
                count=count+1
    

        def resize_images(paths, target_size, target_format):
            resized_image_paths = []
            for path in paths:
                image = Image.open(path)
                # Convert image format if necessary  --- in this case if image not jpeg then converts it to jpeg
                if image.format.lower() != target_format:
                    new_path = os.path.splitext(path)[0] + '.' + target_format
                    image = image.convert('RGB')  # Convert RGBA to RGB
                    image.save(new_path) 
                    path = new_path

                # resizes the image to target format ---like 9:16 (360, 740 --SAMSUNG 8+ DIMENSIONS SAW IT ON DEV TOOLS)
                resized_image = image.resize(target_size)
                resized_image_path = "resized_" + os.path.basename(os.path.dirname(path)) +os.path.basename(path)
                resized_image_path = os.path.join('resized', resized_image_path)

                # Ensure image is in RGB mode
                if resized_image.mode != 'RGB':
                    resized_image = resized_image.convert('RGB') 
                resized_image.save(resized_image_path)
                resized_image_paths.append(resized_image_path)
            return resized_image_paths

        def create_video_from_photos(display_text,PER_IMAGE_DURATON, output_file, foreign_key):
            
            paths =Imgpath.objects.get(fk=foreign_key)
            photo_paths = paths.paths  
            photo_paths= toList(photo_paths,sep="|")
            resized_paths  =  resize_images(photo_paths,target_size=(360, 740),target_format='PNG')
            audio_clips = generate_and_add_audio(display_text)
            overlay_text(display_text,resized_paths)

            #creates ImageClip obj of all paths --- it converts images to short clips like img1 with duration=2 will be displayed for 2sec in the video
            image_clips = [ImageClip(path).set_duration(PER_IMAGE_DURATION) for path in resized_paths]
            image_clips_with_audio = [image.set_audio(audio) for image,audio in zip(image_clips,audio_clips)]

            video_clip = concatenate_videoclips(image_clips_with_audio, method="compose")
            os.chdir("..")
            video_clip.write_videofile(output_file, codec='libx264', fps=24)
            return True



        os.makedirs(f'temp',exist_ok=True)
        os.chdir('temp')
        time.sleep(1)
        os.makedirs('resized',exist_ok=True)
        os.makedirs('audio_clips',exist_ok=True)

        # count total keywords ---so that duration could be set for all of them ---like 2 sec for 6 keywords= [2,2,2,2,2,2]        
        total =Keyword.objects.get(id=id).pic_keywords
        display_text = Keyword.objects.get(id=id).display_keywords
        display_text = toList(display_text)
        VIDEO_TITLE = display_text[0]   #.replace(" ","_")
        display_text= arrange(display_text,reverse,titlebar)
        PER_IMAGE_DURATION = 2  # 2 SECONDS
        total= len(toList(total))
        if total>=3 and total<=10:
            video_created = create_video_from_photos(display_text,PER_IMAGE_DURATION,f'{VIDEO_TITLE}.mp4',fk)
            if video_created:
                print("Video was Created!")
                print("Removing Temporary Folders in 3 secs...")
                time.sleep(3)
                remove_directory(os.path.join(os.getcwd(),'images'))  # remove images folder
                remove_directory(os.path.join(os.getcwd(),'temp'))  # remove temp folder
                print("Temporary Folders Removed!")
                print(f"video_{id}",VIDEO_TITLE)

                return f"video_{id}",VIDEO_TITLE

    def upload_to_drive(self,title,file_path,service_account_file,parent_folder_id):

        # Authenticate and create a Google Drive API service instance
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        drive_service = build('drive', 'v3', credentials=creds)

        # File metadata with the fixed parent folder ID
        file_metadata = {
            'name': f"{title}.mp4",
            'mimeType': 'video/mp4',  # Adjust according to your file type
            'parents': [parent_folder_id]
        }

        # Media file upload
        media = MediaFileUpload(file_path, mimetype='video/mp4')

        # Upload file
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'  # Request webViewLink field for the file
        ).execute()

        # Get the webViewLink (full link) of the uploaded file
        file_link = file.get('webViewLink')

        # Return the full link to the uploaded file
        return file_link



