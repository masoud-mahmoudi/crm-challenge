# Event-Driven CRM Platform

A small event-driven CRM built with **Django microservices**, **REST**, **GraphQL BFF**, **Kafka**, **Docker Compose**, and a **centralized PostgreSQL instance with per-service schemas**.

---

## Table of Contents

* Overview
* Goals
* Architecture Summary
* High-Level Architecture Diagram
* Core Design Decisions
* Services Overview
* Service Details
* Domain Model
* Authentication
* Authorization
* Kafka and Workflow
* Database Strategy
* Running the System
* Tradeoffs

---

## Overview

This project implements a simple CRM platform with:

* Parent / child company hierarchy
* Role-based access control
* Lead creation and management
* Secure service-to-service communication
* Kafka-based async workflows
* Outbox pattern for reliability
* Eventual consistency in UI
* GraphQL BFF for frontend

---

## Goals

1. Clear service boundaries
2. Secure request handling (JWT/JWKS-based security + local validation)
3. Reliable async processing (Kafka + retries + DLQ)
4. Clean user-facing flow

---

## Architecture Summary

### Components

* identity-service
* crm-service
* workflow-service
* api-gateway
* web-app

### Communication

* Web → API Gateway (REST + GraphQL)
* Internal → REST
* Async → Kafka

### Database

* One PostgreSQL instance
* Database: `crm_platform`
* Schemas:

  * identity
  * crm
  * workflow

---

## High-Level Architecture

```text
Web App → API Gateway → Services → Kafka → Workflow → CRM
```

---

## Core Design Decisions

### 1. GraphQL only at BFF

* Internal services use REST
* API Gateway provides GraphQL

### 2. Local JWT validation

* No dependency on identity-service per request

### 3. Outbox pattern

* Avoids dual-write problem

### 4. Centralized DB with schemas

* Simpler infra + logical isolation

---

## Services Overview

| Service          | Responsibility     |
| ---------------- | ------------------ |
| identity-service | Auth, users, roles |
| crm-service      | Leads + outbox     |
| workflow-service | Async processing   |
| api-gateway      | BFF                |
| web-app          | UI                 |

---

## Domain Model

### Identity

* User
* Company
* Membership

### CRM

* Lead

### Workflow

* ProcessedMessage
* WorkflowRun
* DeadLetterEvent

---

## Authentication

* JWT/JWKS-based security
* Issued by identity-service
* Includes:

  * user id
  * roles
  * memberships

---

## Authorization

* Enforced in services
* Rules:

  * Child users → own company only
  * Parent users → all children
  * No sibling access

---

## Kafka Workflow

Event: `crm.lead.created`

Flow:

1. Lead created
2. Outbox saved
3. Event published
4. Workflow processes
5. CRM updated

---

## Outbox Pattern

* Lead + event stored in same transaction
* Separate publisher sends to Kafka

---

## Eventual Consistency

* Lead appears immediately
* Enrichment happens later
* UI updates via polling

---

## Database Strategy

* Single Postgres
* Separate schemas per service
* Independent migrations

---

## Running the System

```bash
docker compose up --build
```

---

## Tradeoffs

* REST internally (simplicity)
* GraphQL only at BFF
* Centralized DB for simplicity
* Polling over subscriptions
