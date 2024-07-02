# ytshortmaker-api

Ytshortmaker-api is a web Api built with Django and Django REST Framework (DRF) that allows users to create youtube shorts with just a video title.

This project is actually the web version of my previous ytshortmaker-tkinter-app but with much improvements. Also, it is hosted on render.com(the free plan, ofcourse) so you can check it out too( but again, no frontend it is just an api, for now)

**Live URL:** [https://videoapidjango.onrender.com/](https://videoapidjango.onrender.com/)

So here is what it does

You make a POST request at this endpoint `/videoapi/createvideo/` with the video title and wait for it; It will return a google drive video-link to generated video along with a msg of "Video created".

Since, it is already hosted, you can try this sample request right about now,


## Example Using Curl

```sh

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"title": "Top 5 Mountains in the World"}' \
  http://videoapidjango.onrender.com/ytshortmakerapi/createvideo/
```

## Example Using Python
```python
import requests

url = 'http://videoapidjango.onrender.com/ytshortmakerapi/createvideo/'
payload = {'title': 'Top 5 Mountains in the World'}
response = requests.post(url, json=payload)

print(response.json())  # Replace with your handling of response if needed
```


**Response Example**

```json
{
    "message": "Video Created!",
    "link": "https://drive.google.com/file/d/17q4ndOBx98M-pTpe9O0o-faneRxA9hkx/view?usp=drivesdk"
}
```

### How it does that?

It is a pretty simple project, what it actually does is:

1. Takes a video title from User. **Note:** it assumes the titles to be in "top 5" or 3 etc like format i.e ***Top 5 Mountains***, ***Top 5 Marvel Superheroes*** etc anything for which it can extract keywords.
   
2. Using Gemini API generates keywords based on that ***title***.

3. Downloads Images against those keywords.

4. Creates a video from it along with the text overlay.

5. Once created, it uploads the video to Google Drive and returns the link to that video.



### What it's capable of?

This project started as a hobby to tackle a specific use case, but it quickly became a valuable learning experience for practicing Django, Django REST Framework, Docker, containerization, automation, and deployment (AWS and Render).

It is designed to generate specific kinds of videos such as:
1. Top 5 Mountains in the World
2. Top 3 Horror places in China
3. Top 7 wonders of the world

and so on. In the backend, it uses Gemini to extract facts (like names of five mountains) and an image-downloader library to fetch images based on these keywords.

So, to answer ***What it's capable of*** now that you know what actually takes place behind the scenes: well, it can create such videos (the specific kind). However, results may not always meet expectations as Gemini's responses can sometimes be unexpected, and the downloaded images may not accurately represent the keywords every time (because, after all, it is just searching, just like on Google).

If a video doesn't turn out as expected, trying again with the same title might produce the desired outcome. Until I come up with a better approach to overcome this.




## Setting Up Locally

1. ### Clone the repository and navigate into it
   ```sh
   git clone https://github.com/legeRise/video-creator-api-django.git
   ```
   ```sh
   cd video-creator-api-django
   ```

2. ### Creating a Virtual Environment

    ```sh
   python -m venv venv
    ```

3. ## Activate the virtual environment

   - **For Windows:**
     ```sh
     venv\Scripts\activate
     ```

   - **For Linux:**
     ```sh
     source venv/bin/activate
     ```


4. install dependencies
   pip install -r requirements.txt

5. create .env using the .env.sample.txt sample i provided
   mention your gemini api key
   your google drive folder id where you want it to upload the filees
   and your service_account_file.json  which is the json file you get when you create a service account on google cloud console


6 Once you have all this setup run migrations
python manage.py makemigrations
python manage.py migrate

7. Run the project
   python manage.py runserver

the project will start running on localhost:8000 (127.0.0.1:8000)  
go to '/videoapi/createvideo/' endpoint and   make a post rquest using DRF interface you see 
{"title": "Top 5 Mountains in the World"}  and hit the post button

you will see the response after sometime meanwhile you can see the process when it connects to gemini gets keywords, download images and eventually generates video with a link to it.
And cheers you have the project in your hands now 

REMINDER: the project it live anyway so if you don't want to get in the hassle of setting it up and just want to see the results just use one of the ways(python or curl) to get quick results.

here is a link to sample video if don't even want this 
https://drive.google.com/file/d/17q4ndOBx98M-pTpe9O0o-faneRxA9hkx/view?usp=drive_link






