package tools

import (
	"image"
	"sync"
	"time"

	"github.com/disintegration/gift"
	"github.com/nfnt/resize"
)

func processImage(img image.Image) image.Image {
	// Redimensionar imagem
	bounds := img.Bounds()
	resizedImg := resizeImage(img, uint(bounds.Dx()*2), uint(bounds.Dy()*2))
	time.Sleep(1 * time.Second)

	// Aplicar filtro de desfoque
	blurredImg := applyBlurFilter(resizedImg)

	return blurredImg
}

func ProcessImagesWithConcurrency(images []image.Image) []image.Image {
	currentTime := time.Now()
	var wg sync.WaitGroup
	result := make([]image.Image, len(images))
	ch := make(chan struct {
		index int
		img   image.Image
	})

	for i, img := range images {
		wg.Add(1)
		go func(i int, img image.Image) {
			defer wg.Done()
			processedImg := processImage(img)
			ch <- struct {
				index int
				img   image.Image
			}{i, processedImg}
		}(i, img)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	for res := range ch {
		result[res.index] = res.img
	}

	elapsed := time.Since(currentTime).Seconds()
	println("Processing took using goroutine", elapsed)

	return result
}

func ProcessImages(images []image.Image) []image.Image {
	currentTime := time.Now()

	result := make([]image.Image, len(images))

	for i, img := range images {

		processedImg := processImage(img)
		result[i] = processedImg

	}

	elapsed := time.Since(currentTime).Seconds()
	println("Processing took", elapsed)

	return result
}

// Redimensionar imagem
func resizeImage(img image.Image, width uint, height uint) image.Image {
	return resize.Resize(width, height, img, resize.Lanczos3)
}

// Aplicar filtro de desfoque
func applyBlurFilter(img image.Image) image.Image {
	g := gift.New(
		//	gift.GaussianBlur(3.0),
		gift.Contrast(30),
	)
	dst := image.NewRGBA(g.Bounds(img.Bounds()))
	g.Draw(dst, img)
	return dst
}
