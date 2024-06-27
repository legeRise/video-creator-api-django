# YouTube Short Maker (API Version)

YouTube Short Maker is a web application built with Django and Django REST Framework (DRF) that allows users to create videos by downloading images based on specified keywords, assembling them into a video, and adding text overlays. This version offers an API endpoint for generating YouTube shorts programmatically.

## Features

- **Image Download**: Download images from the internet based on keywords.
- **Video Creation**: Assemble downloaded images into a video.
- **Text Overlay**: Add custom text overlays to the video.
- **API-Based Interface**: Generate videos via a REST API.

## Sample Video

Here's a sample video created by the application:

[![Sample Video](https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg)](https://github.com/user/repository/raw/master/done/Top%205%20Programming%20Languages.mp4)

## Usage

```markdown
### Setup and Installation:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/user/yt-short-maker-api.git
    ```
2. **Navigate to the project directory:**
    ```bash
    cd yt-short-maker-api
    ```
3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Apply the migrations:**
    ```bash
    python manage.py migrate
    ```
5. **Run the Django server:**
    ```bash
    python manage.py runserver
    ```

### Using the API:

1. **API Endpoint**: The API endpoint for creating videos is `http://127.0.0.1:8000/api/create-video/`.
2. **Request Format**:
    - Send a POST request with JSON payload containing `pic_keywords` and `display_keywords`.

3. **JSON Payload Example**:
    ```json
    {
        "pic_keywords": "programminglanguageicons,python,javascript,c,java",
        "display_keywords": "Top 5 Programming Languages,Python,JavaScript,C,Java"
    }
    ```
   - **Note**: Each "display keyword" is the overlay text for the corresponding "pic keyword." For example, if the pic keyword is `programminglanguageicons`, the display keyword might be `Top 5 Programming Languages`, meaning the image for `programminglanguageicons` will have the overlay text "Top 5 Programming Languages."

4. **Response**: The response will contain the URL to download the generated video.

### Example Request:

```bash
curl -X POST http://127.0.0.1:8000/api/create-video/ \
-H "Content-Type: application/json" \
-d '{
    "pic_keywords": "programminglanguageicons,python,javascript,c,java",
    "display_keywords": "Top 5 Programming Languages,Python,JavaScript,C,Java"
}'