/*
Package swift provides an absraction of the Openstack Swift storage technology. An Openstack Swift Container is represented by a Stow Container, and an Openstack Swift Object is represented by a Stow Item. Note that directories may exist within a Swift Container.

Usage and Credentials

Four pieces of information are needed: the user's name and password which will be used to access the Swift endpoint, the tenant name used to identify the storage endpoint, and the authentication URL.

stow.Dial requires both a string value of the particular Stow Location Kind ("swift") and a stow.Config instance. The stow.Config instance requires two entries with the specific key value attributes:

- a key of swift.ConfigUsername with a value of the user account name
- a key of swift.ConfigKey with a value of the user account password
- a key of swift.ConfigTenantName with a value of the Swift endpoint's tenant name
- a key of swift.ConfigTenantAuthURL with a value of the Swift endpoint's authentication URL

Location

Methods of swift.location allow the retrieval of a Swift Container (Container or Containers). A stow.Item representation of a Swift Object can also be retrieved based on the Object's URL (ItemByURL).

Additional swift.location methods provide capabilities to create and remove Swift Containers (CreateContainer or RemoveContainer).

Container

Methods of stow.container allow the retrieval of a Swift Container's:

- name(ID or Name)
- item or complete list of items (Item or Items, respectively)

Additional methods of swift.container allow Stow to:

- remove a stow.Item (RemoveItem)
- update or create a stow.Item (Put)

Item

Methods of swift.Item allow the retrieval of a Swift Object's:
- name (ID or name)
- URL
- size in bytes
- Object specific metadata (information stored within the service)
- last modified date
- Etag
- content
*/
package swift
