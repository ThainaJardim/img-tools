package tools

import (
	"fmt"
	"image"
	"image/jpeg"
	"os"
	"path/filepath"
)

func saveImage(img image.Image, path string) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	defer file.Close()

	fmt.Printf("saving image to %s\n", path)

	return jpeg.Encode(file, img, nil)
}

func SaveProcessedImages(images []image.Image, dir string) error {
	if err := os.MkdirAll(dir, os.ModePerm); err != nil {
		return err
	}
	for i, img := range images {
		path := filepath.Join(dir, fmt.Sprintf("processed_%d.jpg", i))
		if err := saveImage(img, path); err != nil {
			return err
		}
	}
	return nil
}
