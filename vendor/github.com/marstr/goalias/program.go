package main

import (
	"flag"
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"io"
	"os"

	"github.com/marstr/collection"
	"github.com/marstr/goalias/model"
)

var (
	output  io.Writer
	subject *ast.Package
)

func main() {
	var err error
	exitStatus := 1
	defer func() {
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(exitStatus)
		}
	}()

	aliased, err := model.NewAliasPackage(subject)
	if err != nil {
		return
	}

	var files token.FileSet

	err = format.Node(output, &files, aliased.ModelFile())
	// err = printer.Fprint(output, &files, aliased.ModelFile())
	if err != nil {
		return
	}
}

func init() {
	var outputLocation string
	var originalNamespace string
	var inputLocation string

	const defaultNamespace = "<input location>"

	flag.StringVar(&outputLocation, "o", "", "The name of the output file that should be generated.")
	flag.StringVar(&originalNamespace, "n", defaultNamespace, "The path that should be used to import the original package.")
	flag.Parse()

	arg, err := collection.Single(collection.AsEnumerable(flag.Args()))
	if err != nil {
		os.Exit(1)
		return
	}

	if outputLocation == "" {
		output = os.Stdout
	} else {
		var err error
		output, err = os.Create(outputLocation)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}

	var files token.FileSet

	const selectedMode = parser.ParseComments

	var fauxPackage ast.Package
	fauxPackage.Name = "faux"
	fauxPackage.Files = make(map[string]*ast.File)

	if inputLocation == "" {
		const filename = "source.go"
		source, err := parser.ParseFile(&files, filename, os.Stdin, selectedMode)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fauxPackage.Files[filename] = source
		subject = &fauxPackage
	} else if inputInfo, err := os.Stat(inputLocation); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	} else if inputInfo.IsDir() {
		packages, err := parser.ParseDir(&files, inputLocation, nil, selectedMode)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}

		for _, v := range packages {
			subject = v
			break
		}
	} else {
		source, err := parser.ParseFile(&files, inputLocation, nil, selectedMode)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fauxPackage.Files[inputLocation] = source
		subject = &fauxPackage
	}

}
