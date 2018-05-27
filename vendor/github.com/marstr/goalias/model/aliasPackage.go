package model

import (
	"errors"
	"fmt"
	"go/ast"
	"go/token"
	"regexp"
	"strings"

	"github.com/marstr/collection"
)

type AliasPackage ast.Package

type ErrorUnexpectedToken struct {
	Expected token.Token
	Received token.Token
}

var errUnexpectedNil = errors.New("unexpected nil")

func (utoken ErrorUnexpectedToken) Error() string {
	return fmt.Sprintf("Unexpected token %d expecting type: %d", utoken.Received, utoken.Expected)
}

const modelFile = "models.go"
const origImportAlias = "original"

// ModelFile is a getter for the file accumulating aliased content.
func (alias AliasPackage) ModelFile() (result *ast.File) {
	if alias.Files != nil {
		result = alias.Files[modelFile]
	}
	return
}

// SetModelFile is a setter for the file accumulating aliased content.
func (alias *AliasPackage) SetModelFile(val *ast.File) {
	if alias.Files == nil {
		alias.Files = make(map[string]*ast.File)
	}

	alias.Files[modelFile] = val
}

// NewAliasPackage stuff and things
func NewAliasPackage(original *ast.Package, originalLocation string) (alias *AliasPackage, err error) {
	ast.PackageExports(original)
	for k := range original.Files {
		if matched, _ := regexp.MatchString("_test.go$", k); matched {
			delete(original.Files, k)
		}
	}

	originalLocation = strings.Replace(originalLocation, `\`, "/", -1)

	models := &ast.File{
		Name: &ast.Ident{
			Name:    original.Name,
			NamePos: token.Pos(len("package") + 2),
		},
		Package: 1,
	}

	alias = &AliasPackage{
		Name: original.Name,
		Files: map[string]*ast.File{
			modelFile: models,
		},
	}

	models.Decls = append(models.Decls, &ast.GenDecl{
		Tok: token.IMPORT,
		Specs: []ast.Spec{
			&ast.ImportSpec{
				Name: &ast.Ident{
					Name: origImportAlias,
				},
				Path: &ast.BasicLit{
					Kind:  token.STRING,
					Value: fmt.Sprintf("\"%s\"", originalLocation),
				},
			},
		},
	})

	var walker collection.Enumerable = PackageWalker{target: original}

	walker = collection.Where(walker, func(x interface{}) (ok bool) {
		ok = x != nil
		return
	})

	generalDecls := collection.Where(walker, func(x interface{}) (ok bool) {
		_, ok = x.(*ast.GenDecl)
		return
	})

	for item := range generalDecls.Enumerate(nil) {
		alias.AddGeneral(item.(*ast.GenDecl))
	}

	funcDecls := collection.Where(walker, func(x interface{}) (ok bool) {
		_, ok = x.(*ast.FuncDecl)
		return
	})

	funcDecls = collection.Where(funcDecls, func(x interface{}) (ok bool) {
		cast, ok := x.(*ast.FuncDecl)
		if !ok {
			return
		}

		if cast.Recv == nil {
			ok = true
			return
		}

		ok = len(cast.Recv.List) == 0
		return
	})

	for item := range funcDecls.Enumerate(nil) {
		alias.AddFunc(item.(*ast.FuncDecl))
	}

	return
}

// AddGeneral handles dispatching a GenDecl to either AddConst or AddType.
func (alias *AliasPackage) AddGeneral(decl *ast.GenDecl) error {
	var adder func(*ast.GenDecl) error

	switch decl.Tok {
	case token.CONST:
		adder = alias.AddConst
	case token.TYPE:
		adder = alias.AddType
	default:
		adder = func(item *ast.GenDecl) (result error) {
			result = fmt.Errorf("Unusable token: %v", item.Tok)
			return
		}
	}

	return adder(decl)
}

// AddConst adds a Const block with indiviual aliases for each Spec in `decl`.
func (alias *AliasPackage) AddConst(decl *ast.GenDecl) (err error) {
	if decl == nil {
		err = errors.New("unexpected nil")
		return
	} else if decl.Tok != token.CONST {
		err = ErrorUnexpectedToken{Expected: token.CONST, Received: decl.Tok}
		return
	}

	targetFile := alias.ModelFile()

	for _, spec := range decl.Specs {
		cast := spec.(*ast.ValueSpec)
		for j, name := range cast.Names {
			cast.Values[j] = &ast.SelectorExpr{
				X: &ast.Ident{
					Name: origImportAlias,
				},
				Sel: &ast.Ident{
					Name: name.Name,
				},
			}
		}
	}

	targetFile.Decls = append(targetFile.Decls, decl)

	return
}

// AddType adds a Type delcaration block with individual alias for each Spec handed in `decl`
func (alias *AliasPackage) AddType(decl *ast.GenDecl) (err error) {
	if decl == nil {
		err = errUnexpectedNil
		return
	} else if decl.Tok != token.TYPE {
		err = ErrorUnexpectedToken{Expected: token.TYPE, Received: decl.Tok}
		return
	}

	targetFile := alias.ModelFile()

	for _, spec := range decl.Specs {
		cast := spec.(*ast.TypeSpec)
		cast.Assign = 1
		cast.Type = &ast.SelectorExpr{
			X: &ast.Ident{
				Name: origImportAlias,
			},
			Sel: &ast.Ident{
				Name: cast.Name.Name,
			},
		}
	}

	targetFile.Decls = append(targetFile.Decls, decl)
	return
}

// AddFunc creates a stub method to redirect the call to the original package, then adds it to the model file.
func (alias *AliasPackage) AddFunc(decl *ast.FuncDecl) (err error) {

	if decl == nil {
		err = errUnexpectedNil
		return
	}

	paramNames := collection.AsEnumerable(decl.Type.Params.List)
	paramNames = collection.SelectMany(paramNames, func(x interface{}) collection.Enumerator {
		return collection.AsEnumerable(x.(*ast.Field).Names).Enumerate(nil)
	})

	arguments := []ast.Expr{}

	for n := range paramNames.Enumerate(nil) {
		arguments = append(arguments, n.(*ast.Ident))
	}

	decl.Body = &ast.BlockStmt{
		List: []ast.Stmt{
			&ast.ReturnStmt{
				Results: []ast.Expr{
					&ast.CallExpr{
						Fun: &ast.SelectorExpr{
							X: &ast.Ident{
								Name: origImportAlias,
							},
							Sel: &ast.Ident{
								Name: decl.Name.Name,
							},
						},
						Args: arguments,
					},
				},
			},
		},
	}

	targetFile := alias.ModelFile()

	targetFile.Decls = append(targetFile.Decls, decl)

	return
}
