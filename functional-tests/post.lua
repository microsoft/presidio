wrk.method = "POST"
wrk.body   = '{"text":"my credit card number is 2970-84746760-9907 345954225667833 4961-2765-5327-5913", "analyzeTemplate":{"fields":[{"name":"CREDIT_CARD"}]}  }'
wrk.headers["Content-Type"] = "application/json"