FROM python:3.12

## Pip dependencies
# Upgrade pip
RUN pip install --upgrade pip
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
RUN rm requirements.txt
