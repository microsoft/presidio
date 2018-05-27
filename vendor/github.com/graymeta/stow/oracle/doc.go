/*
Package Oracle provides an absraction of the Oracle Storage Cloud Service. In this package, an Oracle Service Instance of type Storage is represented by a Stow Container, and an Oracle Storage Object is represented by a Stow Item.

Oracle Storage Cloud Service is strictly a blob storage service, therefore nested directories do not exist.

Usage and Credentials

The most important detail in accessing the service is the authorization endpoint of the Service Instance. This URL can be found in the Overview page of the Instance, and is the value which corresponds to the "Service REST endpoint" field.

The remaining two parts of information needed are the user name and password of the account which will be used to manipulate the service. Ensure that the AWS User whose credentials are used to manipulate service has permissions to do so.

stow.Dial requires both a string value of the particular Stow Location Kind ("oracle") and a stow.Config instance. The stow.Config instance requires two entries with the specific key value attributes:

- a key of oracle.ConfigUsername with a value of the account user name
- a key of oracle.ConfigPassword with a value of the account pasword
- a key of oracle.AuthEndpoint with a value of the authorization endpoint

Location

Methods of oracle.location allow the retrieval of an Oracle Cloud Service Storage Instance (Container or Containers). A stow.Item representation of an Oracle Object can also be retrieved based on the Object's URL (ItemByURL).

Additional oracle.location methods provide capabilities to create and remove Storage Service Instances (CreateContainer or RemoveContainer, respectively).

Container

Methods of an oracle.container allow the retrieval of a Storage Service Instance's:

- name(ID or Name)
- item or complete list of items (Item or Items, respectively)

Additional methods of an oracle.container allow Stow to:

- remove an Object (RemoveItem)
- update or create an Object (Put)

Item

Methods of oracle.Item allow the retrieval of a Storage Service Instance's:
- name (ID or name)
- URL
- size in bytes
- Oracle Storage Object specific metadata (information stored within Oracle Cloud Service)
- last modified date
- Etag
- content
*/
package swift
