# Stage 1: Cài đặt dependencies
FROM ubuntu:latest AS dependencies

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openjdk-11-jdk

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

WORKDIR /app/BackEnd
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Sao chép mã nguồn
FROM dependencies AS source

WORKDIR /app/BackEnd
COPY . .

# Stage 3: Build image cuối cùng
FROM dependencies

WORKDIR /app
COPY --from=source /app .

EXPOSE 8000

CMD ["uvicorn", "BackEnd.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
