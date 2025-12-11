# Crypto Streaming Pipeline (Real-Time Kafka → Kubernetes → Snowflake)

This project implements a **cloud-native, real-time data streaming pipeline** that ingests market events from the Massive API, publishes them into Kafka, processes them with a consumer service, and loads the results into Snowflake for analytics.

---

## Overview

The system consists of three major components:

### **1. Producer Service (Massive → Kafka)**
A Python service that:
- Calls the Massive REST API for real-time market data (e.g., dividends)
- Packages each event as a Kafka message
- Publishes messages to the `market_events` topic

Runs both locally (via Docker Compose) and inside Kubernetes.

---

### **2. Kafka Broker**
A single-node Kafka broker used for development and local testing.  
It acts as the streaming backbone for the pipeline by receiving messages from the producer and making them available to consumers.

(For cloud deployment, Kafka will be replaced by AWS MSK.)

---

### **3. Consumer Service (Kafka → Snowflake)**
A Python consumer that:
- Subscribes to the `market_events` Kafka topic
- Batches incoming events
- Writes data into Snowflake (`MARKET_EVENTS` table)

Enables near real-time analytics in Snowflake.

---

## Cloud Deployment (AWS + Kubernetes)

Both the producer and consumer services are containerized with Docker and pushed to **Amazon ECR**.

An **Amazon EKS (Kubernetes)** cluster runs the workloads:
- Producer deployment
- Consumer deployment  
- ConfigMaps and Secrets for credentials  
- Cluster networking managed by EKS add-ons  

This provides scalable, production-style infrastructure.

---

## Current Architecture

**Pipeline Flow:**  
**Massive API → Kafka Producer → Kafka Broker → Kafka Consumer → Snowflake**

**Technologies Used:**
- Python  
- Docker & Docker Compose  
- Apache Kafka  
- Amazon ECR  
- Amazon EKS (Kubernetes)  
- Snowflake  
- AWS IAM / AWS CLI / eksctl  

---

## Status

The pipeline is currently operational end-to-end:

- ✔ Producer successfully streams real market events  
- ✔ Kafka receives and buffers messages  
- ✔ Consumer writes to Snowflake in batches  
- ✔ Docker images published to ECR  
- ✔ EKS cluster deployed and ready for cloud workloads  

Next planned steps:
- Deploy managed Kafka via AWS MSK  
- Configure autoscaling for producer/consumer pods  
- Add monitoring, logging, and alerting (CloudWatch + Prometheus)  

---

