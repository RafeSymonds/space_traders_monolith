<!-- Mirrored from https://docs.spacetraders.io/api-guide/response-errors -->

# Response Codes

The SpaceTraders API uses standard HTTP response codes to indicate the success or failure of an API request.

In general, codes in the `2xx` range indicate success, codes in the `4xx` range indicate an error that failed given the information provided (e.g., a required parameter was omitted), and codes in the `5xx` range indicate an error with the SpaceTraders servers.

The structure of an API error response contains an error key with code, message and data fields. The following is an example of an API error response:

```json
{
  "error": {
    "message": "Missing Bearer token in the request. Did you confirm sending the \"Bearer {token}\" as the authorization header?",
    "code": 4103,
    "data": {}
  }
}
```

> **Note: Work in progress**
>
> We are currently working on fully documenting all errors in our OpenAPI specification. In the meantime, you can find a list of error codes below.

## General Error Codes

This list is non-exhaustive. For the full list (we'll use that one here eventually), please see the [/error-codes](https://spacetraders.io/openapi#tag/global/GET/error-codes) endpoint in the OpenAPI specification.

```js
const cooldownConflictError = 4000
const waypointNoAccessError = 4001
```

## Account Error Codes

```js
const tokenEmptyError = 4100
const tokenMissingSubjectError = 4101
const tokenInvalidSubjectError = 4102
const missingTokenRequestError = 4103
const invalidTokenRequestError = 4104
const invalidTokenSubjectError = 4105
const accountNotExistsError = 4106
const agentNotExistsError = 4107
const accountHasNoAgentError = 4108
const registerAgentExistsError = 4109
const registerAgentSymbolReservedError = 4110
const registerAgentConflictSymbolError = 4111
```

## Ship Error Codes

```js
const navigateInTransitError = 4200
const navigateInvalidDestinationError = 4201
const navigateOutsideSystemError = 4202
const navigateInsufficientFuelError = 4203
const navigateSameDestinationError = 4204
const shipExtractInvalidWaypointError = 4205
const shipExtractPermissionError = 4206
const shipJumpNoSystemError = 4207
const shipJumpSameSystemError = 4208
const shipJumpMissingModuleError = 4210
const shipJumpNoValidWaypointError = 4211
const shipJumpMissingAntimatterError = 4212
const shipInTransitError = 4214
const shipMissingSensorArraysError = 4215
const purchaseShipCreditsError = 4216
const shipCargoExceedsLimitError = 4217
const shipCargoMissingError = 4218
const shipCargoUnitCountError = 4219
const shipSurveyVerificationError = 4220
const shipSurveyExpirationError = 4221
const shipSurveyWaypointTypeError = 4222
const shipSurveyOrbitError = 4223
const shipSurveyExhaustedError = 4224
const shipRefuelDockedError = 4225
const shipRefuelInvalidWaypointError = 4226
const shipMissingMountsError = 4227
const shipCargoFullError = 4228
const shipJumpFromGateToGateError = 4229
const waypointChartedError = 4230
const shipTransferShipNotFound = 4231
const shipTransferAgentConflict = 4232
const shipTransferSameShipConflict = 4233
const shipTransferLocationConflict = 4234
const warpInsideSystemError = 4235
const shipNotInOrbitError = 4236
const shipInvalidRefineryGoodError = 4237
const shipInvalidRefineryTypeError = 4238
const shipMissingRefineryError = 4239
const shipMissingSurveyorError = 4240
const shipMissingWarpDriveError = 4241
const shipMissingMineralProcessorError = 4242
const shipMissingMiningLasersError = 4243
const shipNotDockedError = 4244
const purchaseShipNotPresentError = 4245
const shipMountNoShipyardError = 4246
const shipMissingMountError = 4247
const shipMountInsufficientCreditsError = 4248
const shipMissingPowerError = 4249
const shipMissingSlotsError = 4250
const shipMissingMountsError = 4251
const shipMissingCrewError = 4252
const shipExtractDestabilizedError = 4253
const shipJumpInvalidOriginError = 4254
const shipJumpInvalidWaypointError = 4255
const shipJumpOriginUnderConstructionError = 4256
const shipMissingGasProcessorError = 4257
const shipMissingGasSiphonsError = 4258
const shipSiphonInvalidWaypointError = 4259
const shipSiphonPermissionError = 4260
const waypointNoYieldError = 4261
const shipJumpDestinationUnderConstructionError = 4262
```

## Contract Error Codes

```js
const acceptContractNotAuthorizedError = 4500
const acceptContractConflictError = 4501
const fulfillContractDeliveryError = 4502
const contractDeadlineError = 4503
const contractFulfilledError = 4504
const contractNotAcceptedError = 4505
const contractNotAuthorizedError = 4506
const shipDeliverTermsError = 4508
const shipDeliverFulfilledError = 4509
const shipDeliverInvalidLocationError = 4510
const existingContractError = 4511
```

## Market Error Codes

```js
const marketTradeInsufficientCreditsError = 4600
const marketTradeNoPurchaseError = 4601
const marketTradeNotSoldError = 4602
const marketNotFoundError = 4603
const marketTradeUnitLimitError = 4604
```

## Faction Error Codes

```js
const waypointNoFactionError = 4700
```

## Construction Error Code

```js
const constructionMaterialNotRequired = 4800
const constructionMaterialFulfilled = 4801
const shipConstructionInvalidLocationError = 4802
```
