# Dockerfile
# 1. Base image
FROM python:3.11.12-slim

# 2. System packages for Gradio, ffmpeg, Git-LFS, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git-lfs \
      ffmpeg \
      libsm6 \
      libxext6 \
      cmake \
      rsync \
      libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working dir
WORKDIR /home/user/app

# 4. Copy & install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy your app code
COPY . .

# 6. Default launch command
CMD ["python", "app.py"]
