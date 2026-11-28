package main

import (
	"fmt"
	"os"
)

func showError(s string) { fmt.Fprintln(os.Stderr, s) }
func launch() error      { return fmt.Errorf("La interfaz requiere Windows; usa --iso/--dlc/--salida") }
