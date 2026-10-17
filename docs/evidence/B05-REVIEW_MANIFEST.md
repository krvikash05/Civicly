# Civicly B05 external technical review

Actual repository files, preserving relative structure. B04 accepted baseline8aaf17c; B05 changes uncommitted for human review. Source graph algorithms read-only; no B06 work.

## Reproduce the focused B05 checks

Use Python3.12 and pinned backend/pyproject.toml + uv.lock. Configure ignored local.env with supplied setup helper; start pinned Compose without deleting volumes. The full accepted synthetic city bundle is included because its exact manifest is required by the actual-city test; it contains no evaluator answers.

If the retained B04 graph does not exist on a new review machine, bootstrap it safely through the included B04 importer:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion import --graph civicly_b04_test_a84beda80da64aacbc367a9399e07a97 --bundle data/ingestion/city-v3.json --report /tmp/civicly-review-b04-import.json
backend/.venv/bin/python -m pytest backend/tests/unit/test_graph_algorithm_models.py backend/tests/integration/test_graph_algorithms.py -v -s
```

Existing equal city data is a no-op; changed data conflicts, never overwrite/reset it. Full B01–B05 regression and both SPEC commands require the full repository, not this focused test subset; exact commands/results are in B05-COMMANDS.md and B05-regression-tests.txt. No live MCP/LLM/GraphRAG/API/frontend is implemented/tested by this milestone.

## Dependencies not included

- Python interpreter, virtual environment, installed wheels/SDK runtime, Docker engine/image and database/Browser volume contents. Pins and Compose definition included.
- Local.env, credentials, API/private keys, caches and Git internals. Local baseline commit hash is a reference, not bundled history.
- Prior B01–B04 full test sources, legacy fixtures, specification validators and unrelated blueprint contracts; use full accepted repository for complete regression/SPEC reproduction. Required B05 test helpers are included.
- Original synthetic generator/legacy source and18 municipal Markdown document bodies/GeoJSON (none supplied). Canonical bundle, input hashes and sanitized readiness are included; B05 does not retrieve document bodies. Accepted full repository preserves original payloads.
- Hidden evaluator truth, scenario catalog expected answers and delayed reveal payloads; deliberately not runtime/review algorithm inputs. B19 runtime isolation remains pending.

## Included file purpose and exact SHA256

| File | Purpose | SHA256 |
|---|---|---|
| `.env.example` | Pinned setup, dependency or review reproduction source | `213426a08ef14d53cf25d7c23a148242a4b1779498a56b335c415887129dba80` |
| `.python-version` | Pinned setup, dependency or review reproduction source | `7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d` |
| `AGENTS.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `a77604a28c3fff3be6fbb0ad6f35f154a24395b665ced2721ac7a1a44aafc929` |
| `Makefile` | Pinned setup, dependency or review reproduction source | `86bdd8a5dae21c489b4e24494429224cd0f935be034131d857af379187b0e142` |
| `README.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `67ea37756341d8185f7a23d82e2ef844e866e8ecfdaeb6e8e35b7ae0328fd6b1` |
| `backend/ALGORITHMS.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `e018d2237b49faff724385521279bda2bf2f5b496d47afa8f77fce3b615a1252` |
| `backend/GRAPH_ACCESS.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `a400e48eace94543958ad716d87ff596a9615634d13645ac851a080e37090200` |
| `backend/INGESTION.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `2840358d95fb80d9e9d24436b73bbdd8cf24a83d62bc6175a19bf4362159e862` |
| `backend/README.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `0294be9af1a8c63900e462b129edcc84b7d65cc794cff099e8f338d59764bf9d` |
| `backend/SCHEMA.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `38c0749167acdd29c964c87950c2c2ce3de2a7cd196f67e47b1c19c32333c4b5` |
| `backend/app/__init__.py` | Accepted connection/configuration/health/schema CLI dependency | `2eacaf897b16caa056fe6e2526b4d3f35c71cd0917717ef1120484d86a6a382f` |
| `backend/app/config.py` | Accepted connection/configuration/health/schema CLI dependency | `bd9683498ef5620201f4ad68fb5baf9d3bf1db2dbcde9b02ba3257ab49b40ba5` |
| `backend/app/graph/__init__.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `8bd50bfa109a326b56259f83e861102359ce1d819f1be48b93d94aa4d259488e` |
| `backend/app/graph/analysis/__init__.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `d932f3789cbee3c9c46bbd42056b1f2e1c6c4565264026e449eae3bd2bbe9276` |
| `backend/app/graph/analysis/__main__.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `f2308212202158639c79ae6563d6fc810430f0656eee4de30978dea4d4e4ce09` |
| `backend/app/graph/analysis/cases.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `f9e2b2cc441cf93159fc86cdf1ee82e2972e8fe40594119e9f9458fb74268b97` |
| `backend/app/graph/analysis/counterfactual.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `efb4838e21e54422d73be4c981ccec236e93d287f033e9eb2c3da87b2da66ca8` |
| `backend/app/graph/analysis/engine.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `62f8c21ac7e753354caa13b1c25147b7cabb203f600182b3050b620f52bcce30` |
| `backend/app/graph/analysis/evaluation.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `ff79ff09920b5bd4b9ef611075f107381f864b9783d85b23c689d60b9a724d56` |
| `backend/app/graph/analysis/models.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `19eff045dc16d28cad860af568b2d94c1cbe9accb0e3f46cd4fb0d0cc0280875` |
| `backend/app/graph/analysis/reader.py` | B05 typed algorithm/read/counterfactual/evaluation implementation | `43bc3597f4e7c0e394861485e0442909c95891687bfe1e093a23b7099d96f4ad` |
| `backend/app/graph/connection.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `97ac5639b88a6a0040c7ddc0e667aed5c6306b158cccb19f2e8b82e9f4783bb2` |
| `backend/app/graph/migration.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `952243802e9caf9283eb5d85867b8e8612e4f6b9ad7e72dcc9c0fe1440b454b4` |
| `backend/app/graph/migrations/0001.json` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `94ab9fae6079fe7e87b41afd80701409db6bb51d529c2565dbd340896a5c923b` |
| `backend/app/graph/models.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `f7fc061b19b53a16f90f5ccab2a597811cf3b566a7c4fc5c992d079380c4f519` |
| `backend/app/graph/queries.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `e41d7b08a1b06445f790cf342ca882c317016f02057b71404efaa699615c0cd3` |
| `backend/app/graph/repository.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `200da76851fd3edd562102bcc7e681cb3ef97a8734856763d264bd3cbfd43547` |
| `backend/app/graph/schema.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `cf17f8acfe8c40c2968ad9907a256340f25b10f9aa22dbf5eb660f68140977b1` |
| `backend/app/graph/targets.py` | Accepted B02/B03 registry, migration, read/write and integrity dependency | `80b32d13888c925a29462d5fd58bd31f00f07ebf56ee67a163e51ff8394dff08` |
| `backend/app/ingestion/__init__.py` | Accepted B04 strict validation/import/JSON artifact dependency | `f7f38c673e0197e63ade762ce4f643855a2254a4788fde82fe3bf98000937e33` |
| `backend/app/ingestion/__main__.py` | Accepted B04 strict validation/import/JSON artifact dependency | `c9bb5fdf3196ce58fc24889abb500fb75387064817383dc10d7446797d208c72` |
| `backend/app/ingestion/conversion.py` | Accepted B04 strict validation/import/JSON artifact dependency | `96ac40a3b7d2020726fdc0edee4bef4fbf974706d397bafcb125f089d3283a59` |
| `backend/app/ingestion/importer.py` | Accepted B04 strict validation/import/JSON artifact dependency | `fcf878024834b02efc58a07eaac1d5e360d7c9ef9a21e6f8b99383287a8f4235` |
| `backend/app/services/__init__.py` | Accepted connection/configuration/health/schema CLI dependency | `f008bed287f805b37c0867fca8e85bee20cebadd004919c2f59fb0d70f71a9aa` |
| `backend/app/services/health.py` | Accepted connection/configuration/health/schema CLI dependency | `81a0ff7af70afca1261db9b99e962fde0509bd49caa7bcbbedf1d53ff64a92f0` |
| `backend/app/services/schema.py` | Accepted connection/configuration/health/schema CLI dependency | `4d58f988bb07e97b3a0fb416b0e77bcdf5903fe3207af5839cba6023788a2c41` |
| `backend/cli/__init__.py` | Accepted connection/configuration/health/schema CLI dependency | `3ea85b6fd80d8b5cf810cdc3349441a6e0d769c9abad8ef7f4f27b4ae30aa522` |
| `backend/cli/__main__.py` | Accepted connection/configuration/health/schema CLI dependency | `0bcec0bfe33df1b723e39503fbdc3b71e17ac43be60f40328124fd4928bf977c` |
| `backend/cli/main.py` | Accepted connection/configuration/health/schema CLI dependency | `808d2e32c05642e89982bf588a5e84c1be345ba82786cc57e0c21981b2984325` |
| `backend/pyproject.toml` | Pinned setup, dependency or review reproduction source | `d566b1e2a17fab4eac16d9f59f64a4e291967bded9c5fcec8b09902eedd38e9a` |
| `backend/tests/__init__.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `21c8ffe17336d5d046de8231f6ccf418afdc8e8c10535481e062fe392a19c409` |
| `backend/tests/b05_benchmark.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `5d7a193ccc9f05dc3dc2e4493d421ca27f1847c8834ac1f44b5843b199645947` |
| `backend/tests/b05_fixtures.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `01ce5e9de1827a916c645d9695ab543c2aa9a30aea6a258b0ae632e42c1deeac` |
| `backend/tests/conftest.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `fdfbb3238c314b7c0e22c7cf4e4ef03092da909b9470ff9aa196bf848781109d` |
| `backend/tests/integration/conftest.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `94dd6c5d904e7611adf2b85699dc68032654bea94dc83634c3536c67d2c08d52` |
| `backend/tests/integration/test_graph_algorithms.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `a382c11a6fde3f7e890c220fa9920245213c6c666a67f7a08a790057864101b6` |
| `backend/tests/schema_examples.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `e241e8e5d0b5d66c9d10cd00d697be8ca7d9f629deb0313b05354d5d825165b0` |
| `backend/tests/unit/test_graph_algorithm_models.py` | B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper | `f2029e7dc1d2975af1274a2f1c8c1c5447aabd90b2098ab8cf53d9460e11b52d` |
| `backend/uv.lock` | Pinned setup, dependency or review reproduction source | `cea10431c1826cac7503f9fe1037a763afbc8c9f6462a5e886889ca674312196` |
| `blockers.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `e21a03e79af5a7f5fbf79b952350a4f9bfd770a0e23183c4d6cefb31fc74e1fe` |
| `compose.yaml` | Pinned setup, dependency or review reproduction source | `79d2849e7fd79f5515bdce4a85a66c3e51a830f263f8c58a4486d949809de458` |
| `contracts/dataset_ingestion.json` | Normative schema, relationship, ingestion or B05 result/budget contract | `78f615c612d06d82cb4adb1cbf278a209ed7ac126010302b59aaa6cef3cbc3a7` |
| `contracts/graph_access.json` | Normative schema, relationship, ingestion or B05 result/budget contract | `11b4cc8a5d3a0516a842e1ae42c1aabefb7d6130745c16f496b2819cd34348f4` |
| `contracts/graph_algorithms.json` | Normative schema, relationship, ingestion or B05 result/budget contract | `3ab40998181da0b665db136ea9217f4fcf1cdfec1dcbb057ae9244a22739b833` |
| `contracts/schema_registry.json` | Normative schema, relationship, ingestion or B05 result/budget contract | `12541990b58d65e8602bff77b93b735009616e7ee658b9e7582a7ae9f449aac6` |
| `data/ingestion/DATA_QUALITY.md` | Accepted synthetic runtime dataset/manifest or sanitized source-quality inventory | `4c2ebed440ac16626b0b7178d259c3680e997442979358e27a1d8a86f8b4a1d9` |
| `data/ingestion/city-v3.json` | Accepted synthetic runtime dataset/manifest or sanitized source-quality inventory | `6a5f39ab91d7da74a2857203c53c3d5e5ddc8e6a17b691f886c6846a5d97bc0d` |
| `data/ingestion/input-manifest.json` | Accepted synthetic runtime dataset/manifest or sanitized source-quality inventory | `6710f31d7e4ac3ae7f1c430118f4f2928a2709aded2e2e67f150bfa6e560d44a` |
| `data/ingestion/scenario-readiness.json` | Accepted synthetic runtime dataset/manifest or sanitized source-quality inventory | `44f33ca81aa4399ab314a12407e56832cd5ab16c4ed33fe3556929004a2e91df` |
| `data/review/B05-city-extract.json` | Accepted synthetic runtime dataset/manifest or sanitized source-quality inventory | `50213fc18ff159b5c5909f5e856c3e768625cb67db2d7d911d33373b660e3595` |
| `decision.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `4900d4da580e5ea5d7ee3c716360b6040026d72386704ab7eba519eaa0a58b5b` |
| `docs/backend/00_requirements.md` | Normative requirements/architecture/task/vendor-reference documentation | `a0317d6c26c871a1bf728f0936e34776549792dbf15457a3405a0543a33a591a` |
| `docs/backend/01_system.md` | Normative requirements/architecture/task/vendor-reference documentation | `4e2d28a216be5551cf28d03ce858bace2eac9cb56f12ac7b7c9a212b7bea701b` |
| `docs/backend/02_graph.md` | Normative requirements/architecture/task/vendor-reference documentation | `a282d838ada5c8d2ebd50ecc8cf61b10bb393436a694ed5b3e088a86eb2db9de` |
| `docs/backend/03_data.md` | Normative requirements/architecture/task/vendor-reference documentation | `acd8116134217f5cf4d1e04ab8e8f0eae3a750dcb9804011179732ea7ceeeadf` |
| `docs/backend/11_microtasks.md` | Normative requirements/architecture/task/vendor-reference documentation | `0976f308bd8be91b953ed480a49059fb1b7203dcce9541f0a57ba924c654679f` |
| `docs/backend/12_falkordb_sources.md` | Normative requirements/architecture/task/vendor-reference documentation | `018a9d14092f78d9e77ebc4bcabb27d992718e092fb473bf2b777b22479da288` |
| `docs/evidence/B05-COMMANDS.md` | Actual B05 commands, outputs, measurements, source audit or changes | `7908744b6f2f5586d9ab7cf2d55c5e7fbb74c3392850fd6e451cf38e3e9a7dd9` |
| `docs/evidence/B05-FILES.md` | Actual B05 commands, outputs, measurements, source audit or changes | `ba47b10a7d9a00f5fdadff6bf37e599eb0e3e7ae185632fa080a5f151e37cda8` |
| `docs/evidence/B05-RESULTS.md` | Actual B05 commands, outputs, measurements, source audit or changes | `605ce5bd796c3e0e011b102f106840631d0d75e2e34cab9776908286f243056b` |
| `docs/evidence/B05-baseline-spec.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `8fa124535ca85725f1795f48fcccc77d931713036b42bebf221b3e7d5de1f3c1` |
| `docs/evidence/B05-baseline-tests.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `04d4dcbe811840093e4c54660e6c5a725b7831541a7dc0b96e96824f556cb906` |
| `docs/evidence/B05-baseline.json` | Actual B05 commands, outputs, measurements, source audit or changes | `c08cf44d4ea8991d7e336f8288d8efccbfc9fcb1a138d2d7cf3948ebee7cfe1c` |
| `docs/evidence/B05-canonical-status.json` | Actual B05 commands, outputs, measurements, source audit or changes | `115b08ffc7932a29ee331ef7dd7d8d6b25fd6274935c704603da9a86395dc560` |
| `docs/evidence/B05-changes.patch` | Actual B05 commands, outputs, measurements, source audit or changes | `8d851aee1b5cb7c217774ae661a434717e732193f757af57d63c6829b3d92535` |
| `docs/evidence/B05-city-before-positive-proof-fix.json` | Actual B05 commands, outputs, measurements, source audit or changes | `e4bb67995c534449cb1a4f61a0de5264013ae52a00727ec5e26da8ca7bc1ba12` |
| `docs/evidence/B05-city-evaluation.json` | Actual B05 commands, outputs, measurements, source audit or changes | `62fa1db518719de50e6abd4db464d285e3a680c7541ca440fff8b15c68837115` |
| `docs/evidence/B05-controlled-results.json` | Actual B05 commands, outputs, measurements, source audit or changes | `1e786c7d26cb35a243bf140d6f23a5bd03c2a159a3accbe1fe04fad6c2de3f71` |
| `docs/evidence/B05-final-boundary-tests.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `628fb924cf76c37dcdb95b77903d4228c9e447546bdc144cb96ac761386f674c` |
| `docs/evidence/B05-frontend-example.json` | Actual B05 commands, outputs, measurements, source audit or changes | `44bd78ced5c2100cd42a0cb1b1ffeab1e20521b2550ceee7d9f17b7e7774d51f` |
| `docs/evidence/B05-health.json` | Actual B05 commands, outputs, measurements, source audit or changes | `9588e6106774a584e0e0741a8d2b9c857e3de6e54465a7a6ac3aa44570d7a9aa` |
| `docs/evidence/B05-integration-final.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `71b6f9f3a4e7a534dc443fbefc6c32ab549688d1b23d83bd83abce48c6027ae1` |
| `docs/evidence/B05-integration-first.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `7103e028d9bd6974f02aa1b3be0675eb8797118589f18eec1140d0ca35ad9c15` |
| `docs/evidence/B05-integration-second.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `59e5295cefe38afa1edcb7c577703e7d9970a91bf9dc4f3f31beb712fa8d5d35` |
| `docs/evidence/B05-integration-strengthened.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `7ad97916aff04f859c361f2ce7343f735fce5502fe79e74b6350ed2bca2cc135` |
| `docs/evidence/B05-package-focused-tests.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `e739e67aebfa3729ee4c83cdc92c436a66db2c9ff1875e7e9ed6523a3c264bd0` |
| `docs/evidence/B05-performance-before-positive-proof-fix.json` | Actual B05 commands, outputs, measurements, source audit or changes | `27c6ad354a6bbbe3b9d76b7416f81f368693efac6f16551729d5fa2395af13b0` |
| `docs/evidence/B05-performance.json` | Actual B05 commands, outputs, measurements, source audit or changes | `b2c0f7f627ff2651c7be448ff5cc07ed7579884dbe023a2c4019dcd7e1e1f336` |
| `docs/evidence/B05-positive-proof-tests.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `b23b48a1f96f7ae950e04a3f3ced1e15a1cd0baf02a8f873f7d2107690aa6154` |
| `docs/evidence/B05-post-lifecycle.json` | Actual B05 commands, outputs, measurements, source audit or changes | `d76ad724944715da49b0f01e380451975c3eda989be1e00417f9e3aa85fcfd7a` |
| `docs/evidence/B05-regression-before-positive-proof-fix.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `b254879366105dc25bd2a726cfb35a6f866b4317ca83432db18a0111508bc229` |
| `docs/evidence/B05-regression-collection-error.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `6e4e0062dc9a419fc7b1edc0f8747b93de49c715fb2d0e76401c5b5e3be2ca48` |
| `docs/evidence/B05-regression-tests.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `559b93bc12a7d6ad4cd003602ffad13532c1f61d29c7af96ef292df323f395cf` |
| `docs/evidence/B05-scenario-dependencies.json` | Actual B05 commands, outputs, measurements, source audit or changes | `8d1f23f62afad628f986627692bdeb51d0bc41a7dea8efde15bc601b4c6dd959` |
| `docs/evidence/B05-source-audit.json` | Actual B05 commands, outputs, measurements, source audit or changes | `bac48c58900fc1725b16d62595e7793fc98f8e6ea1746d0a338fd642bd2cd01e` |
| `docs/evidence/B05-spec-validation.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `8fa124535ca85725f1795f48fcccc77d931713036b42bebf221b3e7d5de1f3c1` |
| `docs/evidence/B05-unit-tests.txt` | Actual B05 commands, outputs, measurements, source audit or changes | `986874ab94a3e4092d8e5bbef484c13c756424fbd1c9fbcb5a8aae17367426bc` |
| `flow.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `e3606260f4d2a511085db1a2876db139929aba5219651579af2a6a287b2a1df3` |
| `implementation_status.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `cb14dc10b3b3cf3cc7ff5d421043e076c8e45be94047642ec9e72a6587d2b670` |
| `scripts/configure_local.py` | Pinned setup, dependency or review reproduction source | `46660a8f917c773b654ab6989f15527315ef222874a828f167482587eecd5a6c` |
| `scripts/package_b05_review.py` | Pinned setup, dependency or review reproduction source | `55ca837ffb2042089da10d01208afcc7393eba2a0566cd5c7e0432123052d1fa` |
| `task_board.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `e5e3fe6119fd7dafae2e6a1ba02b54587b55d357775809918a46342fd425be06` |
| `test_log.md` | Engineering guide or append-only decision/flow/status/test/blocker history | `823d51434cd5b92927eb372f2bee843eeb5082b66f9705fd52a4d27de92286e1` |

REVIEW_MANIFEST.md is generated metadata; every other entry is byte-identical repository source/evidence.
