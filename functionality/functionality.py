import os
import shutil
import time
import random
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips
from webcreatorApp.models import Keyword
from webcreatorApp.models import Imgpath
from .function_wrap_center import add_text_to_image
from django.conf import settings
from icrawler.builtin import GoogleImageCrawler  # before using it --must install 1.lxml 2. bs4 3. requests  4. six 6. pillow
#from icrawler.builtin import BingImageCrawler
from django.conf import settings

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
        imgkeywords =toList(imgkeywords)
        print(imgkeywords,'92 downloadImages ---imgkeywords')
        media=settings.MEDIA_ROOT
        os.chdir(media)
        os.makedirs(f'video_{id}',exist_ok=True)
        os.makedirs(f'video_{id}/images',exist_ok=True)   
        for img_keyword in imgkeywords:
            print(img_keyword,'for this img_keyword')
            os.chdir(os.path.join(media,f'video_{id}','images'))
            print('Starting Download...')
            print('keyword to be download',img_keyword)
            
            google_crawler =GoogleImageCrawler( feeder_threads=1,parser_threads=3,downloader_threads=4,storage={'root_dir': img_keyword})
            google_crawler.crawl(keyword=img_keyword, filters=dict(size='large'), max_num=4, file_idx_offset=0)


            print('Download Complete...')
            os.chdir(media)
        
    #_______________________________________________________________________________________________________________________
    def bestChoice(self,id,reverse,titlebar):
                                 
        media=settings.MEDIA_ROOT
        os.chdir( os.path.join(media,f'video_{id}'))

        allimgfolders = os.listdir('images')
        names =Keyword.objects.get(id=id)     # get keyword list from database
        names = toList(names.pic_keywords)
        print(names,'before arranging')
        names= arrange(names,reverse,titlebar)
        print(names,f'when reverse was {reverse}')
        print("123--names",names)
        print("124---all img folders",allimgfolders)

        imgpaths = []
        for name in names:
            for img in allimgfolders:
                if name == img:
                    new_path = os.path.join(media,f'video_{id}','images',img)
                    all_new = os.listdir(new_path)
                    random_pic = os.path.join(new_path, random.choice(all_new))
                    imgpaths.append(random_pic)
        return imgpaths
    #_______________________________________________________________________________________________________________________

    def  makeVideo(self,id,fk,duration=2,titlebar=False,reverse=False):

        def overlay_text(text_list,path_list):
            count=0
            for text,image_path in zip(text_list,path_list):
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

        def create_video_from_photos(display_text,duration_per_photo, output_file, foreign_key):
            
            paths =Imgpath.objects.get(fk=foreign_key)
            photo_paths = paths.paths  
            photo_paths= toList(photo_paths,sep="|")
            resized_paths  =  resize_images(photo_paths,target_size=(360, 740),target_format='PNG')
            overlay_text(display_text,resized_paths)

            #creates ImageClip obj of all paths --- it converts images to short clips like img1 with duration=2 will be displayed for 2sec in the video
            image_clips = [ImageClip(path, duration=duration) for path, duration in zip(resized_paths, duration_per_photo)]
            video_clip = concatenate_videoclips(image_clips, method="compose")
            os.chdir("..")
            video_clip.write_videofile(output_file, codec='libx264', fps=30)
            return True

        
        # video should be in 9:16
        # the function first comes here -------
        target_height = 900
        target_width = int(target_height * (9/16))
        target = (target_width, target_height)

        os.makedirs(f'temp',exist_ok=True)
        os.chdir('temp')
        time.sleep(1)
        os.makedirs('resized',exist_ok=True)


        # count total keywords ---so that duration could be set for all of them ---like 2 sec for 6 keywords= [2,2,2,2,2,2]        
        total =Keyword.objects.get(id=id).pic_keywords
        display_text = Keyword.objects.get(id=id).display_keywords
        display_text = toList(display_text)
        VIDEO_TITLE = display_text[0]
        display_text= arrange(display_text,reverse,titlebar)
        total= len(toList(total))
        if total>=3 and total<=10:
            durations=[duration]*total
            video_created = create_video_from_photos(display_text,durations,f'{VIDEO_TITLE}.mp4',fk)
            if video_created:
                print("Video was Created!")
                print("Removing Temporary Folders in 3 secs...")
                time.sleep(3)
                remove_directory(os.path.join(os.getcwd(),'images'))  # remove images folder
                remove_directory(os.path.join(os.getcwd(),'temp'))  # remove temp folder
                print("Temporary Folders Removed!")
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
            'name': title,
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



