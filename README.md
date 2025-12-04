# Programming4IOTApplications

This repository contains a comprehensive IoT application ecosystem designed to be deployed using Docker. The system is composed of multiple microservices interacting via MQTT and HTTP to manage devices, analyze data, and provide user interfaces through Telegram and ThingSpeak.

## 🏗 Architecture

The project is structured into several independent microservices orchestrated by Docker Compose:

- **Catalog Service** (`/catalog`): The core component that acts as a service registry. It manages the registration and discovery of other services and devices in the system.
- **Adaptor Service** (`/adaptor`): Bridges the internal MQTT network with **ThingSpeak** to visualize data and log sensor readings.
- **Control Service** (`/control`): Contains the business logic for the system. It analyzes incoming sensor data (`Data_analysis.py`) and executes control strategies for subsystems like air conditioning (`air_control.py`) and timing schedules (`time_control.py`).
- **Device Service** (`/device`): Simulates or manages various physical IoT devices. It includes handlers for:
  - Environmental sensors (Temperature, Humidity)
  - Actuators (Air Conditioner, Lights)
  - specialized zones (Kitchen, Toilet, Door, Motion sensors)
- **Telegram Service** (`/telegram`): Provides a bot interface for users to receive notifications and send commands to the IoT system.

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dtjgp/Programming4IOTApplications.git
   cd Programming4IOTApplications
   ```

2. **Configure Environment:**
   Review the `docker-compose.yml` file. It sets up the necessary environment variables (like `CATALOG_HOST` and timezones). 

   *Note: Individual services may have configuration files in their respective `config/` directories that you might need to adjust (e.g., Telegram bot tokens, ThingSpeak API keys).*  

3. **Build and Run:**
   Use Docker Compose to build the images and start the services.
   ```bash
   docker-compose up --build
   ```

   This will start the following containers:
   - `catalog` (Port 8080)
   - `adaptor` (Port 8082)
   - `telegram` (Port 8081)
   - `control`
   - `device`

## 🔌 Communication

The services communicate primarily using **MQTT**. A shared library `MyMQTT.py` is included in most service directories to standardize the publication and subscription to topics. 

- **Services** register themselves with the **Catalog**.
- **Devices** publish telemetry data which is picked up by the **Control** and **Adaptor** services.
- **Control** logic publishes commands back to devices or triggers alerts via **Telegram**.

## 📂 Project Structure

```
Programming4IOTApplications/
├── docker-compose.yml    # Orchestration for all services
├── flows.json            # Node-RED flows configuration
├── MyMQTT.py             # Shared MQTT Helper class
├── adaptor/              # ThingSpeak connection logic
├── catalog/              # Service Registry
├── control/              # Logic/Control Loop
├── device/               # Device simulators and managers
└── telegram/             # Telegram Bot implementation
```