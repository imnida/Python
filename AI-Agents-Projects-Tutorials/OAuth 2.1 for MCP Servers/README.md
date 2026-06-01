# 🔐 OAuth 2.1 for MCP Servers

**OAuth 2.1** is the officially mandated authorization standard in the **Model Context Protocol (MCP)** specifications.  
According to the official documentation, **authorization servers must implement OAuth 2.1** with proper security measures for both confidential and public clients.

MCP provides **authorization at the transport level**, allowing clients to securely access restricted servers on behalf of resource owners. OAuth 2.1 was chosen as the framework for MCP because it offers a **modern, secure, and standardized approach** to managing authorization.

<img width="619" height="215" alt="image" src="https://github.com/user-attachments/assets/6693a3a8-7807-4837-bb21-7b47bacd9390" />

---

## ⚙️ How the Authorization Flow Works

The MCP authorization flow is designed to ensure **secure and controlled access** to protected servers.  
It happens in **three main phases**:

### 1️⃣ Discovery Phase  
When an MCP client tries to connect to a protected server:  
- The server responds with a **401 Unauthorized** status.  
- It includes a `WWW-Authenticate` header that points to its authorization server.  
- The client then uses the **metadata** from the authorization server to discover its capabilities and understand the next steps for authentication.

---

### 2️⃣ Authorization Phase  

Once the client understands how the server handles authorization, it begins the **registration and authorization** process.

- If **Dynamic Client Registration** is supported, the client can automatically register itself without manual setup.  
- During registration, the client provides:  
  - Name  
  - Type  
  - Redirect URLs  
  - Desired scopes  

The authorization server then issues:  
- **Client credentials** — typically `client_id` and `client_secret`.

#### 🔄 Supported OAuth Flows:
- **🔑 Authorization Code Flow** – Used when acting on behalf of a **human user**.  
- **🤖 Client Credentials Flow** – Used for secure **machine-to-machine** communication.

In the **Authorization Code Flow**, the user grants consent. Once approved, the server issues an **access token** with the correct scopes.

---

### 3️⃣ Access Phase  
With the **access token** in hand:  
- The client includes the token with its requests.  
- The MCP server validates the token and scopes.  
- Only then does the server process the request and return the response.  

Every interaction is **logged for auditing and compliance**, ensuring security and traceability.

---
<img width="723" height="692" alt="image" src="https://github.com/user-attachments/assets/974e44e0-38b6-4c21-8e37-ef4b28891db8" />

**Source:** [MCP Authorization Spec](https://modelcontextprotocol.io/specification/draft/basic/authorization)

---

## 🔒 Key Security Enhancements in MCP OAuth 2.1  

The MCP authorization specification includes **several important security upgrades**:

- **🔑 Mandatory PKCE**  
  All MCP clients must use **PKCE (Proof Key for Code Exchange)**, adding an extra security layer by preventing code interception attacks.


- **📍 Strict Redirect URI Validation**  
  Clients must **pre-register their exact redirect URIs**. During authorization, the server checks for an **exact match**, reducing the risk of token redirection attacks.


- **⏳ Short-Lived Tokens**  
  Tokens are issued with **short lifespans** to minimize risk in case they are leaked or compromised.

- **🛠️ Granular Scope Model**  
  MCP OAuth 2.1 uses **fine-grained scopes** to control permissions:  
  - `mcp:tools:weather` – Access to weather tools only  
  - `mcp:resources:customer-data:read` – Read-only access to customer data  
  - `mcp:exec:workflows:*` – Permission to run any workflow  

- **⚡ Dynamic Client Registration**  
  Enables **automatic client registration**, letting new clients obtain credentials like `client_id` without manual setup.

---

## 🚀 How to Implement OAuth 2.1 for MCP Servers  

You can refer to the codes in this section to create a **simple finance sentiment analysis server** and implement **authorization using Scalekit**, a platform that **simplifies the entire OAuth 2.1 process**.
