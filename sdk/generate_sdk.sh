echo "Downloading openapi generator jar version 5.1.0"
curl https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/5.1.0/openapi-generator-cli-5.1.0.jar -o openapi-generator-cli-5.1.0.jar
echo "Generating C# SDK with .net core 3.1"
java -jar openapi-generator-cli-5.1.0.jar generate -i ../docs/api-docs/api-docs.yml -o csharp/ --additional-properties netCoreProjectFile=true,targetFramework=netcoreapp3.1,legacyDiscriminatorBehavior=false -g csharp-netcore -c csharp/config.json



