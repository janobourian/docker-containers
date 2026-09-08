# k8s

* Container Orchestration System
* Declarative Approach to infrastructure management
* Kubernetes concepts:
    * Nodes: are the worker machines (VMs or bare metal) that run your containers
    * Cluster: a group of nodes working together
    * Master: is the brain of the cluster
    * kubectl: command-line tool to communicate with the API server
    * Pods: are the smallest deployable units in Kubernetes (e.g. a pod can have one or more containers)
    * Components: are processes that run on the master and worker nodes
        * API Server: is the RESTful interface to the control plane
        * etcd: is the key-value store for the cluster
        * Scheduler: decides which node to run a pod on
        * Controller: are processes that watch the API server and maintain the desired state
        * kubelet: is the agent that runs on each node and manages the pods
        * kube-proxy: is the agent that runs on each node and manages the pods
        * kube-apiserver: is the frontend to the control plane
        * Container Runtime: is the software that runs the containers on the nodes (e.g. containerd, CRI-O, Docker)
    * Services:
        * ClusterIP: exposes the service on a cluster-internal IP
        * NodePort: exposes the service on a port on each node
        * LoadBalancer: exposes the service on a load balancer
        * ExternalName: exposes the service on an external name
    * Namespaces: are used to divide cluster resources between multiple users
