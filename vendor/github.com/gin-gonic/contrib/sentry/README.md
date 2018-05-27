# sentry

Middleware to integrate with [sentry](https://getsentry.com/) crash reporting.  Middleware version of `raven.RecoveryHandler()`.

## EOL-warning

**This package has been abandoned on 2017-01-13. Please use [gin-contrib/sentry](https://github.com/gin-contrib/sentry) instead.**

## Example
```go
package main

import (
  "github.com/getsentry/raven-go"
  "github.com/gin-gonic/contrib/sentry"
  "github.com/gin-gonic/gin"
)

func init() {
  raven.SetDSN("https://<key>:<secret>@app.getsentry.com/<project>")
}

func main() {
  r := gin.Default()
  r.Use(sentry.Recovery(raven.DefaultClient, false))
  // ...
  r.Run(":8080")
}
```
