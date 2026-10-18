# B13 audit attempt

Initial final audit stopped because a broad recursive private-field scan treated an archived B05 synthetic idempotency_key as a credential. Location `.runtime/b10o-baseline/docs/evidence/B05-controlled-results.json` is a historical public-evidence snapshot, not a credential file. No value printed. Corrected scope to actual root private runtime profiles plus explicit `.runtime/auth/credentials.json` values, retaining all new operator password checks and private-key patterns. No source/test/database change or provider call. Final audit recorded separately.
