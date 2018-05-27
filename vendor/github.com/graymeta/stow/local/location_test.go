package local_test

import (
	"fmt"
	"path/filepath"
	"testing"

	"github.com/cheekybits/is"
	"github.com/graymeta/stow"
	"github.com/graymeta/stow/local"
)

func TestContainers(t *testing.T) {
	is := is.New(t)
	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()

	cfg := stow.ConfigMap{"path": testDir}

	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	items, cursor, err := l.Containers("", stow.CursorStart, 10)
	is.NoErr(err)
	is.Equal(cursor, "")
	is.OK(items)

	is.Equal(len(items), 5)
	isDir(is, items[0].ID())
	is.Equal(items[0].Name(), "All")
	isDir(is, items[1].ID())
	is.Equal(items[1].Name(), "one")
	isDir(is, items[2].ID())
	is.Equal(items[2].Name(), "three")
	isDir(is, items[3].ID())
	is.Equal(items[3].Name(), "two")
}

func TestAllContainer(t *testing.T) {
	is := is.New(t)

	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()

	cfg := stow.ConfigMap{"path": testDir}

	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	containers, cursor, err := l.Containers("", stow.CursorStart, 10)
	is.NoErr(err)
	is.Equal(cursor, "")
	is.OK(containers)

	is.Equal(containers[0].Name(), "All")

	items, cursor, err := containers[0].Items("root", stow.CursorStart, 10)
	is.Equal(cursor, "")
	is.OK(items)
	is.NoErr(err)
	is.Equal(len(items), 1)
}

func TestContainersPrefix(t *testing.T) {
	is := is.New(t)
	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()

	cfg := stow.ConfigMap{"path": testDir}

	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	containers, cursor, err := l.Containers("t", stow.CursorStart, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(cursor, "")

	is.Equal(len(containers), 2)
	isDir(is, containers[0].ID())
	is.Equal(containers[0].Name(), "three")
	isDir(is, containers[1].ID())
	is.Equal(containers[1].Name(), "two")

	cthree, err := l.Container(containers[0].ID())
	is.NoErr(err)
	is.Equal(cthree.Name(), "three")
}

func TestContainer(t *testing.T) {
	is := is.New(t)
	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()

	cfg := stow.ConfigMap{"path": testDir}

	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	containers, cursor, err := l.Containers("t", stow.CursorStart, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(cursor, "")

	is.Equal(len(containers), 2)
	isDir(is, containers[0].ID())

	cthree, err := l.Container(containers[0].ID())
	is.NoErr(err)
	is.Equal(cthree.Name(), "three")

}

func TestCreateContainer(t *testing.T) {
	is := is.New(t)
	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()

	cfg := stow.ConfigMap{"path": testDir}

	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	c, err := l.CreateContainer("new_test_container")
	is.NoErr(err)
	is.OK(c)
	is.Equal(c.ID(), filepath.Join(testDir, "new_test_container"))
	is.Equal(c.Name(), "new_test_container")

	containers, cursor, err := l.Containers("new", stow.CursorStart, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(cursor, "")

	is.Equal(len(containers), 1)
	isDir(is, containers[0].ID())
	is.Equal(containers[0].Name(), "new_test_container")
}

func TestByURL(t *testing.T) {
	is := is.New(t)
	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()

	cfg := stow.ConfigMap{"path": testDir}

	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	containers, cursor, err := l.Containers("t", stow.CursorStart, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(cursor, "")

	three, err := l.Container(containers[0].ID())
	is.NoErr(err)
	items, cursor, err := three.Items("", stow.CursorStart, 10)
	is.NoErr(err)
	is.OK(items)
	is.Equal(cursor, "")
	is.Equal(len(items), 3)

	item1 := items[0]

	// make sure we know the kind by URL
	kind, err := stow.KindByURL(item1.URL())
	is.NoErr(err)
	is.Equal(kind, local.Kind)

	i, err := l.ItemByURL(item1.URL())
	is.NoErr(err)
	is.OK(i)
	is.Equal(i.ID(), item1.ID())
	is.Equal(i.Name(), item1.Name())
	is.Equal(i.URL().String(), item1.URL().String())

}

func TestContainersPaging(t *testing.T) {
	is := is.New(t)
	testDir, teardown, err := setup()
	is.NoErr(err)
	defer teardown()
	cfg := stow.ConfigMap{"path": testDir}
	l, err := stow.Dial(local.Kind, cfg)
	is.NoErr(err)
	is.OK(l)

	for i := 0; i < 25; i++ {
		_, err := l.CreateContainer(fmt.Sprintf("container-%02d", i))
		is.NoErr(err)
	}

	// get the first page
	containers, cursor, err := l.Containers("container-", stow.CursorStart, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(len(containers), 10)
	is.OK(cursor)
	is.Equal(filepath.Base(cursor), "container-10")

	// get next page
	containers, cursor, err = l.Containers("container-", cursor, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(len(containers), 10)
	is.OK(cursor)
	is.Equal(filepath.Base(cursor), "container-20")

	// get last page
	containers, cursor, err = l.Containers("container-", cursor, 10)
	is.NoErr(err)
	is.OK(containers)
	is.Equal(len(containers), 5)
	is.True(stow.IsCursorEnd(cursor))

	// bad cursor
	_, _, err = l.Containers("container-", "made-up-cursor", 10)
	is.Equal(err, stow.ErrBadCursor)

}
