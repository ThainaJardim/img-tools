package tools

import (
	"fmt"
	"image"
	"image/jpeg"
	"image/png"
	"os"
	"path/filepath"
)

// Load any type of images from a directory
func loadImage(path string) (image.Image, error) {
	img, err := decodeImg(path)
	if err != nil {
		return nil, err
	}
	return img, nil
}

func decodeImg(path string) (image.Image, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}

	defer file.Close()

	ext := filepath.Ext(path)
	switch ext {
	case ".jpg", ".jpe":
		img, err := jpeg.Decode(file)
		if err != nil {
			return nil, err
		}
		return img, nil
	case ".png":
		img, err := png.Decode(file)
		if err != nil {
			return nil, err
		}
		return img, nil
	default:
		return nil, fmt.Errorf("unsupported image format: %s", ext)
	}
}

func LoadImagesFromDir(dir string) ([]image.Image, error) {
	var images []image.Image
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			img, err := loadImage(path)
			if err != nil {
				return err
			}
			images = append(images, img)
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	return images, nil
}
