import os
import time
import random
import cv2
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips
from webcreatorApp.models import Keyword
from webcreatorApp.models import Imgpath
from django.conf import settings
from icrawler.builtin import GoogleImageCrawler  # before using it --must install 1.lxml 2. bs4 3. requests  4. six 6. pillow

#_________________________________________________________________________________________________________
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
    
    def downloadImages(self,id,imgkeywords):
        imgkeywords =toList(imgkeywords)
        media=settings.MEDIA_ROOT
        os.chdir(media)
        os.makedirs(f'user_{id}',exist_ok=True)
        os.makedirs(f'user_{id}/images',exist_ok=True)   
        for img_keyword in imgkeywords:
            os.chdir(os.path.join(media,f'user_{id}','images'))
            print('Starting Download...')
            print('keyword to be download',img_keyword)
            google_crawler =GoogleImageCrawler( feeder_threads=1,parser_threads=3,downloader_threads=4,storage={'root_dir': img_keyword})
            google_crawler.crawl(keyword=img_keyword, filters=dict(size='large'), max_num=4, file_idx_offset=0)
            print('Download Complete...')
            os.chdir(media)

    #_______________________________________________________________________________________________________________________
    def bestChoice(self,id,reverse,titlebar):

        media=settings.MEDIA_ROOT
        os.chdir( os.path.join(media,f'user_{id}'))

        allimgfolders = os.listdir('images')
        names =Keyword.objects.get(id=id)     # get keyword list from database
        names = toList(names.pic_keywords)

        print(names,'before arranging')
        names= arrange(names,reverse,titlebar)
        print(names,f'when reverse was {reverse}')

        imgpaths = []
        for name in names:
            for img in allimgfolders:
                if name == img:
                    new_path = os.path.join(media,f'user_{id}','images',img)
                    all_new = os.listdir(new_path)
                    random_pic = os.path.join(new_path, random.choice(all_new))
                    imgpaths.append(random_pic)
        return imgpaths
    #_______________________________________________________________________________________________________________________

    def  makeVideo(self,id,fk,duration=2):

        def resize_images(path, target_size, target_format):
            image = Image.open(path)
            # Convert image format if necessary  --- in this case if image not jpeg then converts it to jpeg
            if image.format.lower() != target_format:
                new_path = os.path.splitext(path)[0] + '.' + target_format
                image = image.convert('RGB')  # Convert RGBA to RGB
                image.save(new_path)
                path = new_path

            # resizes the image to target format ---like 9:16  
            resized_image = image.resize(target_size)
            resized_image_path = "resized_" + os.path.basename(path)
            resized_image_path = os.path.join('resized', resized_image_path)

            # Ensure image is in RGB mode
            if resized_image.mode != 'RGB':
                resized_image = resized_image.convert('RGB')

            resized_image.save(resized_image_path)
            return resized_image_path

        def create_video_from_photos(duration_per_photo, output_file, foreign_key):
            
            paths =Imgpath.objects.get(fk=foreign_key)
            photo_paths = paths.paths  
            photo_paths= toList(photo_paths,sep="|")
            resized_paths = map(resize_images,photo_paths,[target]*len(photo_paths),['jpeg']*len(photo_paths))
            
            # creates ImageClip obj of all paths --- it converts images to short clips like img1 with duration=2 will be displayed for 2sec in the video
            image_clips = [ImageClip(path, duration=duration) for path, duration in zip(resized_paths, duration_per_photo)]
            video_clip = concatenate_videoclips(image_clips, method="compose")
            video_clip.write_videofile(output_file, codec='libx264', fps=24)

        
        # video should be in 9:16
        target_height = 900
        target_width = int(target_height * (9/16))
        target = (target_width, target_height)


        os.makedirs(f'temp',exist_ok=True)
        os.chdir('temp')
        time.sleep(1)
        os.makedirs('resized',exist_ok=True)

        # count total keywords ---so that duration could be set for all of them ---like 2 sec for 6 keywords= [2,2,2,2,2,2]        
        total =Keyword.objects.get(id=id).pic_keywords
        total= len(toList(total))
        if total>=3 and total<=10:
            durations=[duration]*total
            create_video_from_photos(durations, 'output.mp4',fk)
        
    #_______________________________________________________________________________________________________________________

    def titleBar(self,id,bg_color="yellow",text_color="black",fontSize=2,thickness=3):
        #Extract title text

        title = Keyword.objects.get(id=id).display_keywords
        title = toList(title)[0]

        # Load the video
        video_path = "output.mp4" 
        cap = cv2.VideoCapture(video_path)

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the output video codec and create VideoWriter object
        output_path = "title_added.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Define title bar properties
        title_bar_height = 80
        title_text = title
        title_font = cv2.FONT_HERSHEY_SIMPLEX
        title_font_scale = fontSize
        title_text_color = colorname(text_color)
        title_bg_color = colorname(bg_color)
        title_thickness = thickness
        title_offset_top = 300
        title_offset_sides = 20
        title_text_max_width = width - 2 * title_offset_sides

        # Set the duration for which the title bar will be displayed (in seconds)
        title_duration = 1.0

        # Variables to keep track of elapsed time and title bar visibility
        start_time = cv2.getTickCount() / cv2.getTickFrequency()
        current_time = 0
        display_title_bar = True

        # Loop through each frame of the video
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Add title bar if it should be displayed
            if display_title_bar:
                frame[title_offset_top:(title_offset_top + title_bar_height),
                title_offset_sides:(width - title_offset_sides)] = title_bg_color

                # Fit title text within the title bar
                text_width, text_height = cv2.getTextSize(title_text, title_font, title_font_scale, title_thickness)[0]
                while text_width > title_text_max_width:
                    title_font_scale -= 0.1
                    text_width, text_height = cv2.getTextSize(title_text, title_font, title_font_scale, title_thickness)[0]

                # Add title text
                text_x = int((width - text_width) / 2)
                text_y = title_offset_top + int(title_bar_height / 2) + int(text_height / 2)
                cv2.putText(frame, title_text, (text_x, text_y), title_font, title_font_scale, title_text_color,
                            title_thickness, cv2.LINE_AA)

            # Calculate elapsed time
            current_time = (cv2.getTickCount() / cv2.getTickFrequency()) - start_time

            # Check if the duration has been exceeded
            if current_time >= title_duration:
                display_title_bar = False

            # Write the modified frame to the output video
            out.write(frame)


            # Press 'q' to stop the video processing
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the resources
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    #_______________________________________________________________________________________________________________________

    def textOnVideo(self,id,titlebar,reverse,duration):
    
        def add_text_with_shadow(frame, text, position, font, font_scale, thickness, shadow_color, shadow_offset):
            # Add shadow text
            shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            cv2.putText(frame, text, shadow_position, font, font_scale, shadow_color, thickness, cv2.LINE_AA)

        def add_timestamp(frame,text, **text_properties):

            # Access individual properties of text_properties dictionary
            font = text_properties.get("font", cv2.FONT_HERSHEY_SIMPLEX)
            font_scale = text_properties.get("font_scale", 1.5)
            color = text_properties.get("color", (0,255,255))
            thickness = text_properties.get("thickness", 2)
            offset = text_properties.get("offset", (0, 0))
            line_type = text_properties.get("line_type", cv2.LINE_AA)

            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            wrapped_lines = []
            words = text.split(' ')
            current_line = ''
            for word in words:
                (line_width, _), _ = cv2.getTextSize(current_line + ' ' + word, font, font_scale, thickness)
                if line_width <= frame_width:
                    current_line += ' ' + word
                else:
                    wrapped_lines.append(current_line.strip())
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line.strip())
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness) #so basically getTextSize() function takes  "Text(content), "fontScale(size of text)","font( type of font)  and thickness  ) and based on these inputs returns text height and width ...means how would it look like when placed on screen and also it returns another thing baseline offset that we don't need so we ignore it by storing it in "_" that is a convention
            line_spacing = int(text_height * 1.5)  # Adjust the line spacing as needed   2 would inceasing line spacing 1 would decrese it is obvious



            y = int((frame_height + text_height) / 2)
            y= y+ offset[1]
            y = y - (len(wrapped_lines) * line_spacing)

            for textLine in wrapped_lines:
                (textline_width, _), _ = cv2.getTextSize(textLine, font, font_scale, thickness)
                x = int((frame_width - textline_width) / 2) + offset[0]

                """Draws shadow text   """
                add_text_with_shadow(frame, textLine, (x, y), font, font_scale,thickness,shadow_color,shadow_offset)
                """Draws Main text   """
                cv2.putText(frame, textLine, (x, y), font, font_scale, color, thickness, line_type) # and finally this function draws text on video by taking follwing arguments: 1. frame(screen/full_image)  2. textline(put this func in loop if more than one lines)3. (x,y) coordinates that we calculated above.  and the other text properties like font, thickness etc and finally draws the text
                y += line_spacing

        def put_text_on_video(video_path, output_path, text_properties):

            # Open the video file
            video = cv2.VideoCapture(video_path)

            fps = video.get(cv2.CAP_PROP_FPS)
            frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Create a VideoWriter object to save the output video
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # * is used in unpacking iterables so, *'avc1' is easy way to pass. the other way is separately passing 4 characters like 'm','p','4','v'
            output_video = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height)) # it makes an empty video continer with the specified name and path for the video
            # ...and the following code keeps modifying each frame and storing in it
            
            display_text =Keyword.objects.get(id=id).display_keywords
            display_text = toList(display_text) 
            actual =arrange(display_text,reverse,titlebar=titlebar)   # arranges  items in reverse order for 5 4 3 2 1  type of video


            timestamps = []
            time =0 if not titlebar else duration

            if titlebar:
                for i in range(1,len(actual)):
                    stamp= {}
                    stamp["text"] = f"{len(actual)-i}. {actual[i]}"
                    stamp["start_time"] = time
                    stamp["end_time"] = stamp["start_time"] +duration
                    time= stamp["end_time"]
                    timestamps.append(stamp)
            else:
                for i in range(len(actual)):
                    stamp= {}
                    stamp["text"] = f"{len(actual)-i}. {actual[i]}"
                    stamp["start_time"] = time
                    stamp["end_time"] = stamp["start_time"] +duration
                    time= stamp["end_time"]
                    timestamps.append(stamp)


            # Read and process each frame of the video
            frame_count = 0
            current_timestamp = None

            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break


                if current_timestamp is None or frame_count >= current_timestamp["end_frame"]:
                    if timestamps:
                        current_timestamp = timestamps.pop(0)
                        current_timestamp["start_frame"] = int(current_timestamp["start_time"] * fps)
                        current_timestamp["end_frame"] = int(current_timestamp["end_time"] * fps)


                if current_timestamp and frame_count >= current_timestamp["start_frame"]:
                    add_timestamp(frame, current_timestamp["text"], **text_properties)

                output_video.write(frame)  # Write the frame with added text to the output video

                frame_count += 1

            video.release()  # leaves the input video
            output_video.release() # releases/or finalizes the output video
            cv2.destroyAllWindows()  # destroy all windows created by opencv

        # step 1: Specify the input video path,output video path and Define the text properties
        media=settings.MEDIA_ROOT
        user= os.path.join(media,f'user_{id}')
        if titlebar:
            vf = videoFunctions()
            vf.titleBar(id=id)  # after calling this function title is added and the  video is saved as 'title_added.mp4'
            input_video_path = "title_added.mp4"
        else:
            input_video_path = "output.mp4"


        # output videopath
        title = Keyword.objects.get(id=id).display_keywords
        titleName = toList(title)[0].replace(" ","")
        output_video_path = os.path.join(user, f'{titleName}.mp4')


        # text properties
        text_properties = {
            "font": cv2.FONT_HERSHEY_SIMPLEX,  # cv2.FONT_HERSHEY_TRIPLEX
            "font_scale": 1.7,
            "color": colorname("yellow"),  # Red color (BGR)
            "thickness": 6,
            "offset": (0, 60),  # Move text 10 pixels to the right and 10 pixels up
            "line_type": cv2.LINE_AA
        }
        shadow_color = colorname("black")
        shadow_offset = (7, 7)

        # step 2: Call the function which takes input video path, output video path and text properties as input
        put_text_on_video(input_video_path, output_video_path, text_properties)

        return f"user_{id}",titleName
        
