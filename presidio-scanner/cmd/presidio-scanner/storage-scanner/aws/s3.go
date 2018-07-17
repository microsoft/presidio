package aws

import (
	"log"
	"os"

	"github.com/presid-io/stow"

	"github.com/presid-io/presidio/pkg/storage"
)

// InitS3 inits the storage with the supplied credentials
func InitS3() (stow.ConfigMap, string) {
	s3AccessKeyID := os.Getenv("S3_ACCESS_KEY_ID")
	s3SecretKey := os.Getenv("S3_SECRET_KEY")
	s3Region := os.Getenv("S3_REGION")
	s3Bucket := os.Getenv("S3_BUCKET")
	if s3AccessKeyID == "" || s3SecretKey == "" || s3Region == "" || s3Bucket == "" {
		log.Fatal("S3_ACCESS_KEY_ID, S3_SECRET_KEY, S3_REGION, S3_BUCKET env vars must me set.")
	}
	_, config := storage.CreateS3Config(s3AccessKeyID, s3SecretKey, s3Region)
	return config, s3Bucket
}
