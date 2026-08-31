# CKA Cheat Sheet: ConfigMaps & Secrets

> **Scope**: Configuration & Security  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

ConfigMaps and Secrets are used to decouple configuration artifacts and sensitive data from your container images. This keeps images portable across Dev, Staging, and Prod.

---

## 1. ⚡ Imperative Commands (CKA Speed Strategy)

**ConfigMaps:**
```bash
# Create CM from literal
kubectl create configmap web-config --from-literal=theme=dark --from-literal=env=prod

# Create CM from file
kubectl create configmap file-config --from-file=game.properties

# Output YAML without creating
kubectl create cm my-config --from-literal=key1=value1 --dry-run=client -o yaml > cm.yaml
```

**Secrets:**
```bash
# Create generic Secret from literal
kubectl create secret generic db-secret --from-literal=dbpass=P@ssw0rd!

# Create a TLS secret (e.g. for Ingress)
kubectl create secret tls my-tls --cert=path/to/cert/file --key=path/to/key/file
```

---

## 2. Using Them in Pods

You can inject ConfigMaps/Secrets into Pods in two main ways: **Environment Variables** or **Mounted Volumes**.

### A. Environment Variables
*Best for injecting specific database URLs or single keys.*
```yaml
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: dbpass
    - name: THEME
      valueFrom:
        configMapKeyRef:
          name: web-config
          key: theme
```

### B. Mounted Volumes
*Best for dropping entire configuration files (like nginx.conf) into a container folder. If the ConfigMap is updated, the file in the pod updates automatically over time.*
```yaml
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: web-config
```

---

## 3. Important Exam Tips
1. **Secrets are NOT encrypted by default!** They are only Base64 encoded in `etcd`. Anyone with access to the Secret object can read it `echo "cGFzc3dvcmQ=" | base64 --decode`.
2. To genuinely encrypt secrets, you must enable `EncryptionConfiguration` at the API Server level (common advanced CKA question).
3. If a Pod uses a ConfigMap/Secret as a Volume and it gets updated, it takes ~1 minute to sync into the Pod.
4. If a Pod uses a ConfigMap/Secret as an Environment Variable, the Pod must be **restarted** to pick up the new value!
