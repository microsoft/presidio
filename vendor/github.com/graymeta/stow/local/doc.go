/*
Package local provides an abstraction of a general filesystem. A Stow Container is a directory, and a Stow Item is a file.

Credentials

The only information required in accessing a filesystem via Stow is the path of a directory.

Usage

Aside from providing stow.Dial with the correct Kind ("local"), a stow.Config instance is needed. This instance requires an entry with a key of stow.ConfigKeyPath and a value of the path of the directory.

Location

There are local.location methods which allow the retrieval of one or more directories (Container or Containers). A stow.Item representation of a file can also be achieved (ItemByURL).

Additional methods provide capabilities to create and remove directories (CreateContainer, RemoveContainer).

Container

Of a directory, methods of local.container allow the retrieval of its name (ID or Name) as well as one or more files (Item or Items) that exist within.

Additional local.container methods allow the removal of a file (RemoveItem) and the creation of one (Put).

Item

Methods of local.Item allow the retrieval of quite detailed information. They are:
- full path (ID)
- base file name (Name)
- size in bytes (Size)
- file metadata (path, inode, directory, permission bits, etc)
- last modified date (ETag for string, LastMod for time.Time)
- content (Open)
*/
package local
