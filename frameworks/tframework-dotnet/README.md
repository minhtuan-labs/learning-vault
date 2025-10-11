# TFramework (.NET + Thrift)

**TFramework** is a lightweight educational framework built with **.NET** and **Apache Thrift**.  
It simplifies RPC‑based client–server communication and demonstrates core ideas in distributed systems.

It includes a minimal **framework layer** (`TFramework`) with sample client/server implementations,  
and a **P2PChatSystem** project showcasing how to use the framework to build a peer‑to‑peer chat application.

> *For self‑learning and experimentation with networking, RPC, and framework architecture in .NET.*

---

## 📦 Repository Structure

```text
tframework-dotnet/
├─ TFramework/
│  ├─ SampleServer/    # Example server (Thrift RPC)
│  └─ SampleClient/    # Example client using generated Thrift stubs
└─ P2PChatSystem/      # Simple P2P chat demo built on TFramework
```

---

## **1️⃣  The Core Framework** — `TFramework` 🧩

### SampleServer
- Implements a **Thrift‑based RPC server** in .NET
- Exposes service interfaces (IDL) for message passing and operations
- Shows server‑side request handling, connection management, and serialization

### SampleClient
- **Thrift client** connecting to `SampleServer` via generated stubs
- Sends/receives data over RPC calls
- Minimal reference for building service consumers

Together, these projects demonstrate how to build and connect Thrift‑based services on .NET.

---

## **2️⃣  Demo Application** `P2PChatSystem` 💬

A simple **peer‑to‑peer chat** demo built on top of `TFramework`.

**Features**
- Each peer can act as both **sender** and **receiver**
- Uses `SampleServer` and `SampleClient` under the hood
- Demonstrates message routing and multi‑peer communication

**Learning Focus**
- RPC message flow and data serialization
- Handling asynchronous network events in C#
- Extending Thrift for multi‑node communication

---

## 🚀 How to Build & Run

### 1. Build the entire solution
```bash
dotnet build
```

### 2. Run the server
```bash
dotnet run --project TFramework/SampleServer
```

### 3. Run one or more clients
```bash
dotnet run --project TFramework/SampleClient
```

### 4. Run the P2P chat system (optional)
```bash
dotnet run --project P2PChatSystem
```

> Tip: open multiple client terminals to simulate several chat participants.

---

## 🧠 Key Concepts Demonstrated

| Concept | Description |
|--------|-------------|
| Apache Thrift RPC | IDL‑based interface definition, multi‑language stubs |
| Client–Server Model | Separation of transport/framework vs. app logic |
| P2P Extension | Clients can also receive messages and act as nodes |
| Async I/O in .NET | Uses async/await for concurrency and responsiveness |
| Reusable Framework Design | Modular abstraction of Thrift communication |

---

## 🧱 Tech Stack
- **.NET 6+ / C# 10**  
- **Apache Thrift** for IDL and serialization  
- **Async/Await** concurrency model  
- Console UI for simple interaction/debugging

---

## 🎯 Purpose
- Build a reusable communication foundation for learning  
- Understand RPC architecture and distributed programming patterns  
- Explore framework structure and extension in .NET  
- Provide a base for future experiments (registries, MQ, streaming, etc.)

---

## 🧭 Next Steps
- Add logging/diagnostics middleware  
- Plugin‑based services & extensibility hooks  
- Bi‑directional event streaming  
- Thrift over HTTP/2 or WebSocket transport adapters

---

## 📚 References
- Apache Thrift Docs — https://thrift.apache.org/docs  
- .NET SDK Docs — https://learn.microsoft.com/en-us/dotnet/core/tools/  
- Apache Thrift (GitHub) — https://github.com/apache/thrift

---

**Author:** *Pham Minh Tuan*  
© 2025 — Built for learning, experimentation, and sharing.
