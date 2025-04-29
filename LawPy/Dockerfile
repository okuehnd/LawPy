FROM python:3.9

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Django and MongoDB connector
RUN pip install --no-cache-dir django pymongo djongo 

# Copy project files
COPY . /app/

# Expose port for Django
EXPOSE 8000

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 