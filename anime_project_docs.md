# ![LLMOps](https://img.shields.io/badge/Anime%20Recommender%20System-LLMOps-blueviolet)

# 🧠 Anime Recommender System — LLMOps Deployment Guide

Welcome to the **Anime Recommender System powered by LLMOps**. This guide provides a professional, step-by-step walkthrough to deploy your application using:

- 🐳 **Docker**
- ☸️ **Kubernetes (Minikube)**
- ☁️ **Google Cloud VM**
- 📈 **Grafana Cloud Monitoring**

---

## 📦 1. Initial Setup

### 🚀 Push Code to GitHub

Push your project to GitHub:

```bash
git init
git remote add origin https://github.com/Najam0786/ANIME-RECOMMENDER-SYSTEM-LLMOPS.git
git checkout -b main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 🐳 Create a Dockerfile

Add a `Dockerfile` in your root directory to containerize your application.

### ☸️ Create a Kubernetes Deployment File

Create a file named `llmops-k8s.yaml`.

### ☁️ Create a VM Instance on Google Cloud

- Go to **VM Instances** > Click **Create Instance**
- Name: `anime-recommender`
- Machine Type:
  - Series: `E2`
  - Preset: `Standard`
  - Memory: `16 GB RAM`
- Boot Disk:
  - Size: `256 GB`
  - Image: **Ubuntu 24.04 LTS**
- Networking:
  - ✅ Enable HTTP and HTTPS traffic

Click **Create** and then connect using **SSH** from browser.

---

## 🛠️ 2. Configure VM Instance

### 🔁 Clone Your Repository

```bash
git clone https://github.com/Najam0786/ANIME-RECOMMENDER-SYSTEM-LLMOPS.git
cd ANIME-RECOMMENDER-SYSTEM-LLMOPS
```

### 🐳 Install Docker

1. Search: _Install Docker on Ubuntu_
2. Follow official instructions at [https://docs.docker.com](https://docs.docker.com)
3. Test Docker:

```bash
docker run hello-world
```

### 🔓 Run Docker Without Sudo

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

### 🧰 Enable Docker to Start on Boot

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

### ✅ Verify Docker Setup

```bash
systemctl status docker
docker ps
docker ps -a
```

---

## ☸️ 3. Install Minikube and kubectl

### 🔧 Install Minikube

Follow [https://minikube.sigs.k8s.io](https://minikube.sigs.k8s.io) → Linux → Binary download section.

```bash
minikube start
```

### 🔧 Install kubectl

```bash
sudo snap install kubectl --classic
kubectl version --client
```

### ✅ Minikube Health Check

```bash
minikube status
kubectl get nodes
kubectl cluster-info
docker ps
```

---

## 🔗 4. GitHub Config on VS Code or VM

```bash
git config --global user.email "nazmulfarooquee@gmail.com"
git config --global user.name "Najam0786"

git add .
git commit -m "commit"
git push origin main
```

---

## 🚀 5. Build & Deploy Application

```bash
# Point Docker to Minikube
eval $(minikube docker-env)

# Build Docker image
docker build -t llmops-app:latest .

# Create Secrets
kubectl create secret generic llmops-secrets \
  --from-literal=GROQ_API_KEY="" \
  --from-literal=HUGGINGFACEHUB_API_TOKEN=""

# Apply K8s Deployment
kubectl apply -f llmops-k8s.yaml

kubectl get pods
```

### 🧪 Test Deployment

```bash
minikube tunnel
```
Open new terminal:

```bash
kubectl port-forward svc/llmops-service 8501:80 --address 0.0.0.0
```
Visit your external IP: `http://<external-ip>:8501`

---

## 📊 6. Grafana Cloud Monitoring Setup

### 🧰 Create Monitoring Namespace

```bash
kubectl create ns monitoring
kubectl get ns
```

### 🧠 Create Grafana Cloud Account

1. Go to [https://grafana.com](https://grafana.com)
2. Navigate to **Observability > Kubernetes > Start sending data**
3. Set:
   - Cluster name: `minikube`
   - Namespace: `monitoring`
4. Create access token: `minikube-token`

### 🧰 Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 📄 Create `values.yaml`
Paste provided values from Grafana UI, but **remove** `<<EOF` and the ending `EOF`

### 📦 Install Grafana Monitoring Stack

```bash
helm repo add grafana https://grafana.github.io/helm-charts && \
  helm repo update && \
  helm upgrade --install --atomic --timeout 300s grafana-k8s-monitoring grafana/k8s-monitoring \
  --namespace monitoring --create-namespace --values values.yaml
```

### ✅ Verify Monitoring

```bash
kubectl get pods -n monitoring
```
Refresh Grafana UI and explore your cluster metrics.

---

## ✅ Clean Up

Don’t forget to delete unused pods, secrets, and optionally your VM instance to avoid extra charges.

---

## ✉️ Author

- GitHub: [Najam0786](https://github.com/Najam0786)
- Email: [nazmulfarooquee@gmail.com](mailto:nazmulfarooquee@gmail.com)

---

Feel free to ⭐ the repo if you found it helpful!
