/*
Package s3 provides an abstraction of Amazon S3 (Simple Storage Service). An S3 Bucket is a Stow Container and an S3 Object is a Stow Item. Recall that nested directories exist within S3.

Usage and Credentials

There are three separate pieces of information required by Stow to have access to an S3 Stow Location: an AWS User's ACCESS_KEY_ID and SECRET_KEY fields, as well as the physical region of the S3 Endpoint. Ensure that the AWS User whose credentials are used to manipulate the S3 endpoint has permissions to do so.

stow.Dial requires both a string value ("s3") of the particular Stow Location Kind and a stow.Config instance. The stow.Config instance requires three entries with the specific key value attributes:

- a key of s3.ConfigAccessKeyID with a value of the AWS account's Access Key ID
- a key of s3.ConfigSecretKey with a value of the AWS account's Secret Key
- a key of s3.ConfigRegion with a value of the S3 endpoint's region (in all lowercase)

Location

The s3.location methods allow the retrieval of an S3 endpoint's Bucket or list of Buckets (Container or Containers). A stow.Item representation of an S3 Object can also be retrieved based on the Object's URL (ItemByURL).

Additional s3.location methods provide capabilities to create and remove S3 Buckets (CreateContainer or RemoveContainer, respectively).

Container

There are s3.container methods which can retrieve an S3 Bucket's:

- name (ID or Name)
- Object or complete list of Objects (Item or Items)
- region

Additional s3.container methods give Stow the ability to:

- remove an S3 Bucket (RemoveItem)
- update or create an S3 Object (Put)

Item

Methods within an s3.item allow the retrieval of an S3 Object's:
- name (ID or name)
- URL (ItemByUrl)
- size in bytes (Size)
- S3 specific metadata (Metadata, key value pairs usually found within the console)
- last modified date (LastMod)
- Etag (Etag)
- content (Open)
*/
package s3
