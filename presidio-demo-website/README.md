[![Build Status](https://dev.azure.com/csedevil/Presidio/_apis/build/status/Presidio-demo-website?branchName=master)](https://dev.azure.com/csedevil/Presidio/_build/latest?definitionId=56?branchName=master)

# Presidio Demo Website

[Demo website](https://presidio-demo.westeurope.cloudapp.azure.com/) to display the capabilities of [presidio](https://github.com/Microsoft/presidio).

## Getting Started

### Run locally

```sh
$ npm install

# Run dev environment
$ npm run start dev

# Production: Build & serve
$ npm run build
$ serve -s build
```

### Build and run with Docker

```sh
$ docker build -t presidio-demo .
$ docker run -p 5000:5000 presidio-demo
```

---

Thank you [@morsh](https://github.com/morsh/) for the support and [starter kit](https://github.com/morsh/react-client-server-starter)
