# 🔐 Simple TLS MQTT Broker

This is a university project implementing a **simple MQTT-like broker** using a certificates, digital signatures, and both asymmetric and symmetric encryption to simulate TLS. The goal is to enable end-to-end encrypted publish/subscribe messaging between clients.

## 📚 Overview

This project implements a secure broker that:

- Authenticates clients using **X.509 certificates**.
- Uses **digital signatures** to prove possession of private keys.
- Exchanges **symmetric session keys** securely using **asymmetric encryption**.
- Supports **encrypted topic management** and **end-to-end encrypted messaging**.
- Implements basic MQTT-style commands: `create`, `subscribe`, `publish`, `unsubscribe`, and `exit`.

## ⚙️ Features

✅ TLS-based mutual authentication (server & client certificates)  
✅ Digital envelope with Fernet symmetric key encryption  
✅ Asymmetric encryption (RSA) for secure key exchange  
✅ Message confidentiality using Fernet  
✅ Topic-based pub/sub messaging  
✅ Multi-client support via threading  

## 🗂️ Project Structure

```
project-root/
│
├── src/
│   ├── broker.py                # Main broker class
│   ├── client_handler.py        # Handles client connection and communication
│   └── security/
│       ├── auth.py              # Key and certificate handling, signing, encryption
│       ├── client_keys/         # Clients' public keys (PEM)
│       ├── server_keys/         # Broker's public/private keys (PEM)
│       └── certificates/        # Broker certificate (.crt)
```

## 🚀 How It Works

1. **Client connects to the broker**
2. **Mutual TLS handshake**:
   - Broker sends its certificate and signed challenge
   - Client sends its certificate and signed challenge
3. Broker:
   - Verifies client's certificate was signed by the broker
   - Verifies the client's digital signature
4. **Session key exchange**:
   - Broker generates a symmetric key (Fernet)
   - Encrypts it with the client's public key
   - Client decrypts and establishes the session

## 📬 Commands Supported

| Command     | Description                                                                          |
|-------------|--------------------------------------------------------------------------------------|
| `create`    | Creates a new topic. Sends public keys for clients to allow encrypted topic access. |
| `subscribe` | Subscribes the client to a topic and sends past messages.                           |
| `publish`   | Publishes a message encrypted with the topic key to all subscribers.                |
| `unsubscribe`| Unsubscribes the client from a topic.                                               |
| `exit`      | Terminates the client session.                                                       |

## 🔐 Security Details

- 🔑 **Symmetric Encryption**: All messages and session communication are encrypted using `Fernet`.
- 🔏 **Asymmetric Encryption**: RSA is used for securely sending the session key to the client.
- 📜 **Certificates**: Broker and clients use `.crt` X.509 certificates for authentication.
- ✍️ **Digital Signatures**: Verifies possession of private keys before communication.


## 🛠 Requirements

- Python 3.10+
- `cryptography` library  
  Install it via pip:

```bash
pip install -r requirements.txt
```

## 🧪 Running the Broker

```bash
python src/broker.py
```

Default host is set to `127.0.0.1` , change it to your machine's local IP for LAN testing.

## 📄 License

This project is intended for **educational use** only.  
