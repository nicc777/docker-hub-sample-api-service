
- [Intro](#intro)
- [Creating a Namespace](#creating-a-namespace)
- [Pods](#pods)
- [Deployments](#deployments)
- [Adding a service to a Deployment (exposing the deployed Pods)](#adding-a-service-to-a-deployment-exposing-the-deployed-pods)
- [Miscellaneous Tasks](#miscellaneous-tasks)
  - [Getting a shell in a Pod](#getting-a-shell-in-a-pod)
  - [Manually Scaling a Service at Runtime](#manually-scaling-a-service-at-runtime)
  - [Perform a rolling update](#perform-a-rolling-update)
  - [Forcing a restart](#forcing-a-restart)
  - [Observing Kubernetes Automatically Replace a Deleted Pod](#observing-kubernetes-automatically-replace-a-deleted-pod)

# Intro

Here are some examples to familiarize you with Kubernetes. If you do not have a Kubernetes environment, consider something like [this k3s quick start](https://gist.github.com/nicc777/0f620c9eb2958f58173224f29b23a2ff) guide.

Once you have a running cluster, and assuming you have followed the instructions for the `k3s quick start`, you can point your `kubectl` config to it (the example assumes the config file is saved in your home directory):

```bash
$ export KUBECONFIG=$HOME/k3s.yaml
```

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


$ kubectl get all
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
$ curl http://192.168.64.5:8080/version
{"version": "2.0.0", "timestamp": "2020-07-28T12:06:01.621629", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-hnz24", "ip_address": "10.42.1.49"}
```

# Miscellaneous Tasks

## Getting a shell in a Pod

```bash
$ kubectl get pods
NAME                                        READY   STATUS    RESTARTS   AGE
sample-api-deployment-v2-646f4b4ccc-zsp6z   0/1     Running   0          3m34s
sample-api-deployment-v2-646f4b4ccc-fv75q   0/1     Running   0          3m34s

$ kubectl exec --stdin --tty sample-api-deployment-v2-646f4b4ccc-zsp6z -- /bin/bash
```

You should now be able to execute commands inside the Pod.

## Manually Scaling a Service at Runtime

The default number of nodes as per the manifest is `2`. At runtime we can scale by directly editing the running configuration:

```bash
$ kubectl get deployments
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE                                                                                   │{"version": "2.0.0", "timestamp": "2020-07-28T12:09:15.311421", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
sample-api-deployment-v2   4/4     4            4           22m

$ kubectl edit deployment sample-api-deployment-v2
```


Search for the line containing `replicas: 2` and change the `2` to `3`. Save and exit the file. You should now see 3 pods running and ready:

```bash
$ kubectl get pods
NAME                                     READY   STATUS    RESTARTS   AGE
sample-api-deployment-75dc85446c-2lf59   1/1     Running   0          4m9s
sample-api-deployment-75dc85446c-9fdhx   1/1     Running   0          3m26s
sample-api-deployment-75dc85446c-bb5tb   1/1     Running   0          103s
```

## Perform a rolling update

For this demonstration, open another Terminal window and run the following command:

```bash
$ while true
do curl 192.168.64.5:8080/version
sleep 1
done
```

You should now see a continuous stream of output from the different nodes:

```json
{"version": "2.0.0", "timestamp": "2020-07-28T12:13:40.777061", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-hnz24", "ip_address": "10.42.1.49"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:13:41.922566", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:13:42.849771", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-hnz24", "ip_address": "10.42.1.49"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:13:43.874415", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-hnz24", "ip_address": "10.42.1.49"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:13:45.024193", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:13:46.062818", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
```

While this is running, edit the deployment:

```bash
$ kubectl get deployments
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE                                                                                   │{"version": "2.0.0", "timestamp": "2020-07-28T12:09:15.311421", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
sample-api-deployment-v2   4/4     4            4           22m

$ kubectl edit deployment sample-api-deployment-v2
```

Search for `- image: nicc777/sample-api-service:v2` and replace the `v2` with `v3`. The line should now read: `- image: nicc777/sample-api-service:v3`

Save and exit. After a while you will see the other terminal monitor update with something like this:

```json
{"version": "2.0.0", "timestamp": "2020-07-28T12:16:48.659734", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:16:49.687131", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:16:50.511074", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-hnz24", "ip_address": "10.42.1.49"}
{"version": "3.0.0", "timestamp": "2020-07-28T12:16:51.545638", "features": ["Readiness can be toggled", "Liveness can be toggled"], "hostname": "sample-api-deployment-v2-79fcd7796b-tnh2w", "ip_address": "10.42.0.35"}
{"version": "3.0.0", "timestamp": "2020-07-28T12:16:52.569497", "features": ["Readiness can be toggled", "Liveness can be toggled"], "hostname": "sample-api-deployment-v2-79fcd7796b-tnh2w", "ip_address": "10.42.0.35"}
{"version": "3.0.0", "timestamp": "2020-07-28T12:16:53.603758", "features": ["Readiness can be toggled", "Liveness can be toggled"], "hostname": "sample-api-deployment-v2-79fcd7796b-tnh2w", "ip_address": "10.42.0.35"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:16:54.861941", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "3.0.0", "timestamp": "2020-07-28T12:16:55.665254", "features": ["Readiness can be toggled", "Liveness can be toggled"], "hostname": "sample-api-deployment-v2-79fcd7796b-tnh2w", "ip_address": "10.42.0.35"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:16:56.921590", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "3.0.0", "timestamp": "2020-07-28T12:16:57.723390", "features": ["Readiness can be toggled", "Liveness can be toggled"], "hostname": "sample-api-deployment-v2-79fcd7796b-tnh2w", "ip_address": "10.42.0.35"}
{"version": "2.0.0", "timestamp": "2020-07-28T12:16:59.023583", "features": ["Readiness can be toggled"], "hostname": "sample-api-deployment-v2-6945f97bcf-kn757", "ip_address": "10.42.2.45"}
{"version": "3.0.0", "timestamp": "2020-07-28T12:16:59.844297", "features": ["Readiness can be toggled", "Liveness can be toggled"], "hostname": "sample-api-deployment-v2-79fcd7796b-tnh2w", "ip_address": "10.42.0.35"}
```

Eventually you should see only `{"version": "3.0.0"...` servers responding.

## Forcing a restart

Version 3 of the application (see the previous sub-section) has a utility to allow us to toggle the readiness value of the service. When Kubernetes sees that the Pod is no longer ready it will restart it.

You can open another terminal window and issue the following command:

```bash
$ watch kubectl get all
```

The screen will automatically update, and it should look something like this:

```text
Every 2.0s: kubectl get all               Nicos-MacBook-Pro-2.local: Tue Jul 28 14:20:07 2020

NAME                                            READY   STATUS    RESTARTS   AGE
pod/svclb-sample-api-lb-service-jxrmg           1/1     Running   0          25m
pod/svclb-sample-api-lb-service-wr7pq           1/1     Running   0          25m
pod/svclb-sample-api-lb-service-c9l9g           1/1     Running   0          25m
pod/sample-api-deployment-v2-79fcd7796b-tnh2w   1/1     Running   0          3m27s
pod/sample-api-deployment-v2-79fcd7796b-dmfx4   1/1     Running   0          3m16s

NAME                            TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)          AGE
service/sample-api-lb-service   LoadBalancer   10.43.121.233   192.168.64.4   8080:30133/TCP   25m

NAME                                         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/svclb-sample-api-lb-service   3         3         3       3            3           <none>          25m

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/sample-api-deployment-v2   2/2     2            2           33m

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/sample-api-deployment-v2-646f4b4ccc   0         0         0       33m
replicaset.apps/sample-api-deployment-v2-79fcd7796b   2         2         2       23m
replicaset.apps/sample-api-deployment-v2-6945f97bcf   0         0         0       26m
```

Now, in another open terminal run the following command:

```bash
$ curl http://192.168.64.4:8080/admin/liveness-toggle
{"CommandStatus": "Ok"}
```

In the terminal window running the `watch` command you should now see one of the Pods have been restarted:

```text
pod/svclb-sample-api-lb-service-jxrmg           1/1     Running   0          27m
pod/svclb-sample-api-lb-service-wr7pq           1/1     Running   0          27m
pod/svclb-sample-api-lb-service-c9l9g           1/1     Running   0          27m
pod/sample-api-deployment-v2-79fcd7796b-dmfx4   1/1     Running   0          4m56s
pod/sample-api-deployment-v2-79fcd7796b-tnh2w   1/1     Running   1          5m7s
```

## Observing Kubernetes Automatically Replace a Deleted Pod

You will also see that if a Pod is completely deleted, Kubernetes will automatically replace it. This is sometimes handy for a misbehaving Pod an administrator wants to forcefully remove to force a re-creation of a new replacement Pod:

```bash
$ kubectl get pods
NAME                                        READY   STATUS    RESTARTS   AGE
svclb-sample-api-lb-service-jxrmg           1/1     Running   0          29m
svclb-sample-api-lb-service-wr7pq           1/1     Running   0          29m
svclb-sample-api-lb-service-c9l9g           1/1     Running   0          29m
sample-api-deployment-v2-79fcd7796b-dmfx4   1/1     Running   0          7m30s
sample-api-deployment-v2-79fcd7796b-tnh2w   1/1     Running   1          7m41s

$ kubectl delete pod sample-api-deployment-v2-79fcd7796b-dmfx4
```

The the terminal window with the `watch` command you will notice the Pod being removed an a new one spinning up:

```text
NAME                                            READY   STATUS        RESTARTS   AGE
pod/svclb-sample-api-lb-service-jxrmg           1/1     Running       0          30m
pod/svclb-sample-api-lb-service-wr7pq           1/1     Running       0          30m
pod/svclb-sample-api-lb-service-c9l9g           1/1     Running       0          30m
pod/sample-api-deployment-v2-79fcd7796b-tnh2w   1/1     Running       1          8m50s
pod/sample-api-deployment-v2-79fcd7796b-dmfx4   0/1     Terminating   0          8m39s
pod/sample-api-deployment-v2-79fcd7796b-2crww   0/1     Running       0          5s
```

There should be no interruption of your `curl` command.