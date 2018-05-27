# S3 Stow Implementation

Location = Amazon S3

Container = Bucket

Item = File

Helpful Links:

`http://docs.aws.amazon.com/sdk-for-go/api/service/s3/#example_S3_ListBuckets`

---

SDK Notes:

- Metadata of an S3 Object can only be set when the Object is created.

---

Concerns:

- An AWS account may have credentials which temporarily modifies permissions. This is specified by a token value. This feature is implemented but disabled and added as a TODO.

---

Things to know:

- Paging for the list of containers doesn't exist yet, this is because there's a hard limit of about 100 containers for every account.

- A client is required to provide a region. Manipulating buckets that reside within other regions isn't possible.

---

###### Dev Notes

The init function of every implementation of `stow` must call `stow.Register`.

`stow.Register` accepts a few things:

### Kind, a string argument respresenting the name of the location.

`makefn` a function that accepts any type that conforms to the stow.Config
interface. It first validates the values of the `Config` argument, and then
attempts to use the configuration to create a new client. If successful, An
instance of a data type that conforms to the `stow.Location` interface is
created. This Location should have fields that contain the client and
configuration.

Further calls in the hierarchy of a Location, Container, and Item depend
on the values of the configuration + the client to send and receive information.

- `kingmatchfn` a function that ensures that a given URL matches the `Kind` of the type of storage.

---

**stow.Register(kind string, makefn func(Config) (Locaion, error), kindmatchfn func(*url.URL) bool)**

- Adds `kind` and `makefn` into a map that contains a list of locations.

- Adds `kind` to a slice that contains all of the different kinds.

- Adds `kind` as part of an anonymous function which validates the scheme of the url.URL

Once the `stow.Register` function is completed, a location of the given kind is returned.

---
