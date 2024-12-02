# Application for Adding Text Descriptions to Images


The purpose of the program is to add a text description under the image

[Problem definition](Problem_definitions.pdf)

---


Endpoint Specification
After launching the application, endpoint specifications can be accessed at http://127.0.0.1:8000/docs

Example Command to Upload a File and Description

```sh
curl -X POST "http://localhost:8000/api/images" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@~/Documents/your_file.jpeg" \
-F "description=However, it should not be forgotten that the new model of organizational activity represents a qualitatively new stage of impact forms. Only interactive prototypes add fractional disagreements."
```

Retrieve a List of Stored Objects (execute the command or open the URL in a browser)

```sh
curl http://127.0.0.1:8000/api/images
```

Example Input Image

<img src="input_example.png" alt="Example Input Image" width="300" />

Example Output Image


<img src="output_example.jpeg" alt="Example Output Image" width="600" />

## Launching the Application

This document describes the steps for installing and launching the service using Docker Compose.

### Step 1: Install Docker and Docker Compose

To get started, install Docker and Docker Compose on your system.

#### Installing Docker and Docker Compose

```
1. Go to [Docker's download page](https://docs.docker.com/get-docker/) and follow the instructions for your operating system.

2. Visit the [Docker Compose download page](https://docs.docker.com/compose/install/) and follow the instructions for your operating system.
```

### Step 2: Configuring the Application

To configure certain application parameters, a `config.toml` file is available in the repository's root. 
In this file, you can define database connection parameters, Redis service configuration, and the default text to be inserted under the image. 

This file is copied to each of the microservices at runtime.

Note: To use a custom font, place a `.ttf` font file in the `image_processing_service` directory and specify the font file name (without the extension) in the `font` parameter.

### Step 3: Launch the Application

Run the following command from the repository's root directory:

```sh
docker-compose up
```

To run the application in the background, add the `-d` parameter.

### Step 4: Stop the Application

Run the following command:

```sh
docker-compose down
```

---

## Assumptions for Task Execution

#### 1. Storing Processed Images in Binary Format in the Database

Although this is an inefficient use of SSD resources, this approach was chosen for simplicity and as an MVP.

#### 2. Absence of Tests
Tests were not implemented due to time constraints.

#### 3. Formal Logging and Exception Handling

Logging requires improvements. Custom exceptions need to be developed for the image processing and storage services.

#### 4. Service Configuration

Services are configured only at startup, using a single file and code for the entire application. Database configuration is handled within the `docker-compose` file.

#### 5. Lack of Asynchronous Processing
Asynchronous approaches were not used in the image processing and storage service implementation.
