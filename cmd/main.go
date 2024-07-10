package main

import (
	"fmt"
	"log"
	"time"

	"github.com/ThainaJardim/img-tools/pkg/tools"
)

func main() {
	currentTime := time.Now()

	images, err := tools.LoadImagesFromDir("./imagess")
	if err != nil {
		log.Fatalf("failed to load images: %v", err)
	}

	processedImages := tools.ProcessImages(images)

	if err := tools.SaveProcessedImages(processedImages, "output_images"); err != nil {
		log.Fatalf("Failed to save images: %v", err)
	}
	// in seconds
	log.Printf("Processing took %v", time.Since(currentTime))

	fmt.Println("Processing completed!")
}
