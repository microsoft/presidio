package aws

import (
	"log"

	"github.com/presid-io/stow"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/storage"
)

// InitS3 inits the storage with the supplied credentials
func InitS3(inputConfig *message_types.InputConfig) (stow.ConfigMap, string) {
	s3AccessKeyID := inputConfig.S3Config.GetAccessId()
	s3SecretKey := inputConfig.S3Config.GetAccessKey()
	s3Region := inputConfig.S3Config.GetRegion()
	s3Bucket := inputConfig.S3Config.GetBucketName()
	if s3AccessKeyID == "" || s3SecretKey == "" || s3Region == "" || s3Bucket == "" {
		log.Fatal("accessId, accessKey, region, bucket must me set for s3 storage kind.")
	}
	_, config := storage.CreateS3Config(s3AccessKeyID, s3SecretKey, s3Region)
	return config, s3Bucket
}
