// Copyright 2018 Microsoft Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package repo

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strings"
)

// WorkingTree encapsulates a git repository.
type WorkingTree struct {
	dir string
}

// Get returns a WorkingTree for the specified directory.  If the directory is not the
// root of a git repository the directory hierarchy is walked to find the root (i.e. the
// directory where the .git dir resides).
func Get(dir string) (wt WorkingTree, err error) {
	orig := dir
	for found := false; !found; {
		var fi []os.FileInfo
		fi, err = ioutil.ReadDir(dir)
		if err != nil {
			return
		}
		// look for the .git directory
		for _, f := range fi {
			if f.Name() == ".git" {
				found = true
				break
			}
		}
		if !found {
			// not the root of the repo, move to parent directory
			i := strings.LastIndexByte(dir, os.PathSeparator)
			if i < 0 {
				err = fmt.Errorf("failed to find repo root under '%s'", orig)
				return
			}
			dir = dir[:i]
		}
	}
	wt.dir = dir
	return
}

// Clone calls "git clone", cloning the working tree into the specified directory.
// The returned WorkingTree points to the clone of the repository.
func (wt WorkingTree) Clone(dest string) (result WorkingTree, err error) {
	cmd := exec.Command("git", "clone", fmt.Sprintf("file://%s", wt.dir), dest)
	output, err := cmd.CombinedOutput()
	if err != nil {
		err = errors.New(string(output))
		return
	}
	result.dir = dest
	return
}

// Checkout calls "git checkout" with the specified hash.
func (wt WorkingTree) Checkout(hash string) error {
	cmd := exec.Command("git", "checkout", hash)
	cmd.Dir = wt.dir
	output, err := cmd.CombinedOutput()
	if err != nil {
		return errors.New(string(output))
	}
	return nil
}

// Root returns the root directory of the working tree.
func (wt WorkingTree) Root() string {
	return wt.dir
}
