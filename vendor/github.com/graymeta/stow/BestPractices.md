# Best practices

## Configuring Stow once

It is recommended that you create a single file that imports Stow and all the implementations to save you from doing so in every code file where you might use Stow. You can also take the opportunity to abstract the top level Stow methods that your code uses to save other code files (including other packages) from importing Stow at all.

Create a file called `storage.go` in your package and add the following code:

```go
import (
	"github.com/graymeta/stow"
	// support Azure storage
	_ "github.com/graymeta/stow/azure"
	// support Google storage
	_ "github.com/graymeta/stow/google"
	// support local storage
	_ "github.com/graymeta/stow/local"
	// support swift storage
	_ "github.com/graymeta/stow/swift"
	// support s3 storage
	_ "github.com/graymeta/stow/s3"
	// support oracle storage
	_ "github.com/graymeta/stow/oracle"
)

// Dial dials stow storage.
// See stow.Dial for more information.
func Dial(kind string, config stow.Config) (stow.Location, error) {
	return stow.Dial(kind, config)
}
```
