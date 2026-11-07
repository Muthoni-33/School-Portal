# 🏫 School Portal Monorepo

## 📝 Project Overview
The **School Portal Monorepo** houses a decoupled, production-ready microservices architecture tailored for robust academic and user management infrastructure. By separating domain logic into isolated, containerized application runtimes, the system achieves maximum fault isolation, ultra-fast localized processing, and independent horizontal scalability.

This ecosystem is engineered for strict enterprise resiliency, ensuring zero-downtime financial and classroom transactions even under volatile, high-concurrency traffic conditions typical during academic enrollment or grading seasons.

---

## 🏗️ Architecture Overview
The platform follows a headless, decoupled cloud-native topology. Traffic transitions from edge distribution directly into a secured, multi-layered cluster environment:

```mermaid
graph TD
    User([Student/Teacher Browser]) -->|HTTPS Request| Ingress[Kubernetes Ingress Controller]
    
    subgraph K8s Network Isolation [Kubernetes Cluster Security Boundary]
        Ingress -->|Layer 7 Path Routing /api/v1/auth| NetPolicy[Network Policy Enforcer]
        Ingress -->|Layer 7 Path Routing /api/v1/classes| NetPolicy
        
        NetPolicy -->|Allowed Ingress| ServiceAuth[Auth ClusterIP Service: Port 5001]
        NetPolicy -->|Allowed Ingress| ServiceClass[Classes ClusterIP Service: Port 5002]
        
        ServiceAuth -->|Distributed Traffic| AuthPod[Auth Deployment Pods]
        ServiceClass -->|Distributed Traffic| ClassPod[Classes Deployment Pods]
        
        AuthPod -->|Secure DB Wire / Port 5432| AuthDB[(PostgreSQL StatefulSet)]
        ClassPod -->|Secure DB Wire / Port 5432| ClassDB[(PostgreSQL ClassesSet)]
        
        AuthDB -->|Mount| PVC1[Persistent Volume Claim]
        ClassDB -->|Mount| PVC2[Persistent Volume Claim]
    end
```

### End-to-End Enterprise Request Lifecycle:
1. **Edge Entry & Reverse Proxying:** Public browser traffic strikes the **Kubernetes Ingress Controller** over HTTPS. The Ingress acts as the frontline shield, managing SSL/TLS decryption and stripping malicious headers.
2. **Layer 7 Routing:** The Ingress inspects request path definitions. Traffic hitting `/api/v1/auth` is cleanly routed toward the `auth-service`, while `/api/v1/classes` is mapped to the `classes-service`.
3. **Network Isolation Enforcement:** Before reaching application workloads, traffic passes through rigid **Network Policies**. These security guardrails restrict cross-pod communication, ensuring only authorized frontend components can interface with application pods, and absolutely no public internet traffic can ever speak directly to internal databases.
4. **Internal Load Balancing:** Kubernetes **Services (ClusterIP)** catch the routed traffic and spread connections evenly across individual service **Pods** using internal cluster routing mechanisms.
5. **Data Orchestration & Persistence:** Application processes access underlying transactional engines via isolated backend streams. Stateful data is dispatched directly to dedicated database engines running as **StatefulSets**, with physical operations committed to raw cloud blocks via **Persistent Volume Claims (PVC)**.

---

## 💻 Tech Stack & Components
* **Backend Runtime Core:** Python 3.12 powered by the lightweight **Flask API** framework.
* **Production Gateway Multiplier:** **Gunicorn** (WSGI process execution wrapper allocating worker execution nodes directly proportional to available worker CPU capacities).
* **Persistent Storage Engines:** **PostgreSQL 15+** instances bound securely inside hidden private network spaces operating on default port `5432`.
* **Ecosystem Packages Directory:** Tracked and locked cleanly via microservice-specific `requirements.txt` manifests (`psycopg2-binary`, `Flask`, `gunicorn`).

---

## ⚙️ Pattern Implementation & Deployment Strategies

### 🛠️ Kubernetes Declarative Manifest Architecture
The application infrastructure is deployed deterministically via a complete matrix of cloud-native manifests stored under the `/k8s` directory:

* **Deployments:** Manages the stateless application runtimes for `auth-service` and `class-service`, declaring explicit image tags, scaling boundaries, and container lifecycles.
* **Services:** Provides immutable, internal **ClusterIP** endpoints, serving as the localized abstraction layer for pod-to-pod and gateway communications.
* **ConfigMaps & Secrets Configuration Pattern:** Complete environment decoupling is enforced across all repositories. Non-sensitive targets (`DB_HOST`, `DB_PORT`, `DB_NAME`) are mapped inside **ConfigMaps**, while sensitive access strings (`DB_USER`, `DB_PASSWORD`) are stored in base64-encoded **Secrets**.
* **Dynamic `env` Block Injections:** Pod manifests feature explicit `envFrom` references. These hooks catch ConfigMap/Secret values and bind them directly into Python's `os.environ` slots at initial runtime initialization.
* **Network Policies:** Acts as a pod-level firewall, controlling ingress traffic filters and egress routing parameters to block unauthorized internal cluster cross-talk.
* **Ingress Rules:** Maps Layer 7 routing blueprints, handling TLS certificates (`kubernetes.io/tls`) and pointing custom subdomains to target internal ClusterIP services cleanly.

### 🛡️ High-Availability, Scaling & Cluster Resiliency Policies
To prevent single points of failure and guarantee performance under load, the deployment models incorporate rigorous platform policies:

