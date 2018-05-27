/*
Package azure provides an abstraction for the Microsoft Azure Storage service. In this package, an Azure Resource of type "Storage account" is represented by a Stow Location and an Azure blob is represented by a Stow Item.

Usage and Credentials

Two peices of information are needed to access an Azure Resorce of type "Storage account": the Resource Name (found in the "All Resources" tab of the Azure Portal console) and the Access Key (found in the "Access Keys" tab in the "Settings" pane of a Resource's details page).

stow.Dial requires both a string value of the particular Stow Location Kind ("azure") and a stow.Config instance. The stow.Config instance requires two entries with the specific key value attributes:

- a key of azure.ConfigAccount with a value of the Azure Resource Name
- a key of azure.ConfigKey with a value of the Azure Access Key

Location

There are azure.location methods which allow the retrieval of a single Azure Storage Service. A stow.Item representation of an Azure Storage Blob can also be retrieved based on the Object's URL (ItemByURL).

Additional azure.location methods provide capabilities to create and remove Azure Storage Containers.

Container

Methods of an azure.container allow the retrieval of an Azure Storage Container's:

- name (ID or Name)
- blob or complete list of blobs (Item or Items)

Additional azure.container methods allow Stow to :

- remove a Blob (RemoveItem)
- update or create a Blob (Put)

Item

Methods of azure.Item allow the retrieval of an Azure Storage Container's:
- name (ID or name)
- URL
- size in bytes
- Azure Storage blob specific metadata (information stored within the Azure Cloud Service)
- last modified date
- Etag
- content

Caveats

At this point in time, the upload limit of a blob is about 60MB. This is an implementation restraint.
*/
package azure
