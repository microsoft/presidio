# Google Cloud Storage Stow Implementation

Location = Google Cloud Storage

Container = Bucket

Item = File

## How to access underlying service types

Use a type conversion to extract the underlying `Location`, `Container`, or `Item` implementations. Then use the Google-specific getters to access the internal Google Cloud Storage `Service`, `Bucket`, and `Object` values.

```go
import (
  "log"
  "github.com/graymeta/stow"
  stowgs "github.com/graymeta/stow/google"
)

stowLoc, err := stow.Dial(stowgs.Kind, stow.ConfigMap{
	stowgs.ConfigJSON:      "<json config>",
	stowgs.ConfigProjectId: "<project id>",
})
if err != nil {
  log.Fatal(err)
}

stowBucket, err = stowLoc.Container("mybucket")
if err != nil {
  log.Fatal(err)
}

if gsBucket, ok := stowBucket.(*stowgs.Bucket); ok {
  if gsLoc, ok := stowLoc.(*stowgs.Location); ok {

    googleService := gsLoc.Service()
    googleBucket, err := gsBucket.Bucket()

    // < Send platform-specific commands here >

  }
}
```

By default, Stow uses `https://www.googleapis.com/auth/devstorage.read_write` scope. Different scopes can be used by passing a comma separated list of scopes, like below:
```go
stowLoc, err := stow.Dial(stowgs.Kind, stow.ConfigMap{
	stowgs.ConfigJSON:      "<json config>",
	stowgs.ConfigProjectId: "<project id>",
	stowgs.ConfigScopes:    "<scope_1>,<scope_2>",
})
```

---

Configuration... You need to create a project in google, and then create a service account in google tied to that project. You will need to download a `.json` file with the configuration for the service account. To run the test suite, the service account will need edit privileges inside the project.

To run the test suite, set the `GOOGLE_CREDENTIALS_FILE` environment variable to point to the location of the .json file containing the service account credentials and set `GOOGLE_PROJECT_ID` to the project ID, otherwise the test suite will not be run.

---

Concerns:

- Google's storage plaform is more _eventually consistent_ than other platforms. Sometimes, the tests appear to be flaky because of this. One example is when deleting files from a bucket, then immediately deleting the bucket...sometimes the bucket delete will fail saying that the bucket isn't empty simply because the file delete messages haven't propagated through Google's infrastructure. We may need to add some delay into the test suite to account for this.
