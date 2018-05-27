/*
Package google provides an abstraction of Google Cloud Storage. In this package, a Google Cloud Storage Bucket is represented by a Stow Container and a Google Cloud Storage Object is represented by a Stow Item. Note that directories may exist within a Bucket.

Usage and Credentials

A path to the JSON file representing configuration information for the service account is needed, as well as the Project ID that it is tied to.

stow.Dial requires both a string value of the particular Stow Location Kind ("google") and a stow.Config instance. The stow.Config instance requires two entries with the specific key value attributes:

- a key of google.ConfigJSON with a value of the path of the JSON configuration file
- a key of google.ConfigProjectID with a value of the Project ID

Location

There are google.location methods which allow the retrieval of a Google Cloud Storage Object (Container or Containers). An Object can also be retrieved based on the its URL (ItemByURL).

Additional google.location methods provide capabilities to create and remove Google Cloud Storage Buckets (CreateContainer or RemoveContainer).

Container

Methods of stow.container allow the retrieval of a Google Bucket's:

- name(ID or Name)
- object or complete list of objects (Item or Items, respectively)

Additional methods of google.container allow Stow to:

- remove an Object (RemoveItem)
- update or create an Object (Put)

Item

Methods of google.Item allow the retrieval of a Google Cloud Storage Object's:
- name (ID or name)
- URL
- size in bytes
- Object specific metadata (information stored within the Google Cloud Service)
- last modified date
- Etag
- content
*/
package google
