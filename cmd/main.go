package main

import (
	"fmt"
	"log"
	"time"

	"github.com/ThainaJardim/img-tools/pkg/tools"
)

func main() {
	currentTime := time.Now()

	images, err := tools.LoadImagesFromDir("./images")
	if err != nil {
		log.Fatalf("failed to load images: %v", err)
	}

	processedImages := tools.ProcessImages(images)

	if err := tools.SaveProcessedImages(processedImages, "output_images"); err != nil {
		log.Fatalf("failed to save images: %v", err)
	}
	// in seconds
	log.Printf("processing took %v", time.Since(currentTime))

	fmt.Println("processing completed!")
}
