# TFramework (.NET + Thrift)

**TFramework** is a lightweight and educational framework built with **.NET** and **Apache Thrift**,  
designed to simplify RPC-based client–server communication and demonstrate core principles of distributed system design.

It includes a minimal **framework layer** (`TFramework`) with sample client/server implementations,  
and a **P2PChatSystem** project showcasing how to use the framework to build a peer-to-peer chat application.

> 🧠 *This project is intended for self-learning and experimentation with network programming, RPC, and framework architecture in .NET.*

---

## 📦 Repository Structure

```
tframework-dotnet/
├── TFramework/
│   ├── SampleServer/     ← Example server implementation (Thrift RPC)
│   └── SampleClient/     ← Example client communicating via Thrift stubs
└── P2PChatSystem/        ← A sample project using the framework for a simple P2P chat
```

---

## 🧩 1. The Core Framework — `TFramework`

The **TFramework** directory provides the reusable communication foundation.

### 🔹 SampleServer
- Implements a **Thrift-based RPC server** in .NET.  
- Exposes defined service interfaces (IDL) for message passing and basic operations.  
- Demonstrates server-side request handling, connection management, and message serialization.

### 🔹 SampleClient
- A lightweight **Thrift client** that connects to the SampleServer using generated stubs.  
- Sends and receives data through RPC calls.  
- Serves as a minimal reference for building distributed service consumers.

Together, these two projects demonstrate how to build and connect Thrift-based services on .NET.

---

## 💬 2. P2PChatSystem — Demo Application

**P2PChatSystem** is a simple peer-to-peer chat demo built on top of `TFramework`.

### ⚙️ Features
- Each peer can act as both **sender** and **receiver**.  
- Uses the `SampleServer` and `SampleClient` components internally.  
- Demonstrates message routing and connection management between multiple peers.  
- Built to help understand **bidirectional communication** over RPC and serialization with Thrift.

### 🧠 Learning focus
- RPC message flow and data serialization  
- Handling asynchronous network events in C#  
- Extending Thrift for multi-node communication

---

## 🚀 How to Build & Run

### 1️⃣ Build the entire solution
```bash
dotnet build
```

### 2️⃣ Start the server
```bash
dotnet run --project TFramework/SampleServer
```

### 3️⃣ Start one or more clients
```bash
dotnet run --project TFramework/SampleClient
```

### 4️⃣ Run the P2P chat system
```bash
dotnet run --project P2PChatSystem
```

> 💡 Tip: open multiple client terminals to simulate multiple chat participants.

---

## 🧠 Key Concepts Demonstrated

| Concept | Description |
|----------|-------------|
| **Apache Thrift RPC** | Defines communication interfaces using IDL, generating stubs for multiple languages |
| **Client–Server Model** | Separation between communication logic and application logic |
| **P2P Extension** | Demonstrates how clients can also receive messages and act as nodes |
| **Asynchronous I/O in .NET** | Uses async/await for concurrency and responsiveness |
| **Reusable Framework Design** | Abstracts Thrift communication into modular, reusable components |

---

## 🧱 Technical Stack

- **.NET 6+ / C# 10**  
- **Apache Thrift** for IDL and message serialization  
- **Async/Await** for concurrent operations  
- **Console-based UI** for simple interaction and debugging  

---

## 🧩 Project Purpose

The goal of **TFramework** is to:
- Build a minimal but reusable communication foundation for learning purposes  
- Understand RPC-based architecture and distributed programming concepts  
- Explore how frameworks are structured and extended in .NET  
- Provide a base for further experiments (e.g., service registry, message queue, or REST/RPC hybrid patterns)

---

## 🧭 Next Steps

Future improvements may include:
- Adding **logging and diagnostics** middleware  
- Introducing **plugin-based services**  
- Supporting **bi-directional event streaming**  
- Adding **Thrift over HTTP/2 or WebSocket** transport adapters  

---

## 📚 References

- [Apache Thrift Documentation](https://thrift.apache.org/docs)  
- [.NET SDK Documentation](https://learn.microsoft.com/en-us/dotnet/core/tools/)  
- [Thrift GitHub Repository](https://github.com/apache/thrift)

---

**Author:** *Pham Minh Tuan*  
© 2025 — Built for learning, experimentation, and sharing.
