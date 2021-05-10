For now, in order to generate the sdk files for CSharp, we are going to do it manually (until the pipeline is ready).
To do so, on each change in api-docs.yml file, we are required to run the following command from presidio/docs/docs-api folder:
```
openapi-generator generate -i api-docs.yml -o ../../sdk/csharp/ --additional-properties netCoreProjectFile=true,targetFramework=netcoreapp3.1,legacyDiscriminatorBehavior=false -g csharp-netcore -c ../../sdk/csharp/config.json
```

