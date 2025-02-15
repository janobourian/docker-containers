# Getting Started

Welcome to the Docker Containers project! This guide will help you get started with setting up and running the project.

## Project Structure

Here's an overview of the project structure:

```
/Users/frgonzal/Documents/vit/docker-containers/
├── docker-compose.yml
├── Dockerfile
├── docs/
│   └── getting-started.md
├── src/
│   ├── app/
│   └── config/
└── README.md
```

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker
- Docker Compose

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/docker-containers.git
   cd docker-containers
   ```

2. **Build the Docker image:**
   ```sh
   docker-compose build
   ```

3. **Run the Docker containers:**
   ```sh
   docker-compose up
   ```

## Accessing the Application

Once the containers are up and running, you can access the application at `http://localhost:your_port`.

## Documentation

For more detailed information, refer to the [documentation](./docs).

## Troubleshooting

If you encounter any issues, check the logs using:
```sh
docker-compose logs
```

Feel free to reach out for support if you need further assistance.

Happy coding!