<!-- Mirrored from https://docs.spacetraders.io/api-guide/open-api-spec -->

# OpenAPI Spec

The SpaceTraders API is documented using the OpenAPI Specification. This allows users to generate a client library for the API in many different languages. You can find the repository with our OpenAPI specification [here](https://github.com/SpaceTradersAPI/api-docs).

## OpenAPI specification

We provide access to our API documentation on our website itself at [https://spacetraders.io/openapi](https://spacetraders.io/openapi). This allows you to interact with the API directly from your browser and is synced with our OpenAPI specification.

## Generating a Client Library

The OpenAPI specification can be used to generate a client library for the SpaceTraders API in many different languages using the [OpenAPI Generator](https://openapi-generator.tech/)
.

The following is an example of generating a TypeScript client library using the [typescript-axios](https://openapi-generator.tech/docs/generators/typescript-axios) generator and the [bundled specification](https://spacetraders.io/SpaceTraders.json) from [Scalar](https://scalar.com/) (whose components we use).

The following `openapi-generator` was installed using homebrew, but you can find installation instructions for your platform [here](https://openapi-generator.tech/docs/installation).

```bash
openapi-generator generate \
 -i https://spacetraders.io/SpaceTraders.json \
 -o packages/spacetraders-sdk \
 -g typescript-axios \
 --additional-properties=npmName="spacetraders-sdk" \
 --additional-properties=npmVersion="2.3.0" \
 --additional-properties=supportsES6=true \
 --additional-properties=withSeparateModelsAndApi=true \
 --additional-properties=modelPackage="models" \
 --additional-properties=apiPackage="api"
```

> **Warning: Bundled References**
>
> Our specification file uses the $ref keyword in the source to reference other files when downloaded as source. This can cause issues with some OpenAPI generators.
>
> However, the [bundled specification](https://spacetraders.io/SpaceTraders.json) available from the website has all these references already resolved, so it shouldn't cause any issues.
