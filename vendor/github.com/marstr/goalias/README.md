# goalias
## Overview
This rather bizarre program will scour a Go package for all publicly exported entities then create a package that merely delegates the work to the original package. For example, consider the following program:

``` Go
// +build go1.7
package example

import (
	"net/http"
)

// Foo is a useless const in the scheme of things
const Foo = "item"

// B is a mock type just for the sake of adding a type to const declarations
type B string

// Contents of this block shouldn't really be used for anything
const (
	Bar B = "bar"
	Baz B = "baz"
)

// Contents of this block should also be ignored
const (
	Bak B = http.MethodGet
)
```

Running goalias over it would produce the following:

``` Go
// +build go1.9
package example

import (
    original "github.com/marstr/goalias/testdata/example"
)

const Foo = original.Foo

type B = original.B

const (
    Bar B = original.Bar
    Baz B = original.Baz
)

const (
    Bak B = original.Bak
)
```
## Motivation

Why would we want such a program? For starters, there is the trivial justification of wanting to rename a package without breaking people who still target the old name. This would saferly allow for that.

However, over on the [Azure/azure-sdk-for-go](https://github.com/Azure/azure-sdk-for-go), we ran into a far more interesting scenario. For better or worse, we wanted to allow for folks to use the latest version of the SDK to target any API Version of any service. This leads to a large matrix of packages that do more or less the same thing, and a little confusion for folks while writing import statements. To allow for more readable documentation, and quicker identification of which packages will be supported in which environments, Azure & Azure Stack are adding a concept of "Profiles". ([More loosely related reading about that here](https://docs.microsoft.com/en-us/azure/azure-stack/azure-stack-version-profiles)). Profiles create an interesting situation, where we basically want to expose exactly the same code through different namespaces.

To allow for duplicating types across namespaces, [go1.9's introduction of alias types](https://tip.golang.org/doc/go1.9#language) helped out tremendously. This allows for multiple symbols to target a single identity. There won't need to be any casting or composition while passing between identical API Versions, _alias types are just the same as the original_.

However, in addition to types, there are a lot of other top-level items that reside in a package.To fully replace an import statement, we need to replicate all of those items. `const` delcarations are trivial, as we just map the original declaration to a `const` in the new package of the same name. `func` declarations are also relatively easy, we can simply create a function in the new package that targets the orignal function. These functions should be inlined, so they will be invisible at runtime. Because Go is a functional language there are other options here, but I won't get into that now!

Lastly, we're left with global variables. These are somewhat troublesome, as unlike all of the previously mentioned types, they're mutable. The safest way to deal with them would be to create pointers to the original with the same name. However, this would represent this tool's first departure from truly identical types. At the moment of writing this README, I haven't implemented support for global variables so that I can defer that decision. My recommendation is to skip global variables anyway, they smell bad.


