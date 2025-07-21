# 🚀 Targeted Code File Delivery System using AWS S3 + Lambda + DynamoDB

## 👋 Introduction

This project was built to solve a real-world deployment problem for a friend. The idea was to create a simple but effective system that lets an administrator upload unique code files for each machine (identified via machine ID), and ensure that only the intended machine can download its respective file.

The system is secure, efficient, cloud-hosted on AWS, and easy to extend.

---

## ❓ Problem Statement

We had the following problem:

> “I have different code files for different machines. I want to upload each machine’s code file from my central system, and ensure that **only that machine** can download and execute its assigned file.”

Challenges we faced:
- Handling 150+ machines with their own dedicated files.
- Preventing file corruption during upload/download.
- Ensuring only one file exists per machine (old file must be deleted on new upload).
- Making the system lightweight and cost-efficient (AWS Free Tier friendly).

---

## 🎯 Requirements & Features

- 🔒 Secure file upload to AWS S3 using Python API.
- 🎯 Each file is tied to a specific `machine_id`.
- 📥 Machine downloads its file via unique signed URL using `machine_id`.
- ♻️ When a new file is uploaded for the same machine, the **previous file is deleted**.
- 🗃️ File metadata is stored in **DynamoDB** (machine ID ↔ S3 key mapping).
- ⚡ Instant file availability via AWS S3.
- 💬 CORS support and proper headers for frontend integration.

---

## 🛠 Tech Stack Used

| Layer         | Tools / Services                                 |
|---------------|--------------------------------------------------|
| Cloud Storage | AWS S3                                           |
| API Backend   | AWS Lambda (Python)                              |
| Database      | AWS DynamoDB                                     |
| Auth (Basic)  | Machine ID based (can extend to token/API keys)  |
| Frontend      | React.js (Axios / Fetch based form uploads)      |
| Infrastructure| IAM Roles, Lambda Permissions, CORS, S3 CORS     |

---

## 🧠 Solution Overview

We designed the following system:

1. **File Upload (Admin only)**  
   - Admin uploads a file with a query parameter `machine_id`.  
   - Backend stores the file in S3 under a specific key: `files/{machine_id}/{timestamp}.ext`.  
   - If a file already exists for that machine, it is **deleted**.  
   - DynamoDB is updated with the latest file mapping.

2. **File Download (Machine)**  
   - Each machine makes a `GET` request with `machine_id`.  
   - Backend returns a **pre-signed S3 URL** valid for 1 hour.  
   - Only the file for that machine ID is returned.

This ensures **targeted delivery, clean versioning**, and easy scalability.

---

## 🔧 Project Setup Instructions

### 1️⃣ Clone the Project
```bash
git clone https://github.com/your-username/aws-machine-file-distributor.git
cd aws-machine-file-distributor
```
### ✅ .env file (placed at the root of your React project)
```bash
REACT_APP_API_URL=https://your-api-gateway-url.amazonaws.com/prod
```

### 2️⃣ Create Virtual Environment & Install
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3️⃣ Configure AWS Credentials
Make sure your local machine or Lambda has AWS credentials with the correct policy:
```bash
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:*", "dynamodb:*"],
      "Resource": "*"
    }
  ]
}
```
### ☁️ AWS Deployment Guide
✅ S3 Bucket Setup
Create an S3 bucket, e.g., machine-code-files

Enable CORS with:
```bash
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```
✅ DynamoDB Setup
Create a table called MachineFiles

Primary key: machine_id (string)

✅ Lambda Functions
Deploy two Lambda functions:

a) Upload Handler
Trigger: API Gateway (POST)

Responsibilities:

Decode base64 multipart form

Parse machine_id

Delete previous file (if any)

Upload new file to S3

Update DynamoDB

b) Download Handler
Trigger: API Gateway (GET)

Responsibilities:
Accept machine_id

Lookup S3 key from DynamoDB

Generate a pre-signed URL for 1 hour

✅ API Gateway Setup
Enable binary support for file uploads

Set CORS headers:
```bash
Access-Control-Allow-Origin: *,
Access-Control-Allow-Methods: POST, GET,
Access-Control-Allow-Headers: *
```
### 💻 Usage Instructions
Upload (Admin Panel / Script)
```bash
POST /upload?machine_id=MACHINE_001
Content-Type: multipart/form-data

Form:
  file: (Select your file)
```
Old file (if any) is deleted
New file is uploaded to s3://bucket/files/MACHINE_001/xyz.zip

### Download (Machine-side script)
```bash
GET /download?machine_id=MACHINE_001
```
Returns a redirect (302) to a signed S3 URL
Machine downloads only its own file

### 🔮 Future Improvements
Add API key-based authentication for more secure access.
Support file versioning or file history logs.
Add frontend dashboard for file uploads and monitoring.
Add logging and alerting when machines download files.

### 🙌 Credits / Acknowledgments
Built using AWS services (S3, Lambda, DynamoDB).
Special thanks to ChatGPT for planning assistance.
Inspired by a real-world automation problem faced by a friend!


