FROM python:3.12

## Pip dependencies
# Upgrade pip
RUN pip install --upgrade pip
# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && 
    rm /tmp/requirements.txt
