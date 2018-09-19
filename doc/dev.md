1. Setup Node Environment

- Download node package from https://nodejs.org/en/download/ and extract
  to /opt/.  Add to PATH in ~/.bashrc.
```
export PATH=$PATH:/opt/node-v8.12.0-linux-x64/bin
```



2. Build JS.
```
cd vue-element-admin
npm install	# this will be very slow
```
https://panjiachen.github.io/vue-element-admin-site/zh/guide/

3. Rebuild and Run
```
./rebuild.sh
./run.sh
```

4. Debug UI
Run django server in one terminal.
```
./run.sh
```
Then run node debug server in another.
```
cd vue-element-admin
npm run dev
```

