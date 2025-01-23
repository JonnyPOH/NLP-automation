# Use the official AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Copy function code and dependencies into the container
COPY app.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

# Set the CMD to your Lambda handler
CMD ["app.lambda_handler"]
