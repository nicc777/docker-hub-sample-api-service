
- [Intro](#intro)
- [Creating a Namespace](#creating-a-namespace)
- [Pods](#pods)
- [Deployments](#deployments)
- [Adding a service to a Deployment (exposing the deployed Pods)](#adding-a-service-to-a-deployment-exposing-the-deployed-pods)

# Intro

Here are some examples to familiarize you with Kubernetes. If you do not have a Kubernetes environment, consider something like [this k3s quick start](https://gist.github.com/nicc777/0f620c9eb2958f58173224f29b23a2ff) guide.

You may also want to keep [this cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) nearby.

# Creating a Namespace

Reference: [Namespaces Walkthrough](https://kubernetes.io/docs/tasks/administer-cluster/namespaces-walkthrough/)

```bash
$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   60d
kube-system       Active   60d
kube-public       Active   60d
kube-node-lease   Active   60d

$ kubectl create -f kubernetes/admin/namespace-dev.yaml
namespace/development created

$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   60d
kube-system       Active   60d
kube-public       Active   60d
kube-node-lease   Active   60d
development       Active   3s
(venv)
```

The new namespace `development` have been added.

To set this as the default namespace for all you subsequent `kubectl` commands, run:

```bash
$ kubectl config set-context --current --namespace=development
Context "default" modified.

$ kubectl get all
No resources found in development namespace.
```

# Pods

Reference: [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)

Creating a simple stand-alone Pod:

```bash
$ kubectl create -f kubernetes/deployments/basic-pod-v2.yaml
pod/sample-api-service-pod created

$ kubectl get all
NAME                         READY   STATUS    RESTARTS   AGE
pod/sample-api-service-pod   1/1     Running   0          3s

$ kubectl logs pod/sample-api-service-pod
[2020-07-28 08:25:47 +0000] [1] [INFO] Starting gunicorn 20.0.4
[2020-07-28 08:25:47 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2020-07-28 08:25:47 +0000] [1] [INFO] Using worker: sync
[2020-07-28 08:25:47 +0000] [9] [INFO] Booting worker with pid: 9
10.42.1.1 - - [28/Jul/2020:08:25:53 +0000] "GET /readiness HTTP/1.1" 200 16 "-" "kube-probe/1.18"
10.42.1.1 - - [28/Jul/2020:08:25:54 +0000] "GET /liveness HTTP/1.1" 200 16 "-" "kube-probe/1.18"
```

You can also tail logs with:

```bash
$ kubectl logs -f pod/sample-api-service-pod
[2020-07-28 08:25:47 +0000] [1] [INFO] Starting gunicorn 20.0.4
[2020-07-28 08:25:47 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2020-07-28 08:25:47 +0000] [1] [INFO] Using worker: sync
[2020-07-28 08:25:47 +0000] [9] [INFO] Booting worker with pid: 9
10.42.1.1 - - [28/Jul/2020:08:25:53 +0000] "GET /readiness HTTP/1.1" 200 16 "-" "kube-probe/1.18"
10.42.1.1 - - [28/Jul/2020:08:25:54 +0000] "GET /liveness HTTP/1.1" 200 16 "-" "kube-probe/1.18"
10.42.1.1 - - [28/Jul/2020:08:26:04 +0000] "GET /liveness HTTP/1.1" 200 16 "-" "kube-probe/1.18"
10.42.1.1 - - [28/Jul/2020:08:26:14 +0000] "GET /liveness HTTP/1.1" 200 16 "-" "kube-probe/1.18"
^C
```

You will be able to see the `liveness` probe every 10 seconds.

To delete the Pod:

```bash
$ kubectl delete pod/sample-api-service-pod
pod "sample-api-service-pod" deleted

$ kubectl get all
No resources found in development namespace.
```

# Deployments

Reference: [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

To create a deployment in the current namespace:

```bash
$ kubectl apply -f kubernetes/deployments/deployment-pod-v2.yaml
deployment.apps/sample-api-deployment created

$ kubectl get all
NAME                                         READY   STATUS    RESTARTS   AGE
pod/sample-api-deployment-75dc85446c-2lf59   1/1     Running   0          47s
pod/sample-api-deployment-75dc85446c-9fdhx   1/1     Running   0          4s

NAME                                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/sample-api-deployment   2/2     2            2           47s

NAME                                               DESIRED   CURRENT   READY   AGE
replicaset.apps/sample-api-deployment-75dc85446c   2         2         2       47s
```

To *live update* the running deployment and add another Pod, run the following command:

```bash
$ kubectl edit deployment.apps/sample-api-deployment
```

Search for the line containing `replicas: 2` and change the `2` to `3`. Save and exit the file. You should now see 3 pods running and ready:

```bash
$ kubectl get pods
NAME                                     READY   STATUS    RESTARTS   AGE
sample-api-deployment-75dc85446c-2lf59   1/1     Running   0          4m9s
sample-api-deployment-75dc85446c-9fdhx   1/1     Running   0          3m26s
sample-api-deployment-75dc85446c-bb5tb   1/1     Running   0          103s
```

Once you are done, cleanup:

```bash
$ kubectl delete deployment.apps/sample-api-deployment
deployment.apps "sample-api-deployment" deleted
```

# Adding a service to a Deployment (exposing the deployed Pods)

Reference: 

* [Create an External Load Balancer](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/)
* [Connecting Applications with Services](https://kubernetes.io/docs/concepts/services-networking/connect-applications-service/)

Run the following command to apply the service config:

```bash
$ kubectl apply -f kubernetes/deployments/service-v2.yaml
service/sample-api-service created

NAME                                 READY   STATUS              RESTARTS   AGE
pod/svclb-sample-api-service-rgvn7   0/1     ContainerCreating   0          2s
pod/svclb-sample-api-service-x8fd2   1/1     Running             0          2s
pod/svclb-sample-api-service-tmtwf   1/1     Running             0          2s

NAME                         TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)          AGE
service/sample-api-service   LoadBalancer   10.43.221.46   192.168.64.5   8080:31302/TCP   2s

NAME                                      DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/svclb-sample-api-service   3         3         3       3            3           <none>          2s
```

Test:

```bash
TODO
```


