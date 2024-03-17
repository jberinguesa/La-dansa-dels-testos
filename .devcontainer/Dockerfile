FROM python:3.12

## Pip dependencies
# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
RUN rm requirements.txt

# Install opencv dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Per accedir a la pantalla
RUN apt-get update && apt-get install -y '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev
# Set the DISPLAY environment variable
ENV DISPLAY=:99
# Start the X server
CMD Xvfb :99 -screen 0 1024x768x24 &