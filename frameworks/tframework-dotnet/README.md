# TFramework (.NET + Thrift)

**TFramework** is a lightweight .NET framework built on top of **Apache Thrift**, designed to simplify the development of distributed applications and client-server communication.  

It provides an abstraction layer for defining RPC services and message protocols, along with ready-to-use sample implementations for both the **server** and **client** sides.

---

## 📂 Directory Structure
tframework-dotnet/
├── TFramework/
│   ├── SampleServer/   ← Example server implementation (Thrift-based RPC)
│   └── SampleClient/   ← Example client implementation
└── P2PChatSystem/      ← A sample project demonstrating P2P chat using TFramework

---

## ⚙️ Overview

### **1️⃣ TFramework**
This is the core part of the repository.  
It includes two sample projects:

- **SampleServer** — a minimal RPC server exposing Thrift-based interfaces for data exchange and message handling.  
- **SampleClient** — a lightweight Thrift client that communicates with the server through generated stubs and contracts.

Together, they demonstrate how to build a service and consume it over Thrift efficiently.

---

### **2️⃣ P2PChatSystem**
A simple **peer-to-peer chat system** built using the `SampleServer` and `SampleClient` as its communication backbone.

- Each peer can act as both a message sender and receiver.  
- The system illustrates how Thrift can be extended for bi-directional (P2P-like) communication using standard RPC patterns.  
- Intended as a **learning demo** for network communication, serialization, and Thrift integration in C#.

---

## 🚀 How to Run

1. **Build the solution**
   ```bash
   dotnet build