* **Pod Anti-Affinity Scheduling Configuration:** To protect against localized infrastructure node outages, pod specs enforce strict **Pod Anti-Affinity rules** (`topologyKey: "kubernetes.io/hostname"`). This strictly blocks the Kubernetes scheduler from co-locating identical application replica pods onto the same physical cloud host. If a server node fails, remaining replicas on alternate servers pick up the active traffic instantly.
* **Pod Disruption Budgets (PDB):** System upgrades can cause node evictions. We implement strict **PDB manifests** (`minAvailable: 50%`), forcing the Kubernetes API to block automated cluster actions if an operation threatens to drop the active online pod count below baseline safety thresholds.
* **Tuned Scaling Architecture (HPA & Cluster Autoscaler):** Pod resources feature hard-coded boundaries to facilitate seamless elastic growth paths:
    * **Resource Requests & Limits:** Memory and CPU limits are locked down (`resources.requests` and `resources.limits`).
    * **Horizontal Pod Autoscaler (HPA):** Monitors active processing metrics. When average container CPU metrics breach 75%, the HPA replicates matching pods across the node infrastructure immediately.
    * **Cluster Autoscaler (CA):** Controlled via a cluster-wide deployment running inside the `kube-system` namespace. If a massive traffic rush forces the HPA to spawn more pods than the available hardware nodes can handle, the **Cluster Autoscaler** intercepts the pending pod flags and automatically triggers the underlying cloud platform to provision brand-new physical virtual machine servers to join the cluster capacity pool.
* **Comprehensive Health Diagnostics Lifecycle (Probes):** Containers utilize a multi-tier automated diagnostic model to ensure traffic never hits broken endpoints:
    * **Startup Probes:** Holds off all secondary health tracking until heavy initial app environments finish bootstrapping.
    * **Readiness Probes:** Verifies database accessibility hooks are green before signaling the Service to include the container inside active user routing pools.
    * **Liveness Probes:** Continually monitors internal system loops. If an unhandled thread locks up Gunicorn, the probe fails and prompts Kubernetes to kill and reboot the pod instantly.

### 🔄 Zero-Downtime Rolling Update Strategy & GitOps Promotion
The platform implements an enterprise-grade **Progressive Image Promotion Pattern** distributed across three operational environment branches (`main`, `staging`, and `production`). Instead of rebuilding container images for every stage—which risks introducing version skew—the architecture enforces a **"Build Once, Promote via Registry"** strategy using **Crane** and GitOps principles.

```mermaid
graph LR
    A[Push to main] -->|1. Build & Test| B(DockerHub: dev-sha)
    B -->|2. Imperative Update| C[Dev EKS Cluster]
    
    D[Merge PR to staging] -->|3. Crane server-side tag| E(DockerHub: staging-sha)
    E -->|4. Declarative Manifest Write| F[Git Web Repo]
    F -->|5. GitOps Pull Sync| G[ArgoCD: Staging Cluster]
    
    H[Merge PR to production] -->|6. Crane server-side tag| I(DockerHub: prod-sha / latest)
    I -->|7. Declarative Manifest Write| J[Git Web Repo]
    J -->|8. GitOps Pull Sync| K[ArgoCD: Production Cluster]

    style A fill:#3377ff,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#ffaa00,stroke:#fff,stroke-width:2px,color:#fff
    style H fill:#00aa55,stroke:#fff,stroke-width:2px,color:#fff
```

#### 1. Development Baseline (`main` Branch)
* **Trigger Event:** Triggered automatically via explicit developer pushes (`git push origin main`).
* **Operational Flow:** The pipeline mounts a Python 3.12 runtime, runs deep verification suites (`pytest unit` and `integration`), and triggers security scans (**Gitleaks** and **Trivy FS**). It builds multi-architecture layer binaries (`linux/amd64`, `linux/arm64`) using Docker Buildx.
* **Registry Output:** The pristine image is pushed to your registry, tagged with the unique commit identifier: `dev-${{ github.sha }}`.
* **Cluster Deployment:** The pipeline uses an imperative `kubectl set image` command targeting the Dev environment to instantly roll out changes to the development cluster namespace.

#### 2. Staging Infrastructure Tracking (`staging` Branch - Pure GitOps)
* **Trigger Event:** Triggered when a validated code change is merged via a Pull Request into the `staging` tracking branch.
* **Promotion Engine (Crane):** To protect the deployment from environmental drift, **the Dockerfile is never re-compiled.** The runner utilizes Google's **Crane** utility to execute a server-side tag assignment. It points the existing, verified `dev-${{ github.sha }}` registry layer digest to a new tag metadata location: `staging-${{ github.sha }}` in less than 2 seconds.
* **ArgoCD Automation:** Following image tagging, the runner executes a `sed -i` string override on the repository's `k8s/deployment.yaml` file. The GitHub Actions bot commits this structural layout change directly back to the `staging` web branch with `contents: write` authorization. **ArgoCD** instantly notices the Git configuration update, detects the state difference between Git and EKS, and synchronizes the staging cluster workloads automatically.

#### 3. Production Hardening & Release (`production` Branch - Enterprise GitOps)
* **Trigger Event:** Triggered when staging validation criteria are satisfied and code is merged into the `production` deployment branch.
* **Secure Delivery Chain:** Crane tags the proven staging image layer to immutable production markers: `prod-${{ github.sha }}` and `latest`. The pipeline then triggers a final container scan, compiles an Anchore Software Bill of Materials (SBOM), and signs the layer cryptographically with a **Cosign Keyless Signature** utilizing OIDC identity federation tokens.
* **Resiliency Rollout:** The manifest write step commits the production image tag back to Git. The production instance of ArgoCD coordinates a rolling update using your configured `maxSurge: 25%` boundaries. Old pods are retired only after the new, signed production pods pass their startup and readiness health checks.

* 

#### 2. Staging Infrastructure Tracking (`staging` Branch - Pure GitOps)
